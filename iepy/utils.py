from getpass import getuser
import zipfile

from appdirs import AppDirs

DIRS = AppDirs('iepy', getuser())


def unzip(zipped_list, n):
    """returns n lists with the elems of zipped_list unsplitted.
    The general case could be solved with zip(*zipped_list), but here we
    are dealing with:
      - un-zipping empy list to n empty lists
      - ensuring that all zipped items in zipped_list have lenght n, raising
        ValueError if not.
    """
    if not zipped_list:
        return tuple([[]]*n)
    else:
        if not all(isinstance(x, tuple) and len(x) == n for x in zipped_list):
            raise ValueError
        return zip(*zipped_list)


def unzip_file(zip_path, extraction_base_path):
    zfile = zipfile.ZipFile(zip_path)
    zfile.extractall(extraction_base_path)
