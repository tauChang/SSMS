"""
This script is tested and ran only using Python 3.7.9 on MacOS.
"""
"""
This script creates a json file of topology as an input to YAFS.
In this topology, there are three types of devices: cloud_server, fog_server, and car.
All entities of the same type have identical configurations (except ID).
All cloud-server are connected with each other.
All fog-server are connected sequentially (0 - 1 - 2 - ...).
All fog-server are connected to all cloud-server.
All car are not connected with any devices.

Cloud-server are placed along a straight line, with a fixed interval.
Fog-server are placed along a straight line, with a fixed interval.
"""
import json
from coordinateToolkit import *

def create_entity_entry(id, config, lat, lng):
    result = config.copy()
    result["id"] = id
    result["lat"] = lat
    result["lng"] = lng
    return result

def create_single_type_entity_list(device_count, device_first_id, device_first_coord, device_bearing, device_distance, device_config):
    result = []

    for i in range(0, device_count):
        coord = get_next_coordinate(
            (device_first_coord["lat"], device_first_coord["lng"]), 
            device_distance * i, 
            device_bearing
        )

        result.append(create_entity_entry(device_first_id + i, device_config, coord[0], coord[1]))

    return result

def create_link_entry(s, d, BW, PR):
    return {"s": s, "d": d, "BW": BW, "PR": PR}

def create_cloud_server_link_list(server_count, server_first_id, BW, PR):
    """
    All cloud-server are connected with each other.
    """
    result = []
    if server_count <= 1:
        return result
    for i in range(0, server_count):
        for j in range(i + 1, server_count):
            result.append(create_link_entry(server_first_id + i, server_first_id + j, BW, PR))
    return result

def create_cloud_fog_link_list(cloud_server_count, cloud_server_first_id, fog_server_count, fog_server_first_id, BW, PR):
    """
    All fog-server are connected to all cloud-server.
    """
    result = []
    for i in range(0, cloud_server_count):
        for j in range(0, fog_server_count):
            result.append(create_link_entry(cloud_server_first_id + i, fog_server_first_id + j, BW, PR))
    return result

def create_fog_server_link_list(server_count, server_first_id, BW, PR):
    """
    All fog-server are connected sequentially (0 - 1 - 2 - ...).
    """
    result = []
    if server_count <= 1:
        return result
    for i in range(0, server_count - 1):
        result.append(create_link_entry(server_first_id + i, server_first_id + i + 1, BW, PR))
    return result

# User input -----------------------------------------------------
file_path = "/Users/TommyChang/Desktop/networkDefinition.json"  # will be appended with _0.gpx, _1.gpx, ...
# Entity
cloud_server_count = 1
cloud_server_first_id = 0  # the second cloud_server will have id cloud_server_first_id+1, etc.
cloud_server_first_coord = {"lat": 0, "lng": 0}
cloud_server_direction_coord = None
cloud_server_bearing = 0 # if bearing is given, direction_coord will be ignored
cloud_server_distance = 0
cloud_server_config = {
    "model": "cloud-server",
    "IPT": 2000000, # 2000 MIPS
    "RAM": 40000,
    "level": 2 # Not sure if would be used in SMSS
}

fog_server_count = 1
fog_server_first_id = 100
fog_server_first_coord = {"lat": 0, "lng": 0}
fog_server_direction_coord = None
fog_server_bearing = 0  # if bearing is given, direction_coord will be ignored (0 is north, 180 is south)
fog_server_distance = 0.6
fog_server_config = {
    "model": "fog-server",
    "IPT": 800000,
    "RAM": 100,
    "level": 0 # Note, network endpoints should be level 0
}

car_count = 32
car_first_id = 10000
car_first_coord = {"lat": 89, "lng": -179}
car_direction_coord = None # to south
car_bearing = 180.0 # if bearing is given, direction_coord will be ignored
car_distance = 0
car_config = {
    "model": "car",
    "IPT": 1000, # doesn't matter
    "RAM": 1,  # doesn't matter
    "level": -1 
}

# Link
cloud_server_BW = 1 #Mb/time unit
cloud_server_PR = 15 # time unit (ms)
cloud_fog_BW = 1
cloud_fog_PR = 15
fog_server_BW = 1
fog_server_PR = 1

# User input end -------------------------------------------------

if cloud_server_bearing == None:
    cloud_server_bearing = calculate_bearing(cloud_server_first_coord, cloud_server_direction_coord)

if fog_server_bearing == None:
    fog_server_bearing = calculate_bearing(fog_server_first_coord, fog_server_direction_coord)

if car_bearing == None:
    car_bearing = calculate_bearing(car_first_coord, car_direction_coord)

topo = {"entity": [], "link": []}

# Entity
topo["entity"].extend(
    create_single_type_entity_list(
        cloud_server_count, 
        cloud_server_first_id, 
        cloud_server_first_coord, 
        cloud_server_bearing, 
        cloud_server_distance, 
        cloud_server_config
    )
)

topo["entity"].extend(
    create_single_type_entity_list(
        fog_server_count, 
        fog_server_first_id, 
        fog_server_first_coord, 
        fog_server_bearing, 
        fog_server_distance, 
        fog_server_config
    )
)

topo["entity"].extend(
    create_single_type_entity_list(
        car_count, 
        car_first_id, 
        car_first_coord, 
        car_bearing, 
        car_distance, 
        car_config
    )
)

# Link
# Cloud - Cloud
topo["link"].extend(
    create_cloud_server_link_list(
        cloud_server_count,
        cloud_server_first_id,
        cloud_server_BW,
        cloud_server_PR
    )
)
# Cloud - Fog
topo["link"].extend(
    create_cloud_fog_link_list(
        cloud_server_count,
        cloud_server_first_id,
        fog_server_count,
        fog_server_first_id,
        cloud_fog_BW,
        cloud_fog_PR
    )
)

# Fog - Fog
topo["link"].extend(
    create_fog_server_link_list(
        fog_server_count,
        fog_server_first_id,
        fog_server_BW,
        fog_server_PR
    )
)

with open(file_path, 'w') as outfile:
    json.dump(topo, outfile, indent=4)