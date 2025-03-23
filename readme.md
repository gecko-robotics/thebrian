![](docs/brian.webp)

# The Brian

A collection of functions to simplify working with MCap and Foxglove Visualization.

## Linux

```bash
apt install -y protobuf-compiler
```

## macOS

```bash
brew install protobuf
brew install mcap
pip install -U protobuf==5.29.3 mcap mcap-protobuf-support 
pip install -U foxglove-schemas-protobuf foxglove-websocket[examples]
```

## Foxglove Writer

```python
from thebrian import *

filename = "test.mcap"
an = ...
gn = ...
for i in range(size):
  ts = time_ns()

  msg=Imu()
  msg.header.timestamp=make_timestamp(ts)
  msg.header.frame_id = "imu"
  msg.linear_acceleration=Vector(x=an[i,0],y=an[i,1],z=an[i,2])
  msg.angular_velocity=Vector(x=gn[i,0],y=gn[i,1],z=gn[i,2])

  data["/simple_msgs"].append(msg)

write_mcap(filename, data)

rdata, meta = read_mcap(sys.argv[1])
```

Writes a message to an MCAP file.

Parameters:
- **topic:** the topic that this message was originally published on.
- **message:** a Protobuf object to write into the MCAP.
- **log_time:** unix nanosecond timestamp of when this message was written to the MCAP.
- **publish_time:** unix nanosecond timestamp of when this message was originally published.
- **sequence:** an optional sequence count for messages on this topic.

## Foxglove Protobuf Messages

- [schemas](https://github.com/foxglove/schemas/tree/main/schemas/proto/foxglove)
    - CameraCalibration
    - CompressedImage
    - CompressedVideo
    - FrameTransform[s]
    - GeoJSON
    - LaserScan
    - LocationFix
    - Log
    - Pose[InFrame[s]]
    - Quaternion
    - RawImage
    - Vector3
    - more ...

# MIT License

**Copyright (c) 2024 Mom's Friendly Robot Company**

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
