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
    jversion = subprocess.check_output([java_cmd, "-jar", jar], stderr=subprocess.STDOUT)
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
    _FOLDER_PATH = os.path.join(DIRS.user_data_dir, _CORENLP_VERSION)
    COMMAND_PATH = os.path.join(_FOLDER_PATH, "corenlp.sh")
else:
    # Stanford Core NLP 3.5.2
    _CORENLP_VERSION = "stanford-corenlp-full-2015-04-20"
    DOWNLOAD_URL_ES = _STANFORD_BASE_URL + 'stanford-spanish-corenlp-2015-01-08-models.jar'

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

        lang = iepy.instance.settings.IEPY_LANG
        if lang == 'es':
            edu_mods = "edu/stanford/nlp/models"
            annotators.remove('dcoref')  # not supported for spanish on Stanford 3.4.1
            cmd_args += " -tokenize.language es"
            cmd_args += " -pos.model %s/pos-tagger/spanish/spanish-distsim.tagger" % edu_mods
            cmd_args += " -ner.model %s/ner/spanish.ancora.distsim.s512.crf.ser.gz" % edu_mods
            cmd_args += " -parse.model %s/lexparser/spanishPCFG.ser.gz" % edu_mods

        cmd_args += " -annotators {}".format(",".join(annotators))
        return cmd_args.split()

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

        for directory in os.listdir(DIRS.user_data_dir):
            if directory.startswith("stanford-corenlp-full"):
                stanford_directory = os.path.join(DIRS.user_data_dir, directory)
                if os.path.isdir(stanford_directory):
                    corenlp = os.path.join(stanford_directory, "corenlp.sh")
                    st = os.stat(corenlp)
                    os.chmod(corenlp, st.st_mode | stat.S_IEXEC)
                    break

    # Download extra data for specific language
    if lang.lower() == 'es':
        SPANISH_PATH = os.path.join(_FOLDER_PATH, 'edu', 'stanford', 'nlp', 'models')
        if os.path.isdir(SPANISH_PATH):
            print("Extra data for lang '{}' already downloaded.".format(lang))
        else:
            print("Downloading Stanford CoreNLP extra data for lang '{}'...".format(lang))
            unzip_from_url(DOWNLOAD_URL_ES, _FOLDER_PATH)
    elif lang.lower() != 'en':
        print("There are no extra data to download for lang '{}'.".format(lang))
