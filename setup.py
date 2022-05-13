#!/usr/bin/python
#
from setuptools import setup, find_packages

setup(
    name='synack',
    version='0.1.0',
    description='SynackAPI',
    packages=find_packages(include=['synack', 'synack.*']),
    install_requires=[
        'netaddr',
        'pathlib2',
        'pyotp',
        'numpy',
        'requests',
        'selenium',
        'urllib3',
        'psycopg2-binary',
        'cmd2',
    ],
    entry_points={
        'console_scripts': [
            'synack = synack.__main__:main'
        ]
    }
)

