

# from foxglove_schemas_protobuf.CameraCalibration_pb2 import CameraCalibration
# from foxglove_schemas_protobuf.RawImage_pb2 import RawImage
# from foxglove_schemas_protobuf.CompressedImage_pb2 import CompressedImage
# from google.protobuf.timestamp_pb2 import Timestamp
# from google.protobuf import timestamp_pb2

from mcap_protobuf.writer import Writer
from mcap_protobuf.decoder import DecoderFactory
from mcap.reader import make_reader
from collections import deque
from collections import defaultdict

def read_mcap(filename):
    """
    Read mcap file

    Args:
        filename
    Return:
        defaultdict(deque)
        dict: metadata of topics
    """
    data = defaultdict(deque)
    meta = {}
    with open(filename, "rb") as f:
        reader = make_reader(f, decoder_factories=[DecoderFactory()])
        for schema, channel, message, proto_msg in reader.iter_decoded_messages():
            data[channel.topic].append(proto_msg)
            meta[channel.topic] = {"schema": schema.name, "count": len(data[channel.topic])}

    # print(meta)
    return data, meta



def write_mcap(filename, data):
    """
    Write an mcap file

    Args:
        filename
        data: defaultdict(deque)
    """
    with open(filename, "wb") as f, Writer(f) as mcap_writer:
        for topic, deq in data.items():
            for msg in deq:
                ts = make_int(msg.timestamp)
                print(ts)
                mcap_writer.write_message(
                    topic=topic,
                    message=msg,
                    log_time=ts,
                    publish_time=ts,
                )
