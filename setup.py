#! /usr/bin/env python
# -*- coding: utf-8 -*-
# Date: 2022/2/22

import setuptools


with open('README.md', 'r') as fd:
    long_description = fd.read()


setuptools.setup(
    name='pydp-amq',
    version='1.0.0',
    author='Wang Chao',
    author_email='wangchao@trunk.tech',
    description='Python Data Process',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='',
    packages=setuptools.find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
)
