from collections import namedtuple

# vector_t = namedtuple("vector_t", "x y z")
StereoImages = namedtuple("StereoImages", "left right timestamp")
Imu = namedtuple("Imu", "a g timestamp")
CameraInfo = namedtuple("CameraInfo","height width distortion_model d k r p hfov timestamp")
StereoInfo = namedtuple("StereoInfo", "left right imu2camera")

CameraConfigs = namedtuple("CameraConfigs", "w h minFps maxFps type")
CameraFeatures = namedtuple("CameraFeatures", "name sensor height width socket type")
