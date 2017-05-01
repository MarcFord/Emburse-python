import os
import sys
import warnings

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

try:
    from distutils.command.build_py import build_py_2to3 as build_py
except ImportError:
    from distutils.command.build_py import build_py

here = os.path.abspath(os.path.dirname(__file__))
os.chdir(os.path.abspath(here))

install_requires = ['python-dateutil >= 2.6.0']

if sys.version_info < (2, 6):
    warnings.warn(
        'Python 2.5 is not supported by the Emburse Client', DeprecationWarning)

    install_requires.append('requests >= 0.8.8, < 0.10.1')
    install_requires.append('ssl')
else:
    install_requires.append('requests >= 0.8.8')


with open(os.path.join(here, 'DESCRIPTION.rst')) as f:
    long_description = f.read()

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'emburse'))
from version import VERSION

setup(
    name='emburse',
    cmdclass={'build_py': build_py},
    version=VERSION,
    description='Emburse python bindings',
    long_description=long_description,
    author='Marc Ford',
    author_email='marc.ford@gmail.com',
    url='https://github.com/TheNixNinja/Emburse-python',
    license='GPLv3',
    packages=['emburse'],
    package_data={'emburse': ['data/ca-certificates.crt']},
    install_requires=install_requires,
    test_suite='tests.all',
    tests_require=['unittest2', 'mock'],
    use_2to3=True,
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GPLv3 License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: Implementation :: PyPy",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    keywords='emburse'
)
