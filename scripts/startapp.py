"""
Create a IEPY application from the default template.

Usage:
    startapp.py <name>
"""
import os

from docopt import docopt


def startapp(name):
    # Sanitize name:
    san_name = name.decode("ascii", "ignore").lower().replace(" ", "_")

    # Create the folder structure
    folder = san_name
    if os.path.exists(folder):
        print "Error: folder '{}' already exists".format(folder)
        return
    os.mkdir(folder)
    os.mkdir(os.path.join(folder, 'scripts'))
    os.mkdir(os.path.join(folder, 'tests'))

    # Create scripts
    os.mknod(os.path.join(folder, 'scripts', '__init__.py'))
    os.mknod(os.path.join(folder, 'tests', '__init__.py'))


if __name__ == '__main__':
    opts = docopt(__doc__, version=0.1)
    appname = opts['<name>']
    startapp(appname)

