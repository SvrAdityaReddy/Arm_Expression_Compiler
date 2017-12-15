#!/usr/bin/env python
# coding=utf-8

from setuptools import setup


package_name = 'arm_expression_compiler_nobat'
filename = 'source/'+'arm_expression_compiler' + '_nobat'+'.py'


def get_version():
    import ast

    with open(filename) as input_file:
        for line in input_file:
            if line.startswith('__version__'):
                return ast.parse(line).body[0].value.s


def get_long_description():
    try:
        with open('README.md', 'r') as f:
            return f.read()
    except IOError:
        return ''


setup(
    name=package_name,
    author='depikaraj,amateurcoder10,SvrAdityaReddy',
    author_email='deepika.raj.93@gmail.com,Prashanthi.S.K@iiitb.org,Aditya.seelapureddy@yahoo.com',
    description='convert expressions to arm cotrex M4 code',
    url='https://github.com/SvrAdityaReddy',
    long_description=get_long_description(),
    py_modules=[package_name],
    entry_points={
        'console_scripts': [
            'arm_expression_compiler_nobat = source.arm_expression_compiler_nobat:main'
        ]
    },
    license='License :: MIT License',
)