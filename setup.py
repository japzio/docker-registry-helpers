#!/usr/bin/env python3 

from distutils.core import setup

setup(
    name='ECR Image Copy',
    version='0.1.0',
    author='Jasper Culong',
    author_email='jasper.culong@truste.com',
    packages=['tests'],
    license='LICENSE.txt',
    description='Useful towel-related stuff.',
    long_description=open('README.md').read(),
    install_requires=[
        "docker >= 3.7.0",
        "boto3 >= 1.7.57 ",
    ],
)