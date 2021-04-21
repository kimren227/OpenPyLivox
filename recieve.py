import socket
import sys
import struct
import numpy as np
import open3d as o3d 
import tqdm



def pairwise_registration(source, target):
    print("Apply point-to-point ICP")
    reg_p2p = o3d.pipelines.registration.registration_icp(
        source, target, 0.2, np.eye(4),
        o3d.pipelines.registration.TransformationEstimationPointToPoint())
    print(reg_p2p)
    print("Transformation is:")
    print(reg_p2p.transformation)
    draw_registration_result(source, target, reg_p2p.transformation)
    exit()

num_points = 100000
ip = "127.0.0.1"
# ip = "10.161.32.84"
port = 6006
num_device = 2
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

server_address = (ip, port)
s.bind(server_address)

coord1s = [[] for i in range(num_device)]
coord2s = [[] for i in range(num_device)]
coord3s = [[] for i in range(num_device)]


for i in tqdm.tqdm(range(num_points)):
    data, address = s.recvfrom(4096)

    device_id = struct.unpack('<i', data[28:32])[0]

    coord1s[device_id].append(float(struct.unpack('<i', data[:4])[0]) / 1000.0)
    coord2s[device_id].append(float(struct.unpack('<i', data[4:8])[0]) / 1000.0)
    coord3s[device_id].append(float(struct.unpack('<i', data[8:12])[0]) / 1000.0)
    tag_bits = str(bin(int.from_bytes(data[13:14], byteorder='little')))[2:].zfill(8)

    coord1s[device_id].append(float(struct.unpack('<i', data[14:18])[0]) / 1000.0)
    coord2s[device_id].append(float(struct.unpack('<i', data[18:22])[0]) / 1000.0)
    coord3s[device_id].append(float(struct.unpack('<i', data[22:26])[0]) / 1000.0)
    tag_bits = str(bin(int.from_bytes(data[27:28], byteorder='little')))[2:].zfill(8)

color_code = [[1,0,0],[0,1,0],[0,0,1]]
pcds = []
for i in range(num_device):
    coord1s_d = np.asarray(coord1s[i], dtype=np.float32)
    coord2s_d = np.asarray(coord2s[i], dtype=np.float32)
    coord3s_d = np.asarray(coord3s[i], dtype=np.float32)

    coords_d = np.stack([coord1s_d, coord2s_d, coord3s_d], axis=-1)
    point_label = []
    for point in coords_d:
        if (np.abs(point)<30).sum() == 3:
            point_label.append(True)
        else:
            point_label.append(False)
    pcd = o3d.geometry.PointCloud()
    pcd.points = o3d.utility.Vector3dVector(coords_d[point_label,:])
    pcd.paint_uniform_color(color_code[i])
    pcds.append(pcd)

trans, _ = pairwise_registration(pcds[0], pcds[1])
pcds[1].transform(trans)
for i in range(num_device):
    o3d.io.write_point_cloud("recieved_{}.ply".format(i), pcds[i])