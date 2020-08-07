from setuptools import setup, find_packages

NAME = "cape-of-good-place-names-scrubbers"
VERSION = "0.1.0"

setup(
    name=NAME,
    version=VERSION,
    description="Cape of Good Place Names Scrubbers",
    author_email="opmdata+cogpn-support@capetown.gov.za",
    url="",
    keywords=["Cape of Good Place Names Service", "GIS"],
    long_description="""\
    This is the container package for "scrubbers", modules that attempts to make human description of a place into a 
    form more ameanable to translation into a spatial identifier.
    """,
    packages=find_packages(),
)
