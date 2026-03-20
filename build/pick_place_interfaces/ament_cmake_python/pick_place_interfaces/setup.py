from setuptools import find_packages
from setuptools import setup

setup(
    name='pick_place_interfaces',
    version='0.1.0',
    packages=find_packages(
        include=('pick_place_interfaces', 'pick_place_interfaces.*')),
)
