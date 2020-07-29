import pathlib
from setuptools import setup, find_packages

HERE = pathlib.Path(__file__).parent

VERSION = '0.1.1'
PACKAGE_NAME = 'finvizfinance'
AUTHOR = 'Tianning Li'
AUTHOR_EMAIL = 'ltianningli@gmail.com'
URL = 'https://github.com/lit26/finvizfinance'

LICENSE = 'The MIT License (MIT)'
DESCRIPTION = 'Finviz Finance. Information downloader'
LONG_DESCRIPTION = (HERE / "README_pypi.md").read_text()
LONG_DESC_TYPE = "text/markdown"

INSTALL_REQUIRES = [
      'pandas',
      'datetime',
      'requests',
      'bs4'
]

setup(name=PACKAGE_NAME,
      version=VERSION,
      description=DESCRIPTION,
      long_description=LONG_DESCRIPTION,
      long_description_content_type=LONG_DESC_TYPE,
      author=AUTHOR,
      license=LICENSE,
      author_email=AUTHOR_EMAIL,
      url=URL,
      install_requires=INSTALL_REQUIRES,
      packages=find_packages()
      )