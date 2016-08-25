import subprocess
import xmltodict
import os
import sys
import logging
import stat
from functools import lru_cache

import iepy
from iepy.utils import DIRS, unzip_from_url


logger = logging.getLogger(__name__)


def detect_java_version():
    java_cmd = os.getenv('JAVAHOME')
    if not java_cmd:
        print('Environment variable JAVAHOME not defined.')
        sys.exit(-1)

    here = os.path.dirname(os.path.realpath(__file__))
    jar = os.path.join(here, 'utils', 'get-java-version.jar')
    jversion = subprocess.check_output([java_cmd, "-jar", jar], stderr=subprocess.PIPE)
    return int(jversion.strip())


JAVA_VERSION = detect_java_version()


_STANFORD_BASE_URL = "http://nlp.stanford.edu/software/"
if JAVA_VERSION < 8:
    # Stanford Core NLP 3.4.1 - Last version to support Java 6 and Java 7
    # Pitifully Stanford folks have a public name ("version") of their releases that isn't
    # used on their download urls. So, 3.4.1 is "stanford-corenlp-full-2014-08-27"
    _CORENLP_VERSION = "stanford-corenlp-full-2014-08-27"
    DOWNLOAD_URL = _STANFORD_BASE_URL + _CORENLP_VERSION + ".zip"
    DOWNLOAD_URL_ES = _STANFORD_BASE_URL + 'stanford-spanish-corenlp-2014-08-26-models.jar'
    DOWNLOAD_URL_DE = _STANFORD_BASE_URL + 'stanford-german-2016-01-19-models.jar'
    _FOLDER_PATH = os.path.join(DIRS.user_data_dir, _CORENLP_VERSION)
    COMMAND_PATH = os.path.join(_FOLDER_PATH, "corenlp.sh")
else:
    # Stanford Core NLP 3.5.2
    _CORENLP_VERSION = "stanford-corenlp-full-2015-04-20"
    DOWNLOAD_URL_ES = _STANFORD_BASE_URL + 'stanford-spanish-corenlp-2015-01-08-models.jar'
    DOWNLOAD_URL_DE = _STANFORD_BASE_URL + 'stanford-german-2016-01-19-models.jar'

DOWNLOAD_URL = _STANFORD_BASE_URL + _CORENLP_VERSION + ".zip"
_FOLDER_PATH = os.path.join(DIRS.user_data_dir, _CORENLP_VERSION)
COMMAND_PATH = os.path.join(_FOLDER_PATH, "corenlp.sh")


@lru_cache(maxsize=1)
def get_analizer(*args, **kwargs):
    logger.info("Loading StanfordCoreNLP...")
    return StanfordCoreNLP(*args, **kwargs)


