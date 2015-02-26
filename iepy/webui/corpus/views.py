import json
from collections import defaultdict

from django.db.models import Q
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404, render_to_response, redirect
from django.utils.decorators import method_decorator
from django.utils import formats
from django.views.generic.base import TemplateView
from django.http import HttpResponse, HttpResponseBadRequest

from extra_views import ModelFormSetView

from corpus.forms import EvidenceForm, EvidenceOnDocumentForm, EvidenceToolboxForm
from corpus.models import (
    Relation, TextSegment, IEDocument,
    EvidenceLabel, SegmentToTag, EntityKind
)

from iepy.data.db import EntityOccurrenceManager


def _judge(request):
    return request.user.username


class Home(TemplateView):
    template_name = 'corpus/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["relations"] = Relation.objects.all()

        segments_to_tag = SegmentToTag.objects.filter(done=False)
        relation_ids_to_tag = list(set(segments_to_tag.values_list("relation", flat=True)))
        relations_to_tag = Relation.objects.filter(id__in=relation_ids_to_tag)
        context["iepy_runs"] = relations_to_tag

        return context
home = login_required(Home.as_view())


def next_segment_to_label(request, relation_id):
    relation = get_object_or_404(Relation, pk=relation_id)
    segment = relation.get_next_segment_to_label(_judge(request))
    if segment is None:
        return render_to_response('message.html',
                                  {'msg': 'There are no more evidence to label'})
    return redirect('corpus:label_evidence_for_segment', relation.pk, segment.pk)


def next_document_to_label(request, relation_id):
    relation = get_object_or_404(Relation, pk=relation_id)
    doc = relation.get_next_document_to_label(_judge(request))
    if doc is None:
        return render_to_response('message.html',
                                  {'msg': 'There are no more evidence to label'})
    return redirect('corpus:label_evidence_for_document', relation.pk, doc.pk)


def _navigate_labeled_items(request, relation_id, current_id, direction, type_, judgeless):
    # The parameter current_id indicates where the user is situated when asking
    # to move back or forth
    type_name = 'document' if type_ == IEDocument else 'segment'
    url_name = 'corpus:label_evidence_for_%s' % type_name
    relation = get_object_or_404(Relation, pk=relation_id)
    current = get_object_or_404(type_, pk=current_id)
    current_id = int(current_id)
    going_back = direction.lower() == 'back'
    judge = _judge(request) if not judgeless else None

    obj_id_to_show = relation.labeled_neighbor(current, judge, going_back)
    if obj_id_to_show is None:
        # Internal logic couldn't decide what other obj to show. Better to
        # forward to the one already shown
        response = redirect(url_name, relation.pk, current_id)
        messages.add_message(request, messages.WARNING,
                             'No other %s to show.' % type_name)
        return response
    else:
        response = redirect(url_name, relation.pk, obj_id_to_show)
        if obj_id_to_show == current_id:
            direction_str = "previous" if going_back else "next"
            messages.add_message(
                request, messages.WARNING,
                'No {0} {1} to show.'.format(direction_str, type_name))
        return response


def navigate_labeled_segments(request, relation_id, segment_id, direction, judgeless=False):
    return _navigate_labeled_items(
        request, relation_id, segment_id, direction, TextSegment, judgeless
    )


def navigate_labeled_documents(request, relation_id, document_id, direction, judgeless=False):
    return _navigate_labeled_items(
        request, relation_id, document_id, direction, IEDocument, judgeless
    )


class _BaseLabelEvidenceView(ModelFormSetView):
    form_class = EvidenceForm
    model = EvidenceLabel
    extra = 0
    max_num = None
    can_order = False
    can_delete = False

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    @property
    def judge(self):
        return _judge(self.request)


