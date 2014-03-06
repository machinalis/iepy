# coding: utf-8

import os
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


base_path = os.path.dirname(os.path.abspath(__file__))
long_description = open(os.path.join(base_path, 'README.rst')).read()
requirements_path = os.path.join(base_path, "docs", "setup", "requirements-base.txt")
requirements = open(requirements_path).read().splitlines()

setup(
    name="iepy",
    version="0.1",
    description="",
    long_description=long_description,
    author="Rafael Carrascosa, Franco Luque, Laura Alonso, Javier Mansilla",
    packages=[
        "iepy"],
    install_requires=requirements,
)
