# coding: utf-8

import sys
from setuptools import setup, find_packages

NAME = "cape_of_good_place_names"
VERSION = "0.1.0"
# To install the library, run the following
#
# python setup.py install
#
# prerequisite: setuptools
# http://pypi.python.org/pypi/setuptools

REQUIRES = ["connexion"]

setup(
    name=NAME,
    version=VERSION,
    description="Cape of Good Place Names Service",
    author_email="opmdata+cogpn-support@capetown.gov.za",
    url="",
    keywords=["Swagger", "Cape of Good Place Names Service"],
    install_requires=REQUIRES,
    packages=find_packages(),
    package_data={'': ['swagger/swagger.yaml']},
    include_package_data=True,
    entry_points={
        'console_scripts': ['cape_of_good_place_names=cape_of_good_place_names.__main__:main']},
    long_description="""\
    This is a stateless service for performing various geotranslation operations, moving between how people describe places and codified coordinate systems.
    """
)
