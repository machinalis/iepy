from django.contrib import admin
from django.core import urlresolvers
from django.db.models import Q

from relatedwidget import RelatedWidgetWrapperBase

from corpus.models import (
    IEDocument, IEDocumentMetadata, Entity, EntityKind, Relation,
    EntityOccurrence, GazetteItem
)

admin.site.site_header = 'IEPY administration'
admin.site.site_title = 'IEPY'
admin.site.index_title = 'IEPY'


@admin.register(EntityKind)
class EntityKindAdmin(admin.ModelAdmin):
    pass


@admin.register(EntityOccurrence)
class EntityOccurrenceAdmin(admin.ModelAdmin):
    pass


@admin.register(Entity)
class EntityAdmin(admin.ModelAdmin):
    list_per_page = 20


@admin.register(IEDocumentMetadata)
class IEDocumentMetadataAdmin(admin.ModelAdmin):

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(IEDocument)
class IEDocumentAdmin(RelatedWidgetWrapperBase, admin.ModelAdmin):
    change_form_template = 'relatives/change_form.html'
    list_display = ['id', 'human_identifier', 'link_to_document_navigation']
    search_fields = ['text']
    fieldsets = [
        (None, {'fields': ['human_identifier', 'text', 'metadata']}),
        ('Preprocess output',
         {'classes': ['collapse'],
          'fields': ['tokens', 'offsets_to_text', 'tokenization_done_at',
                     'sentences', 'sentencer_done_at',
                     'lemmas', 'lemmatization_done_at',
                     'postags', 'tagging_done_at',
                     'ner_done_at', 'segmentation_done_at', 'syntactic_parsing_done_at'],
          })]

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        metadata_field = form.base_fields['metadata']
        if obj is None:
            metadata_field.queryset = metadata_field.queryset.filter(
                document__isnull=True)
            # let's make this field not required during creating.
            # This means that on save_model we'll create an empty metadata obj if needed
            metadata_field.required = False
        else:
            metadata_field.queryset = metadata_field.queryset.filter(
                Q(document__id=obj.id) | Q(document__isnull=True))
        return form

    def save_model(self, request, obj, form, change):
        if obj.id is None and not change:  # ie, creation
            try:
                obj.metadata
            except IEDocumentMetadata.DoesNotExist:
                obj.metadata = IEDocumentMetadata.objects.create()

        return super().save_model(request, obj, form, change)

    def link_to_document_navigation(self, obj):
        return '<a href="{0}">Rich View</a>'.format(
            urlresolvers.reverse('corpus:navigate_document', args=(obj.id,))
        )
    link_to_document_navigation.short_description = 'Rich View'
    link_to_document_navigation.allow_tags = True
    list_per_page = 20


@admin.register(Relation)
class RelationAdmin(admin.ModelAdmin):
    list_display = ('name', 'left_entity_kind', 'right_entity_kind', 'link_to_label')

    def link_to_label(self, obj):
        return '<a href="{0}">Label evidence</a>'.format(
            urlresolvers.reverse('corpus:next_document_to_label', args=(obj.id,))
        )
    link_to_label.short_description = 'Labeling'
    link_to_label.allow_tags = True

    def get_readonly_fields(self, request, obj=None):
        if obj:  # editing an existing object
            return self.readonly_fields + ('left_entity_kind', 'right_entity_kind')
        return self.readonly_fields


@admin.register(GazetteItem)
class GazetteAdmin(admin.ModelAdmin):
    search_fields = ['text']
    list_display = ('text', 'kind', 'from_freebase',)
    list_filter = ('kind', 'from_freebase',)
    readonly_fields = ('from_freebase', )
