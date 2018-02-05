"""
Setup script for ROV.
"""

from setuptools import setup, find_packages

setup(
    name='rov-control',
    version='1.0.0',
    description='A module that controls the ROV and its devices.',
    url='https://github.com/UNH-ROV/ROV-006',
    py_modules=['rov'],
    install_requires=[
        'pySerial',
        'Adafruit_PCA9685',
    ],
)
