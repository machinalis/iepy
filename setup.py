from setuptools import setup, find_packages  # Always prefer setuptools over distutils
from pip.req import parse_requirements
from os import path

HERE = path.abspath(path.dirname(__file__))

# Get the long description from the relevant file
with open(path.join(HERE, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()


requirements_path = path.join(HERE, "docs", "setup", "requirements-base.txt")
install_reqs = list(parse_requirements(requirements_path))
dev_requirements_path = path.join(HERE, "docs", "setup", "requirements-development.txt")
dev_reqs = [str(x.req) for x in parse_requirements(requirements_path)]
base_reqs = []
deps = [u'%s#egg=%s' % (ir.url, ir.url_name) for ir in install_reqs if ir.url]

for ir in install_reqs:
    if ir.name.startswith(u'nltk-'):
        # For nltk on py3 we are declaring nltk just as an URL
        base_reqs.insert(0, ir.name.replace(u'-', u'==', 1))
        # install it first, so if nltk tarball is not working you not waste time
    else:
        base_reqs.append(str(ir.req))

setup(
    name='iepy',
    version='1.2.0',
    zip_safe=False,
    description='',
    long_description=long_description,
    url='https://github.com/machinalis/iepy',

    # Author details
    author=(
        "Rafael Carrascosa, Franco M. Luque, Laura Alonso, "
        "Javier Mansilla, Daniel Moisset, Gonzalo García",
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

    # List additional groups of dependencies here (e.g. development dependencies).
    # You can install these using the following syntax, for example:
    # $ pip install -e .[dev,test]
    extras_require = {'dev': dev_reqs},

    # To provide executable scripts, use entry points in preference to the
    # "scripts" keyword. Entry points provide cross-platform support and allow
    # pip to create the appropriate form of executable for the target platform.
    entry_points={
        'console_scripts': [
            'iepy=iepy.instantiation.command_line:execute_from_command_line',
        ],
    },
)
