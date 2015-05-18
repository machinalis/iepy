from collections import defaultdict
import logging
import os
import string
import sys

from iepy.data.models import EntityOccurrence, EvidenceLabel

logger = logging.getLogger(__name__)


class FileNameSanitizerForDocuments:
    _acceptable_characters = string.ascii_letters + string.digits + '_-'

    def __init__(self, folder_path):
        self.folder = folder_path
        self._used = []

    def sanitizer(self, name):
        new_name = ''.join(c for c in name if c in self._acceptable_characters)
        return new_name

    def file_name_for_doc(self, doc, key='human_identifier'):
        name = self.sanitizer(getattr(doc, key))
        if name in self._used:
            i = 2
            while True:
                _ = "%s_%i" % (name, i)
                if _ not in self._used:
                    name = _
                    break
        self._used.append(name)
        return os.path.join(self.folder, name + '.txt')


def confirm_want_to_proceed(msg):
    """ask for confirmation. Default is yes"""
    prompt = "%s [y]|n: " % msg
    while True:
        ans = input(prompt)
        if not ans:
            return True
        if ans not in ['y', 'Y', 'n', 'N']:
            print ('please enter y or n.')
            continue
        if ans == 'y' or ans == 'Y':
            return True
        if ans == 'n' or ans == 'N':
            return False


def progress(count, total, suffix=''):
    bar_len = 60
    filled_len = int(round(bar_len * count / float(total)))
    percents = round(100.0 * count / float(total), 1)
    bar = '=' * filled_len + '-' * (bar_len - filled_len)
    sys.stdout.write('[%s] %s%s ...%s\r' % (bar, percents, '%', suffix))


class Brat:
    _palette = ['FFE3AA', 'D4EE9F', 'CD88AF', '7887AB',
                'FFBBBB', 'A8E4A8', '94CACA', 'FFDABB',]

    def __init__(self, palette=None, include_judge_name=False):
        if palette is not None:
            self._palette = palette[:]
        self.include_judge_name = include_judge_name

    def color_i(self, i):
        return self._palette[i % len(self._palette)]

    def create_folder(self, folder_path):
        if os.path.exists(folder_path):
            if os.path.isdir(folder_path):
                msg = ('Folder "%s" already exist. Do you want to proceed, and if'
                       ' needed overwrite the folder contents?' % folder_path)
                if not confirm_want_to_proceed(msg):
                    print ('Export aborted')
                    exit(1)
            else:
                print ('The provided output-folder path (%s) already exists and it\'s '
                       'not a directory.\nExport aborted')
                exit(1)
        os.makedirs(folder_path, exist_ok=True)

    def run(self, path, documents, relations):
        self.create_folder(path)
        self.sanitizer = FileNameSanitizerForDocuments(path)
        documents = list(documents)  # making sure works with consumables too
        doc_ids = [d.id for d in documents]
        entities_per_doc = defaultdict(list)
        logger.info('Getting EntityOccurrences for the documents to export')
        eos = EntityOccurrence.objects.filter(document_id__in=doc_ids).select_related(
            'entity', 'entity__kind')
        for eo in eos.order_by('offset'):
            entities_per_doc[eo.document_id].append(eo)

        logger.info('Dumping %s documents' % len(documents))
        self._entity_kinds = set()
        self._relation_kinds = set()
        for i, doc in enumerate(documents):
            self._export_document(doc, entities_per_doc[doc.id], relations)
            progress(i + 1, len(documents), '')
        print ('\r')
        print ('Documents exported')
        self.generate_brat_conf_files(path)

    def generate_brat_conf_files(self, path):
        fname = os.path.join(path, 'annotation.conf')
        kinds = sorted(self._entity_kinds)
        with open(fname, 'w') as conf_file:
            conf_file.write('[entities]\n')
            conf_file.write('\n'.join(kinds))
            conf_file.write('\n[relations]')
            for rname, kind1, kind2 in sorted(self._relation_kinds):
                conf_file.write(
                    '\n%s\tArg1:%s, Arg2:%s' % (rname, kind1, kind2)
                )
            conf_file.write('\n[events]\n[attributes]\n')

        fname = os.path.join(path, 'visual.conf')
        with open(fname, 'w') as conf_file:
            conf_file.write('[labels]\n')
            conf_file.write('[drawing]\n')
            for i, k in enumerate(kinds):
                color = self.color_i(i)
                conf_file.write('%s\tbgColor:#%s\n' % (k, color))

    def _export_document(self, document, eos, relations):
        fname = self.sanitizer.file_name_for_doc(document)
        text = document.text
        with open(fname, 'w') as doc_file:
            doc_file.write(text)
        annotations_fname = "%s.ann" % os.path.splitext(fname)[0]
        E_lines = []
        for eo in eos:
            tkn_start, tkn_end = eo.offset, eo.offset_end
            start = document.offsets_to_text[tkn_start]
            if tkn_end >= len(document.offsets_to_text):
                end = len(document.text)
            else:
                end = document.offsets_to_text[tkn_end]
            text_substring = text[start:end]
            rstriped = text_substring.rstrip()
            if rstriped and text_substring != rstriped:
                end -= len(text_substring) - len(rstriped)
            if eo.alias.replace(' ', '') != rstriped.replace(' ', ''):
                print ('Problem (doc %s) <%s> not equal to <%s>' % (document.id, eo.alias, rstriped))
            line = 'T{i}\t{kind} {start} {end}\t{alias}'.format(
                i=eo.id, kind=eo.entity.kind.name, start=start, end=end,
                alias=rstriped
            )
            E_lines.append(line)
            self._entity_kinds.add(eo.entity.kind.name)

        # adding relations info
        R_lines = []
        template = 'R{i}\t{rname} Arg1:T{eo1} Arg2:T{eo2}'
        yes_labels = EvidenceLabel.objects.filter(
            label=EvidenceLabel.YESRELATION, relation__in=relations,
            evidence_candidate__segment__document_id=document.id
        ).select_related('evidence_candidate', 'relation',
                         'relation__left_entity_kind',
                         'relation__right_entity_kind')
        for yl in yes_labels:
            r = yl.relation
            eo1 = yl.evidence_candidate.left_entity_occurrence
            eo2 = yl.evidence_candidate.right_entity_occurrence
            if self.include_judge_name:
                rname = '%s-%s' % (r.name, yl.judge)
            else:
                rname = r.name
            R_lines.append(
                template.format(i=yl.id, rname=rname, eo1=eo1.id, eo2=eo2.id)
            )
            self._relation_kinds.add((rname, r.left_entity_kind.name,
                                      r.right_entity_kind.name))

        with open(annotations_fname, 'w') as ann_file:
            ann_file.write('\n'.join(E_lines))
            ann_file.write('\n')
            ann_file.write('\n'.join(R_lines))

