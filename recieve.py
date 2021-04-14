import socket
import sys
import struct
import numpy as np
import open3d as o3d 
import tqdm

num_points = 100000
# ip = "127.0.0.1"
ip = "10.161.32.84"
port = 6006

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

server_address = (ip, port)
s.bind(server_address)
coord1s = []
coord2s = []
coord3s = []
intensity = []

for i in tqdm.tqdm(range(num_points)):
    data, address = s.recvfrom(4096)
    coord1s.append(float(struct.unpack('<i', data[:4])[0]) / 1000.0)
    coord2s.append(float(struct.unpack('<i', data[4:8])[0]) / 1000.0)
    coord3s.append(float(struct.unpack('<i', data[8:12])[0]) / 1000.0)
    intensity.append(struct.unpack('<B',data[12:13])[0])
    tag_bits = str(bin(int.from_bytes(data[13:14], byteorder='little')))[2:].zfill(8)

    coord1s.append(float(struct.unpack('<i', data[14:18])[0]) / 1000.0)
    coord2s.append(float(struct.unpack('<i', data[18:22])[0]) / 1000.0)
    coord3s.append(float(struct.unpack('<i', data[22:26])[0]) / 1000.0)
    intensity.append(struct.unpack('<B', data[26:27])[0])
    tag_bits = str(bin(int.from_bytes(data[27:28], byteorder='little')))[2:].zfill(8)
    # print(len(data[28:28+8]))
    # timestamp_sec = float(struct.unpack('<d', data[28:28+8])[0])
    # print(timestamp_sec)

coord1s = np.asarray(coord1s, dtype=np.float32)
coord2s = np.asarray(coord2s, dtype=np.float32)
coord3s = np.asarray(coord3s, dtype=np.float32)



coord1s = np.asarray(coord1s)
coord2s = np.asarray(coord2s)
coord3s = np.asarray(coord3s)
coords = np.stack([coord1s, coord2s, coord3s], axis=-1)
pcd = o3d.geometry.PointCloud()
pcd.points = o3d.utility.Vector3dVector(coords)
o3d.io.write_point_cloud("recieved.ply", pcd)