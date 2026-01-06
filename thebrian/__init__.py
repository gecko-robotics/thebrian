##############################################
# The MIT License (MIT)
# Copyright (c) 2014 Kevin Walchko
# see LICENSE for full details
##############################################
# -*- coding: utf-8 -*

from .utils import *
from .mcap_file import *
from .stream import *
from .tuples import *

from .protobuf.oak_pb2 import *


def from_nanoseconds(self, ns):
  self.seconds = ns // 1_000_000_000
  self.nanos = ns % 1_000_000_000

Timestamp.FromNanoseconds = from_nanoseconds

from importlib.metadata import version # type: ignore

__license__ = 'MIT'
__copyright__ = 'Copyright (c) 2024 Kevin Walchko'
__author__ = 'Kevin J. Walchko'
__version__ = version("thebrian")