class LabelEvidenceOnSegmentBase(_BaseLabelEvidenceView):
    template_name = 'corpus/segment_questions.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        self.segment.hydrate()
        title = "Labeling Evidence for Relation {0}".format(self.relation)
        subtitle = 'For Document "{0}", Text Segment id {1}'.format(
            self.segment.document.human_identifier,
            self.segment.id)

        context.update({
            'title': title,
            'subtitle': subtitle,
            'segment': self.segment,
            'segment_rich_tokens': list(self.segment.get_enriched_tokens()),
            'relation': self.relation,
            'draw_navigation': True,
        })
        return context

    def get_segment_and_relation(self):
        if hasattr(self, 'segment') and hasattr(self, 'relation'):
            return self.segment, self.relation
        self.segment = get_object_or_404(TextSegment, pk=self.kwargs['segment_id'])
        self.segment.hydrate()
        self.relation = get_object_or_404(Relation, pk=self.kwargs['relation_id'])
        evidences = list(self.segment.get_evidences_for_relation(self.relation))
        for ev in evidences:
            ev.get_or_create_label_for_judge(self.relation, self.judge)  # creating EvidenceLabels
        return self.segment, self.relation

    def get_queryset(self):
        segment, relation = self.get_segment_and_relation()
        return super().get_queryset().filter(
            judge=self.judge, evidence_candidate__segment=self.segment,
            relation=self.relation,
            labeled_by_machine=False,
        )

    def get_success_url(self):
        return reverse('corpus:next_segment_to_label', args=[self.relation.pk])

    def formset_valid(self, formset):
        """
        Add message to the user, and set who made this labeling (judge).
        """
        for form in formset:
            if form.has_changed():
                form.instance.judge = str(self.request.user)
        result = super().formset_valid(formset)
        messages.add_message(self.request, messages.INFO,
                             'Changes saved for segment {0}.'.format(self.segment.id))
        return result


class LabelEvidenceOnSegmentView(LabelEvidenceOnSegmentBase):

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)

        for formset in context["formset"]:
            instance = formset.instance
            evidence = instance.evidence_candidate
            instance.all_labels = evidence.labels.all()

        context["draw_navigation"] = True
        context["draw_postags"] = True

        return context


def human_in_the_loop(request, relation_id):
    relation = get_object_or_404(Relation, pk=relation_id)

    segments_to_tag = SegmentToTag.objects.filter(
        relation=relation,
        done=False,
    ).order_by("-modification_date")

    if not segments_to_tag:
        return render_to_response(
            'message.html',
            {'msg': 'There are no more evidence to label'}
        )

    segment_to_tag = segments_to_tag[0]
    return redirect(
        'corpus:human_in_the_loop_segment',
        relation.pk, segment_to_tag.segment.pk
    )


class HumanInTheLoopView(LabelEvidenceOnSegmentBase):

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context["draw_navigation"] = False
        return context

    def get_success_url(self):
        return reverse('corpus:human_in_the_loop', args=[self.relation.pk])

    def formset_valid(self, formset):
        result = super().formset_valid(formset)

        segment = get_object_or_404(TextSegment, pk=self.kwargs["segment_id"])
        segment_to_tag = SegmentToTag.objects.get(
            segment=segment,
            relation=self.relation,
        )
        segment_to_tag.done = True
        segment_to_tag.save()
        return result


