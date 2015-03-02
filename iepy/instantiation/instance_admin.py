import filecmp
import json
import os
import shutil
import sys

from django.utils.crypto import get_random_string
from django.core.management import execute_from_command_line as django_command_line

import iepy
from iepy import defaults
from iepy.utils import DIRS, unzip_from_url

THIS_FOLDER = os.path.dirname(os.path.abspath(__file__))


class InstanceManager:
    # class instead of a fuction just for allowing better code organization

    files_to_copy = [
        "csv_to_iepy.py",
        "preprocess.py",
        "iepy_runner.py",
        "iepy_rules_runner.py",
        "rules_verifier.py",
        "manage.py",
        "gazettes_loader.py",
    ]
    steps = [
        'create_folders',
        'create_init_file',
        'copy_bin',
        'create_rules_file',
        'create_extractor_config_file',
        # Put this following step at the end of all the steps that doesnt need settings
        'configure_settings_file',
        'migrate_db',
        'create_db_user',
        'greetings',
    ]

    def __init__(self, folder_path, lang='en'):
        self.folder_path = folder_path
        self.abs_folder_path = os.path.abspath(self.folder_path)
        self.creating = True
        self.lang = lang

    def _run_steps(self):
        for step_name in self.steps:
            step = getattr(self, step_name)
            step()

    def create(self):
        if os.path.exists(self.folder_path):
            print("Error: folder already exists")
            sys.exit(1)
        self._run_steps()

    def upgrade(self):
        if not os.path.exists(self.folder_path):
            print("Error: instance folder does not exist")
            sys.exit(1)

        try:
            actual_path = iepy.setup(self.folder_path, _safe_mode=True)
        except ValueError as err:
            print(err)
            sys.exit(1)
        finally:
            self.folder_path = actual_path
            self.abs_folder_path = os.path.abspath(self.folder_path)

        from django.conf import settings
        self.old_version = settings.IEPY_VERSION
        if settings.IEPY_VERSION == iepy.__version__:
            print("Iepy instance '{}' is already up to date.".format(self.folder_path))
            return
        print("Upgrading iepy instance '{}' from {} to {}".format(
            self.folder_path, self.old_version, iepy.__version__))
        self.creating = False
        self.old_version_path = self.download_old_iepy_version()
        self._run_steps()

    def download_old_iepy_version(self):
        oldv = self.old_version
        url = "https://pypi.python.org/packages/source/i/iepy/iepy-{}.tar.gz".format(oldv)
        old_versions_path = os.path.join(DIRS.user_data_dir, 'old_versions')
        os.makedirs(old_versions_path, exist_ok=True)
        asked_tag_path = os.path.join(old_versions_path, 'iepy-{}'.format(oldv))
        if not os.path.exists(asked_tag_path):
            print ('Downloading old iepy version {} for allowing patches'.format(oldv))
            unzip_from_url(url, old_versions_path)
            print('Done')
        return asked_tag_path

    def create_folders(self):
        self.bin_folder = os.path.join(self.folder_path, "bin")
        os.makedirs(self.bin_folder, exist_ok=not self.creating)

    def create_init_file(self):
        rules_filepath = os.path.join(self.folder_path, "__init__.py")
        with open(rules_filepath, "w") as filehandler:
            filehandler.write("from . import rules")

    def copy_bin(self):
        # Create folders
        for filename in self.files_to_copy:
            destination = os.path.join(self.bin_folder, filename)
            self._copy_file(filename, destination)

    def create_rules_file(self):
        rules_filepath = os.path.join(self.folder_path, "rules.py")
        if self.creating:
            with open(rules_filepath, "w") as filehandler:
                filehandler.write("# Write here your rules\n")
                filehandler.write("# RELATION = 'your relation here'\n")

    def create_extractor_config_file(self):
        # Create extractor config
        config_filepath = os.path.join(self.folder_path, "extractor_config.json")

        def do_it():
            with open(config_filepath, "w") as filehandler:
                json.dump(defaults.extractor_config, filehandler, indent=4)

        if self.creating:
            do_it()
        else:
            if json.load(open(config_filepath)) != defaults.extractor_config:
                msg = 'Should we override your extraction config settings?'
                msg += ' (existing version will be backed up first)'
                if self.prompt(msg):
                    self.preserve_old_file_version_as_copy(config_filepath)
                    do_it()
                    print ('Extraction configs upgraded.')
            else:
                    print ('Extraction configs left untouched.')

    def _copy_file(self, filename, destination):
        filepath = os.path.join(THIS_FOLDER, filename)

        def do_it():
            shutil.copyfile(filepath, destination)

        if self.creating:
            do_it()
        else:
            # first check if the file is already present
            if not os.path.exists(destination):
                do_it()
            else:
                # file exists. Let's check if what the instance has is the
                # vainilla old version or not
                old_version_filepath = os.path.join(
                    self.old_version_path, 'iepy', 'instantiation', filename)
                if os.path.exists(old_version_filepath) and filecmp.cmp(old_version_filepath, destination):
                    # vainilla old version. Let's simply upgrade it
                    do_it()
                else:
                    # customized file.
                    # Check if it's exactly what the new version provides
                    if filecmp.cmp(filepath, destination):
                        # you have local changes that are 100% new version. Sounds like
                        # you made your instance with a nightly built.. dunno, but we'll
                        # do nothing, since is not needed.
                        return
                    # We'll back it up, and later upgrade
                    self.preserve_old_file_version_as_copy(destination)
                    do_it()

    def prompt(self, msg):
        answer = input("%s (y/n) " % msg).lower().strip()
        while answer not in ['y', 'n']:
            print ('Invalid answer "{}".'.format(answer))
            answer = input("%s (y/n) " % msg).lower().strip()
        return answer == 'y'

    def preserve_old_file_version_as_copy(self, fpath):
        i = 1
        while True:
            back_up_path = fpath + '.backup_{}'.format(i)
            if not os.path.exists(back_up_path):
                break
            i += 1
        shutil.copyfile(fpath, back_up_path)
        print("Backed up your instance version of {} at {}. "
              "Remove it if you don't need it".format(fpath, back_up_path))

    def configure_settings_file(self):
        # Create the settings file
        folder_name = os.path.basename(self.folder_path)  # aka iepy instance name
        settings_filepath = os.path.join(self.folder_path, "settings.py")

        def do_it():
            print("Initializing database")
            print("By default, we will create an SQLite database although "
                  "it has a very poor performance, specialy with large amounts "
                  "of text.\nYou might want to change this in the future.")
            database_name = input("Database name [{}]: ".format(folder_name))
            if not database_name:
                database_name = folder_name
            database_path = os.path.join(self.abs_folder_path, database_name)
            settings_data = get_settings_string(database_path, self.lang)
            with open(settings_filepath, "w") as filehandler:
                filehandler.write(settings_data)
        if self.creating:
            do_it()
        else:
            if self.old_version in ["0.9", "0.9.0", "0.9.1"]:
                old_settings_filepath = os.path.join(
                    self.folder_path, "{}_settings.py".format(folder_name)
                )
                shutil.move(old_settings_filepath, settings_filepath)

            with open(settings_filepath, 'a') as fhandler:
                msg = 'Remove line declaring the old IEPY_VERSION above.'
                fhandler.write(
                    "IEPY_VERSION = '{}'  # {}\n".format(iepy.__version__, msg))
            print ('Patched IEPY_VERSION at {}.'.format(settings_filepath))

    def migrate_db(self):
        # Setup IEPY with the new instance
        os.chdir(self.abs_folder_path)
        iepy.setup(self.abs_folder_path)
        django_command_line(["", "migrate"])

    def create_db_user(self):
        # Setup the database user
        if self.creating:
            print("\nCreating database user")
            django_command_line(["", "createsuperuser"])

    def greetings(self):
        print("\n IEPY instance ready to use at '{}'".format(self.abs_folder_path))


def get_settings_string(database_path, lang):
    template_settings_filepath = os.path.join(THIS_FOLDER, "settings.py.template")
    with open(template_settings_filepath) as filehandler:
        settings_data = filehandler.read()

    if not database_path.endswith(".sqlite"):
        database_path += ".sqlite"

    chars = 'abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)'
    secret_key = get_random_string(50, chars)
    settings_data = settings_data.replace("{SECRET_KEY}", secret_key)
    settings_data = settings_data.replace("{DATABASE_PATH}", database_path)
    settings_data = settings_data.replace("{IEPY_VERSION}", iepy.__version__)
    settings_data = settings_data.replace("{LANG}", lang)

    return settings_data
