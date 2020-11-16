import gpxpy
import gpxpy.gpx
import random
from lxml import etree
from datetime import datetime, timedelta
import math
import geopy
import geopy.distance
from coordinateToolkit import *
import os
import json

# User input -----------------------------------------------------
track_name = 'ladder'
track_path = './tracks/' + track_name + '.gpx'
target_path = "./" + track_name + '_sets/'
simulation_total_time = 1000
interval_padding = 10
distribution = random.expovariate
mean = 0.05
start_time = datetime(2020, 10, 10, 10, 0, 0)
# User input end -------------------------------------------------

# Some constants ----------------
FORSAKEN_LAT = 89.0
FORSAKEN_LON = -179.0
# Some constants end ----------------


'''
    Note:
        Read the .gpx file which contains the track points.
    What we get:
        - track:
            It is a datatype defined by gpxpy. You can get the data directly.
            More information in https://pypi.org/project/gpxpy/.
        - track_length:
            The length of the track.
'''
gpx_file = open(track_path, 'r')
gpx = gpxpy.parse(gpx_file)
track = gpx.tracks[0].segments[0].points
track_length = len(track)
print('track_length: ', track_length)

'''
    Note:
        Calculate the occurence time of every vehicle
    What we get:
        - vehicle_occur_time:
            This is an array of integers which indicate the occurence time of every vehicle.
'''
vehicle_occur_time = []
current_time = 0
while current_time < simulation_total_time:
    vehicle_occur_time.append(current_time)
    current_time += round(distribution(mean))

'''
    Note:
        !! This part may be a little confusing. More explanation should be provided. !!

        In order to generate valid gpx, we have to separate vehicle occur time to serveral arrays,
        since an individual .gpx file can only represents one vehicle at a time.
        However, we can reduce the number of .gpx files by putting non-overlapping vehicles into the same .gpx file.
        This is why we need 'interval_padding'. It provides a short period of time to cool down. After the cool down,
        we start a new track from the start again.
        (Note that this separating algorithm may not optimized.)
    What we get:
        - vehicle_occur_time_each_gpx:
            This is a two dimensional array of integers. Each array in it represents a gpx file that we are going to produce.
'''
vehicle_occur_time_each_gpx = []
while len(vehicle_occur_time):
    # Reset the list, and insert the current first element
    tmp_occur_time = []
    tmp_occur_time.append(vehicle_occur_time.pop(0))
    for i, t in enumerate(vehicle_occur_time):
        if t > tmp_occur_time[-1] + track_length + interval_padding:
            tmp_occur_time.append(vehicle_occur_time.pop(i))
    vehicle_occur_time_each_gpx.append(tmp_occur_time)

print('track_length + padding:', track_length + interval_padding)
print(len(vehicle_occur_time_each_gpx), vehicle_occur_time_each_gpx)


'''
    Note:
        Based on 'vehicle_occur_time_each_gpx', generate an array of gpx and save it to the specified path.
    What we get:
        - gpxs: 
'''
gpxs = []
for occur_times in vehicle_occur_time_each_gpx:
    gpx_tag = etree.Element("gpx")
    gpx_tag.append(etree.Element("trk"))
    trkseg_tag = etree.Element("trkseg")
    origin_datetime = start_time
    cur_time = 0
    cur_index = 0 # This records the index of occur_times
    while cur_time < simulation_total_time:
        cur_datetime = origin_datetime + timedelta(seconds=cur_time)
        lat = FORSAKEN_LAT
        lon = FORSAKEN_LON
        # If cur_index >= len(occur_times), it means the rest of the track point should be (0,0)
        if cur_index < len(occur_times):
            time_shift = cur_time - occur_times[cur_index]
            # If the time shift is in range of track length, set lat and lon.
            if time_shift >= 0 and time_shift < track_length:
                lat = track[time_shift].latitude
                lon = track[time_shift].longitude
            if time_shift >= track_length:
                cur_index += 1

        # Having lat and lon, generate xml tag and push it into record.
        trkpt_parent_tag = etree.Element("trkpt", lat=str(lat), lon=str(lon))
        ele_child_tag = etree.Element("ele")
        ele_child_tag.text = str(0.0)
        time_child_tag = etree.Element("time")
        time_child_tag.text = cur_datetime.strftime('%Y-%m-%dT%H:%M:%SZ')
        trkpt_parent_tag.append(ele_child_tag)
        trkpt_parent_tag.append(time_child_tag)
        trkseg_tag.append(trkpt_parent_tag)
        cur_time += 1

    gpx_tag.getchildren()[0].append(trkseg_tag)
    gpxs.append(gpx_tag)


'''
    Writing to files.
'''
if not os.path.exists(os.path.dirname(target_path)):
    try:
        os.makedirs(os.path.dirname(target_path))
    except OSError as exc: # Guard against race condition
        if exc.errno != errno.EEXIST:
            raise
for i, gpx in enumerate(gpxs):
    file_name = target_path + track_name + '_' + str(i) + '.gpx'
    with open(file_name, 'w') as f:
        f.write(etree.tostring(gpx, pretty_print=True, encoding="unicode"))


# Store the information of this gpx set in json form, and save it to the same path as .gpx files.
config = {}
config['track_name'] = track_name
config['simulation_total_time'] = 10000
config['interval_padding'] = 10
config['distribution'] = 'random.expovariate, mean=0.05'
with open(target_path + 'gpx_config.json', 'w') as f:
    f.write(json.dumps(config))


