from setuptools import setup

NAME = "basic_scrubber"
VERSION = "0.1.0"

setup(
    name=NAME,
    version=VERSION,
    description="Cape of Good Place Names Basic Scrubber",
    author_email="opmdata+cogpn-support@capetown.gov.za",
    url="",
    keywords=["Cape of Good Place Names Service"],
    long_description="""\
    This is a minimalist implementation of a "scrubber", a module that attempts to make a human description of a place 
    into a form more ameanable to translation into a spatial identifier.
    """
)
