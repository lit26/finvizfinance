"""
.. module:: __init__
    :synopsis: finvizfinance package general information

.. moduleauthor:: Tianning Li <ltianningli@gmail.com>
"""

from __future__ import annotations

import logging

# Library convention: attach a NullHandler to the package's top-level logger so
# finvizfinance never emits log output unless the application configures logging.
logging.getLogger(__name__).addHandler(logging.NullHandler())

__version__ = "1.5.0"
__author__ = "Tianning Li"
