
from google.protobuf.timestamp_pb2 import Timestamp
import time

def make_timestamp(time_ns: int) -> Timestamp:
  return Timestamp(seconds=time_ns // 1_000_000_000, nanos=time_ns % 1_000_000_000)

def make_timestamp_now() -> Timestamp:
  time_ns = time.time_ns()
  return make_timestamp(time_ns)

def to_int(timestamp: Timestamp) -> int:
  return timestamp.seconds*1_000_000_000 + timestamp.nanos