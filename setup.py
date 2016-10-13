from setuptools import setup, find_packages  # Always prefer setuptools over distutils
from os import path
import sys

assert sys.version_info >= (3, 4, 0), "Python 3.4 or newer is required"


HERE = path.abspath(path.dirname(__file__))

# Get the long description from the relevant file
with open(path.join(HERE, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

with open(path.join(HERE, 'iepy', 'version.txt'), encoding='utf-8') as f:
    iepy_version = f.read().strip()

base_reqs = """nltk>=3.2.1
numpy>=1.8.0
scipy>=0.13.3
scikit-learn==0.15.2
REfO==0.13
docopt==0.6.1
future==0.11.4
appdirs==1.2.0
wget==2.0
colorama==0.2.7
featureforge>=0.1.5
Django==1.8.14
django-relatives==0.3.1
django-relatedadminwidget==0.0.3
six>=1.9.0
django-extra-views==0.7.1
jsonfield==1.0.0
django-angular==0.7.8
nose>=1.3.0
factory-boy==2.4.1
xmltodict==0.8.6""".splitlines()


setup(
    name='iepy',
    version=iepy_version,
    zip_safe=False,
    description='Information Extraction framework in Python',
    long_description=long_description,
    url='https://github.com/machinalis/iepy',

    # Author details
    author=(
        "Rafael Carrascosa, Javier Mansilla, Gonzalo García Berrotarán, "
        "Daniel Moisset, Franco M. Luque",
    ),

    # Choose your license
    license='BSD',

    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 5 - Production/Stable',

        # Indicate who your project is intended for
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'Intended Audience :: Information Technology',

        # Pick your license as you wish (should match "license" above)
        'License :: OSI Approved :: BSD License',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3 :: Only',
    ],

    # What does your project relate to?
    keywords='information extraction relation detection',

    # You can just specify the packages manually here if your project is
    # simple. Or you can use find_packages().
    packages=find_packages(exclude=['docs', 'tests*', 'scripts']),
    include_package_data=True,

    # List run-time dependencies here.  These will be installed by pip when your
    # project is installed. For an analysis of "install_requires" vs pip's
    # requirements files see:
    # https://packaging.python.org/en/latest/technical.html#install-requires-vs-requirements-files
    install_requires=base_reqs,

    # To provide executable scripts, use entry points in preference to the
    # "scripts" keyword. Entry points provide cross-platform support and allow
    # pip to create the appropriate form of executable for the target platform.
    entry_points={
        'console_scripts': [
            'iepy=iepy.instantiation.command_line:execute_from_command_line',
        ],
    },
)