class StanfordCoreNLP:
    CMD_ARGS = "-outputFormat xml -threads 4"
    PROMPT = b"\nNLP> "

    def __init__(self, tokenize_with_whitespace=False, gazettes_filepath=None):
        cmd_args = self.command_args(tokenize_with_whitespace, gazettes_filepath)
        os.chdir(_FOLDER_PATH)
        self.corenlp_cmd = [COMMAND_PATH] + cmd_args
        self._start_proc()

    def _start_proc(self):
        self.proc = subprocess.Popen(
            self.corenlp_cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            cwd=_FOLDER_PATH
        )
        self.output = self.iter_output_segments()
        self.receive()  # Wait until the prompt is ready

    def command_args(self, tokenize_with_whitespace, gazettes_filepath):
        annotators = ["tokenize", "ssplit", "pos", "lemma", "ner", "parse", "dcoref"]
        cmd_args = self.CMD_ARGS[:]
        if tokenize_with_whitespace:
            cmd_args += " -tokenize.whitespace=true"

        if gazettes_filepath:
            annotators.insert(annotators.index("ner") + 1, "regexner")
            cmd_args += " -regexner.mapping {}".format(gazettes_filepath)

        tkn_opts = self._tokenizer_options()
        if tkn_opts:
            cmd_args += " " + tkn_opts

        lang = iepy.instance.settings.IEPY_LANG
        edu_mods = "edu/stanford/nlp/models"
        if lang == 'es':
            annotators.remove('dcoref')  # not supported for spanish on Stanford 3.4.1
            cmd_args += " -tokenize.language es"
            cmd_args += " -pos.model %s/pos-tagger/spanish/spanish-distsim.tagger" % edu_mods
            cmd_args += " -ner.model %s/ner/spanish.ancora.distsim.s512.crf.ser.gz" % edu_mods
            cmd_args += " -parse.model %s/lexparser/spanishPCFG.ser.gz" % edu_mods
        if lang == 'de':
            annotators.remove('dcoref')  # not supported for german on Stanford 3.4.1
            cmd_args += " -tokenize.language de"
            cmd_args += " -pos.model %s/pos-tagger/german/german-dewac.tagger" % edu_mods
            cmd_args += " -ner.model %s/ner/german.dewac_175m_600.crf.ser.gz" % edu_mods
            cmd_args += " -parse.model %s/lexparser/germanPCFG.ser.gz" % edu_mods

        cmd_args += " -annotators {}".format(",".join(annotators))
        return cmd_args.split()

    def _tokenizer_options(self):
        """As stated in
        http://nlp.stanford.edu/nlp/javadoc/javanlp/edu/stanford/nlp/process/PTBTokenizer.html
        there are several tokenizer options that can be changed.
        We'll only send to command line those that differ from the Stanford default.
        """
        extra_keys = ['ptb3Escaping']
        defaults = {
            'invertible': False,
            'tokenizeNLs': False,
            'americanize': True,
            'normalizeSpace': True,
            'normalizeAmpersandEntity': True,
            'normalizeCurrency': True,
            'normalizeFractions': True,
            'normalizeParentheses': True,
            'normalizeOtherBrackets': True,
            'asciiQuotes': False,
            'latexQuotes': True,
            'unicodeQuotes': False,
            'ptb3Ellipsis': True,
            'unicodeEllipsis': False,
            'ptb3Dashes': True,
            'keepAssimilations': True,
            'escapeForwardSlashAsterisk': True,
            'untokenizable': "firstDelete",
            'strictTreebank3': False
        }
        allowed_keys = set(defaults.keys()).union(extra_keys)
        customizations = getattr(iepy.instance.settings, 'CORENLP_TKN_OPTS', {})
        opts = []
        for k, v in customizations.items():
            if k not in allowed_keys:
                raise ValueError('Invalid key "%s". Valid options are %s' % (k, allowed_keys))
            if k in defaults and defaults[k] == v:
                # valid option, but it's the defaults, so no need to provide it.
                continue
            if isinstance(v, bool):
                v = ("%s" % v).lower()
            opts.append("%s=%s" % (k, v))
        if opts:
            return '-tokenize.options "{}"'.format(','.join(opts))

    def iter_output_segments(self):
        while True:
            buf = b""
            while self.PROMPT not in buf:
                buf += self.proc.stdout.read1(1024)

                if self.proc.poll() == 1:
                    logger.error("Error running '{}'".format(" ".join(self.corenlp_cmd)))
                    logger.error("Output was: '{}'".format(buf))
                    sys.exit(1)

            segment, _, buf = buf.partition(self.PROMPT)
            yield segment.decode("utf8")

    def receive(self):
        return next(self.output)

    def send(self, data):
        data = data.replace("\n", " ") + "\n"
        self.proc.stdin.write(data.encode("utf8"))
        self.proc.stdin.flush()

    def quit(self):
        self.proc.stdin.write("q\n".encode("utf8"))
        self.proc.stdin.flush()

    @lru_cache(maxsize=1)
    def analyse(self, text):
        self.send(text)
        text = self.receive()
        i = text.index("<?xml version")
        text = text[i:]
        return xmltodict.parse(text)["root"]["document"]


def download(lang='en'):
    base = os.path.dirname(COMMAND_PATH)
    if os.path.isfile(COMMAND_PATH):
        print("Stanford CoreNLP is already downloaded at {}.".format(base))
    else:
        print("Downloading Stanford CoreNLP...")
        unzip_from_url(DOWNLOAD_URL, DIRS.user_data_dir)

        # Zip acquired. Make sure right Java is used, and file is executable
        for directory in os.listdir(DIRS.user_data_dir):
            if directory.startswith("stanford-corenlp-full"):
                stanford_directory = os.path.join(DIRS.user_data_dir, directory)
                if os.path.isdir(stanford_directory):
                    runner_path = os.path.join(stanford_directory, "corenlp.sh")
                    st = os.stat(runner_path)
                    _content = open(runner_path).read()
                    _content = _content.replace('java', '$JAVAHOME')
                    with open(runner_path, 'w') as runner_file:
                        runner_file.write(_content)

                    os.chmod(runner_path, st.st_mode | stat.S_IEXEC)
                    break

    # Download extra data for specific language
    download_urls = dict(es=DOWNLOAD_URL_ES, de=DOWNLOAD_URL_DE)
    if lang.lower() in download_urls.keys():
        print("Downloading Stanford CoreNLP extra data for lang '{}'...".format(lang))
        unzip_from_url(download_urls[lang.lower()], _FOLDER_PATH)
    elif lang.lower() != 'en':
        print("There are no extra data to download for lang '{}'.".format(lang))