class LabelEvidenceOnDocumentView(_BaseLabelEvidenceView):
    template_name = 'corpus/document_questions.html'
    form_class = EvidenceOnDocumentForm

    def get_text_segments(self, only_with_evidences=False):
        if only_with_evidences:
            return self.relation._matching_text_segments().filter(
                document_id=self.document.id).order_by('offset').distinct()
        else:
            return self.document.get_text_segments()

    def get_context_data(self, **kwargs):
        ctx = super(LabelEvidenceOnDocumentView, self).get_context_data(**kwargs)
        title = "Labeling Evidence for Relation {0}".format(self.relation)
        subtitle = 'For Document "{0}"'.format(self.document.human_identifier)

        segments_with_rich_tokens = []
        for segment in self.get_text_segments(only_with_evidences=True):
            segment.hydrate()
            segments_with_rich_tokens.append(
                {'id': segment.id,
                 'rich_tokens': list(segment.get_enriched_tokens())}
            )

        if self.document.syntactic_sentences:
            parsed_sentences = [x.pprint() for x in self.document.syntactic_sentences]
        else:
            parsed_sentences = [""] * len(segments_with_rich_tokens)

        if not segments_with_rich_tokens:
            ctx = {
                'title': title,
                'document': self.document,
                'relation': self.relation,
                'eos_propperties': {},
                'relations_list': [],
                'forms_values': [],
                'draw_navigation': True,
                'entity_kinds': EntityKind.objects.all(),
            }
            return ctx


        other_judges_labels = defaultdict(list)
        for formset in ctx["formset"]:
            instance = formset.instance
            evidence = instance.evidence_candidate
            for label in evidence.labels.filter(
                Q(relation=instance.relation) & ~Q(id=instance.id)
            ):
                other_judges_labels[label.judge].append([
                    evidence.left_entity_occurrence.id,
                    evidence.right_entity_occurrence.id,
                    label.label
                ])

        forms_values = {}
        eos_propperties = {}
        relations_list = []
        formset = ctx['formset']
        for form_idx, form in enumerate(formset):
            lbl_evidence = form.instance
            evidence = lbl_evidence.evidence_candidate

            left_eo_id = evidence.left_entity_occurrence.pk
            right_eo_id = evidence.right_entity_occurrence.pk
            info = "Labeled as {} by {} on {}".format(
                lbl_evidence.label,
                lbl_evidence.judge if lbl_evidence.judge else "unknown",
                formats.date_format(
                    lbl_evidence.modification_date, "SHORT_DATETIME_FORMAT"
                )
            )
            relations_list.append({
                "relation": [left_eo_id, right_eo_id],
                "form_id": form.prefix,
                "info": info,
            })

            forms_values[form.prefix] = lbl_evidence.label

            for eo_id in [left_eo_id, right_eo_id]:
                if eo_id not in eos_propperties:
                    eos_propperties[eo_id] = {
                        'selectable': True,
                        'selected': False,
                    }

        form_toolbox = EvidenceToolboxForm(prefix='toolbox')
        question_options = [x[0] for x in form_toolbox.fields["label"].choices]
        form_for_others = EvidenceForm(
            prefix='for_others', initial={"label": EvidenceLabel.NORELATION}
        )
        different_kind = self.relation.left_entity_kind != self.relation.right_entity_kind

        ctx.update({
            'title': title,
            'subtitle': subtitle,
            'document': self.document,
            'segments': segments_with_rich_tokens,
            'parsed_sentences': parsed_sentences,
            'relation': self.relation,
            'form_for_others': form_for_others,
            'form_toolbox': form_toolbox,
            'initial_tool': EvidenceLabel.YESRELATION,
            'eos_propperties': json.dumps(eos_propperties),
            'relations_list': json.dumps(relations_list),
            'forms_values': json.dumps(forms_values),
            'question_options': question_options,
            'other_judges_labels': json.dumps(other_judges_labels),
            'other_judges': list(other_judges_labels.keys()),
            "draw_navigation": True,
            'entity_kinds': EntityKind.objects.all(),
            'different_kind': different_kind,
        })
        return ctx

    def get_document_and_relation(self):
        if hasattr(self, 'document') and hasattr(self, 'relation'):
            return self.document, self.relation
        self.document = get_object_or_404(IEDocument, pk=self.kwargs['document_id'])
        self.relation = get_object_or_404(Relation, pk=self.kwargs['relation_id'])
        evidences = []
        for segment in self.document.get_text_segments():
            evidences.extend(
                list(segment.get_evidences_for_relation(self.relation))
            )
        for ev in evidences:
            ev.get_or_create_label_for_judge(self.relation, self.judge)  # creating EvidenceLabels

        return self.document, self.relation

    def get_queryset(self):
        document, relation = self.get_document_and_relation()
        return super().get_queryset().filter(
            judge=self.judge, evidence_candidate__segment__document_id=document,
            relation=relation,
            labeled_by_machine=False,
        )

    def get_success_url(self):
        if self.is_partial_save():
            return self.request.META.get('HTTP_REFERER')
        return reverse('corpus:next_document_to_label', args=[self.relation.pk])

    def get_default_label_value(self):
        return self.request.POST.get('for_others-label', None)

    def is_partial_save(self):
        # "partial saves" is a hack to allow edition of the Preprocess while labeling
        return self.request.POST.get('partial_save', '') == 'enabled'

    def formset_valid(self, formset):
        """
        Add message to the user, handle the "for the rest" case, and set
        who made this labeling (judge).
        """
        partial = self.is_partial_save()
        if partial:
            default_lbl = None
        else:
            default_lbl = self.get_default_label_value()
        for form in formset:
            if form.instance.label is None:
                form.instance.label = default_lbl
            if form.has_changed():
                form.instance.judge = str(self.request.user)
        result = super().formset_valid(formset)
        if not partial:
            messages.add_message(
                self.request, messages.INFO,
                'Changes saved for document {0}.'.format(self.document.id)
            )
        return result

    def get_formset_kwargs(self):
        """
        If is a partial save, hacks the forms to match the queryset so it
        matches the ones that actually has a CandidateEvidence.
        This is to handle the case where an entity occurrence was removed.
        """

        kwargs = super().get_formset_kwargs()
        queryset = kwargs.get("queryset", [])
        data = kwargs.get("data", {})
        partial = data.get("partial_save")

        if partial != "enabled":
            return kwargs

        new_data = data.copy()

        initial_forms_key = "form-INITIAL_FORMS"
        total_forms_key = "form-TOTAL_FORMS"
        query_ids = [str(x.id) for x in queryset]
        included_forms = []
        for key, value in data.items():
            if key.endswith("-id"):
                form_id = key[:-3]
                label_key = "{}-label".format(form_id)

                if value in query_ids:
                    label = data[label_key]
                    included_forms.append((value, label))

                new_data.pop(key)
                new_data.pop(label_key)

        for i, (form_id, label) in enumerate(included_forms):
            form_id_key = "form-{}-id".format(i)
            form_label_key = "form-{}-label".format(i)
            new_data[form_id_key] = form_id
            new_data[form_label_key] = label

        new_data[total_forms_key] = str(len(included_forms))
        new_data[initial_forms_key] = str(len(included_forms))

        kwargs["data"] = new_data
        return kwargs


