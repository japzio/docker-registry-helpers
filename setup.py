#!/usr/bin/env python3 

from setuptools import setup, find_packages

setup(
    name='ecr2ecr',
    version='1.2',
    author='Jasper Culong',
    author_email='jculongit10@yahoo.com',
    packages=find_packages(),
    license='LICENSE.txt',
    description='Useful towel-related stuff.',
    long_description=open('README.md').read(),
    url="https://pypi.org/project/ecr2ecr",
    entry_points={
        'console_scripts': [
            'ecr2ecr = ecr2ecr.core:main'
        ]
    },
    install_requires=[
        "docker >= 3.7.0",
        "boto3 >= 1.7.57",
    ],
)