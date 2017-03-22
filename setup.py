from setuptools import setup

import imp
_version = imp.load_source("treecat._version", "treecat/_version.py")

setup(
    name='treecat',
    version=_version.__version__,
    author='Tom Flanagan',
    author_email='tom@zkpq.ca',
    license='MIT',
    url='https://github.com/Knio/treecat',

    description='Displays a tree view of files and their contents',
    packages=['treecat'],
    keywords='tool file',
    include_package_data = True,

    classifiers=[
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Topic :: Desktop Environment :: File Managers',
        'Topic :: System :: Filesystems',
        'Topic :: Utilities',
    ]
)
