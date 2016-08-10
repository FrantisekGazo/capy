#!/usr/bin/env python
# coding=utf-8

from setuptools import setup

DESCRIPTION = '''CAPY is a helper for running calabash tests on iOS and Android'''
LONG_DESCRIPTION = DESCRIPTION

setup(
    author='František Gažo',
    author_email='frantisek.gazo@inloop.eu',
    name='capy',
    version='0.4.2',
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    url='https://github.com/FrantisekGazo/capy/',
    platforms=['MacOS'],
    license='MIT License',
    classifiers=[ # https://pypi.python.org/pypi?%3Aaction=list_classifiers
        'Programming Language :: Python :: 2.7',
        'Development Status :: 1 - Planning',
        'Operating System :: MacOS',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Topic :: Utilities'
    ],
    packages=[
        'capy'
    ],
    install_requires=[ # list of this package dependencies
        'PyYAML>=3.11'
    ],
    entry_points='''
        [console_scripts]
        capy=capy.capy:main
    '''
)