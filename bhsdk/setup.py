#!/usr/bin/env python3

from os import getenv
from distutils.core import setup

setup(name='bhsdk',
    version='1.0',
    description='Bithedge SDK',
    author='Kenneth Feng',
    author_email='',
    url='',
    package_dir={'bhsdk': 'src'},
    packages=['bhsdk', 'bhsdk.rates'],
    data_files=[(getenv('HOME') + '/bhsdk-config/', ['bhsite.conf'])]
    )
