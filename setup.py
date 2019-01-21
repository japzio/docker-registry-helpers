#!/usr/bin/env python3 

from distutils.core import setup

setup(
  name='docker-imgreplicator-py',
  version='1.0',
  description='aws ecr docker image cross-region replicator',
  author='Jasper Culong',
  author_email='jculongit10@yahoo.com',
  packages=['tests'],  #same as name
  install_requires=[
    'boto3',
    'docker',
  ]
)