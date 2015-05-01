#!/usr/bin/python

'''
	Flask-Permissions
	-----------

	A flexible, rule-based permission control system,
	designed to integrate well with Flask.

'''

from setuptools import setup

setup(
	name='Flask-Permissions',
	version='0.1',
	author='Kai Wohlfahrt',
	description='Handling rule-based permissions for objects',
	long_description=__doc__,
	packages=['permissions'],
	platforms='any',
	install_requires=[],
	test_suite='test',
)
