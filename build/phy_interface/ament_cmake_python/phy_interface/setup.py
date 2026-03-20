from setuptools import find_packages
from setuptools import setup

setup(
    name='phy_interface',
    version='0.0.1',
    packages=find_packages(
        include=('phy_interface', 'phy_interface.*')),
)
