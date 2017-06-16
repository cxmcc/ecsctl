#!/usr/bin/env python

from setuptools import setup

install_requires = [
    'boto3',
    'click',
    'configparser',
    'docker',
    'dockerpty',
    'jsonpath',
    'tabulate',
    'humanize',
    'pytz',
]

classifiers = [
    'Development Status :: 4 - Beta',
    'Environment :: Console',
    'Topic :: System :: Clustering',
]

setup(
    name='ecsctl',
    version='20170526',
    description='kubectl-style command line client for AWS ECS.',
    author='Xiuming Chen',
    author_email='cc@cxm.cc',
    url='https://github.com/cxmcc/ecsctl',
    packages=['ecsctl'],
    entry_points={'console_scripts': ['ecsctl = ecsctl.__main__:main']},
    install_requires=install_requires,
    keywords=['ECS', 'kubectl', 'AWS'],
    classifiers=classifiers,
)
