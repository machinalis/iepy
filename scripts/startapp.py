"""
Create a IEPY application from the default template.

Usage:
    startapp.py <name>
"""
import os
import shutil

from docopt import docopt

import iepy

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
    os.mknod(os.path.join(folder, 'scripts', '__init__.py'))
    os.mknod(os.path.join(folder, 'tests', '__init__.py'))

    iepy_basedir = os.path.dirname(os.path.abspath(iepy.__file__))

    # Create scripts from templates
    scripts = ['createdb.py', 'preprocess.py']
    for s in scripts:
        template_filename = 'app_{0}.template'.format(s)
        template_file = os.path.join(iepy_basedir, 'tutorial', template_filename)
        preprocess_file = os.path.join(folder, 'scripts', s)
        shutil.copyfile(template_file, preprocess_file)


if __name__ == '__main__':
    opts = docopt(__doc__, version=0.1)
    appname = opts['<name>']
    startapp(appname)

