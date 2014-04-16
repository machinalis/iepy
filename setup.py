# coding: utf-8
import os
import sys

from pip.req import parse_requirements

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

if (sys.version_info > (3, 0)):
    # Python 3 code in this block
    reqs_filename = "requirements-base-py3.txt"
else:
    # Python 2 code in this block
    reqs_filename = "requirements-base-py2.txt"

base_path = os.path.dirname(os.path.abspath(__file__))
long_description = open(os.path.join(base_path, 'README.rst')).read()
requirements_path = os.path.join(base_path, "docs", "setup", reqs_filename)

install_reqs = list(parse_requirements(requirements_path))
reqs = []
deps = []
for ir in install_reqs:
    if ir.name.startswith(u'nltk-'):
        # For nltk on py3 we are declaring nltk just as an URL
        reqs.insert(0, ir.name.replace(u'-', u'==', 1))
        # install it first, so if nltk tarball is not working you not waste time
    else:
        reqs.append(str(ir.req))
deps = [u'%s#egg=%s' % (ir.url, ir.url_name) for ir in install_reqs if ir.url]

setup(
    name="iepy",
    version="0.1",
    description="",
    long_description=long_description,
    author=("Rafael Carrascosa, Franco M. Luque, Laura Alonso, "
            "Javier Mansilla, Daniel Moisset"),
    packages=[
        "iepy"],
    install_requires=reqs,
    dependency_links=deps,
)
