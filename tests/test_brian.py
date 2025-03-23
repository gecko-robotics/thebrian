from thebrian import *
import pytest

def test_time():
  gtime = Timestamp(seconds=123,nanos=123)
  btime = make_timestamp(123_000_000_123)
  assert gtime.seconds == btime.seconds
  assert gtime.nanos == btime.nanos

  assert 123_000_000_123 == to_int(btime)
