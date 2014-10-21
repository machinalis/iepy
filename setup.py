# coding: utf-8
import os

from pip.req import parse_requirements

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


base_path = os.path.dirname(os.path.abspath(__file__))
long_description = open(os.path.join(base_path, 'README.rst')).read()
requirements_path = os.path.join(base_path, "docs", "setup", "requirements-base.txt")

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
