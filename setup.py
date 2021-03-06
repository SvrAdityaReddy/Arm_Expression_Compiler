#!/usr/bin/python3
# coding=utf-8

from setuptools import setup


package_name = 'aec_arm'

def get_long_description():
    try:
        with open('README.md', 'r') as f:
            return f.read()
    except IOError:
        return ''

setup(
    name=package_name,
    author='depikaraj,amateurcoder10,SvrAdityaReddy',
    author_email='deepika.raj.93@gmail.com,Prashanthi.S.K@iiitb.org,Aditya.seelapureddy@tutanota.com',
    description='convert expressions to arm cotrex M4 code',
    url='https://github.com/SvrAdityaReddy',
    long_description=get_long_description(),
    packages=[package_name],
    entry_points={
        'console_scripts': [
            'aec_arm = aec_arm.__main__:main'
        ]
    },
    license='License :: MIT License',
)