def navigate_documents(request, document_id, direction):
    if direction == "back":
        documents = IEDocument.objects.filter(id__lt=document_id).order_by("-id")
    else:
        documents = IEDocument.objects.filter(id__gt=document_id).order_by("id")

    if documents:
        document_id = documents[0].id
    else:
        messages.add_message(
            request, messages.WARNING,
            'No more documents to show'
        )

    return redirect('corpus:navigate_document', document_id)


class DocumentNavigation(TemplateView):
    template_name = 'corpus/document.html'

    def get_context_data(self, document_id, **kwargs):
        context = super().get_context_data(**kwargs)
        document = get_object_or_404(IEDocument, pk=self.kwargs['document_id'])
        sentences = [{"rich_tokens": x, "id": i} for i, x in enumerate(document.get_sentences(enriched=True))]
        if document.syntactic_sentences:
            parsed_sentences = [x.pprint() for x in document.syntactic_sentences]
        else:
            parsed_sentences = [""] * len(sentences)

        context["entity_kinds"] = EntityKind.objects.all()
        context["document"] = document
        context["segments"] = sentences
        context["parsed_sentences"] = parsed_sentences
        context["draw_navigation"] = True
        return context


def create_entity_occurrence(request):
    kind = get_object_or_404(EntityKind, id=request.POST.get("kind"))
    document = get_object_or_404(IEDocument, id=request.POST.get("doc_id"))

    if "offset" not in request.POST or "offset_end" not in request.POST:
        raise HttpResponseBadRequest("Invalid offsets")
    try:
        offset = int(request.POST["offset"])
        offset_end = int(request.POST["offset_end"])
    except ValueError:
        raise HttpResponseBadRequest("Invalid offsets")

    EntityOccurrenceManager.create_with_entity(kind, document, offset, offset_end)
    result = json.dumps({"success": True})
    return HttpResponse(result, content_type='application/json')
