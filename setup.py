#!/usr/bin/env python

from setuptools import setup

setup(name='tap-zoom',
      version='2.0.2',
      description='Singer.io tap for extracting data from the Zoom API',
      classifiers=['Programming Language :: Python :: 3 :: Only'],
      py_modules=['tap_zoom'],
      install_requires=[
        'backoff==1.8.0',
        'ratelimit==2.2.1',
        'requests==2.31.0',
        'singer-python==5.13.0'
      ],
      entry_points='''
          [console_scripts]
          tap-zoom=tap_zoom:main
      ''',
      packages=['tap_zoom'],
      package_data = {
          'tap_zoom': ['schemas/*.json'],
      }
)