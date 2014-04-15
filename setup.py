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

# parse_requirements() returns generator of pip.req.InstallRequirement objects
install_reqs = parse_requirements(requirements_path)
reqs = [str(ir.req) for ir in install_reqs]

setup(
    name="iepy",
    version="0.1",
    description="",
    long_description=long_description,
    author=("Rafael Carrascosa, Franco Luque, Laura Alonso, "
            "Javier Mansilla, Daniel Moisset"),
    packages=[
        "iepy"],
    install_requires=reqs,
)
