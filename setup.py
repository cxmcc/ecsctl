#!/usr/bin/env python

from setuptools import setup

install_requires = [
    'boto3>=1.4.5',
    'click>=6.7',
    'configparser>=3.5.0',
    'docker>=2.4.2',
    'dockerpty>=0.4.1',
    'jsonpath>=0.75',
    'tabulate>=0.7.7',
    'humanize>=0.5.1',
    'pytz>=2017.2',
]

classifiers = [
    'Development Status :: 4 - Beta',
    'Environment :: Console',
    'Topic :: System :: Clustering',
]

with open('README.rst', 'r') as f:
    long_description = f.read()

setup(
    name='ecsctl',
    version='20170819',
    description='kubectl-style command line client for AWS ECS.',
    long_description=long_description,
    author='Xiuming Chen',
    author_email='cc@cxm.cc',
    url='https://github.com/cxmcc/ecsctl',
    packages=['ecsctl'],
    entry_points={'console_scripts': ['ecsctl = ecsctl.__main__:main']},
    install_requires=install_requires,
    keywords=['ECS', 'kubectl', 'AWS'],
    classifiers=classifiers,
)
