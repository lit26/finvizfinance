import pathlib
from setuptools import setup, find_packages

HERE = pathlib.Path(__file__).parent

VERSION = '1.0.1'
PACKAGE_NAME = 'finvizfinance'
AUTHOR = 'Tianning Li'
AUTHOR_EMAIL = 'ltianningli@gmail.com'
URL = 'https://github.com/lit26/finvizfinance'

LICENSE = 'The MIT License (MIT)'
DESCRIPTION = 'Finviz Finance. Information downloader.'
LONG_DESCRIPTION = (HERE / "README.md").read_text()
LONG_DESC_TYPE = "text/markdown"

INSTALL_REQUIRES = [
      'pandas',
      'requests',
      'beautifulsoup4',
      'lxml'
]
CLASSIFIERS = [
      'Programming Language :: Python :: 3.9',
      'Programming Language :: Python :: 3.10',
      'Programming Language :: Python :: 3.11',
      'License :: OSI Approved :: MIT License'
]
PYTHON_REQUIRES='>=3.9'

setup(name=PACKAGE_NAME,
      version=VERSION,
      description=DESCRIPTION,
      long_description=LONG_DESCRIPTION,
      long_description_content_type=LONG_DESC_TYPE,
      author=AUTHOR,
      license=LICENSE,
      author_email=AUTHOR_EMAIL,
      url=URL,
      classifiers=CLASSIFIERS,
      install_requires=INSTALL_REQUIRES,
      packages=find_packages(),
      python_requires=PYTHON_REQUIRES
      )
