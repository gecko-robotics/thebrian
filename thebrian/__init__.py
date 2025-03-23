##############################################
# The MIT License (MIT)
# Copyright (c) 2014 Kevin Walchko
# see LICENSE for full details
##############################################
# -*- coding: utf-8 -*

from .utils import *
from .file import *
from .stream import *

from importlib.metadata import version # type: ignore

__license__ = 'MIT'
__copyright__ = 'Copyright (c) 2024 Kevin Walchko'
__author__ = 'Kevin J. Walchko'
__version__ = version("thebrian")