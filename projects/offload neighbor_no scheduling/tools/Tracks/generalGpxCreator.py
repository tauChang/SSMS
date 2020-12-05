"""
This script is tested and ran only using Python 3.7.9 on MacOS.
"""

from lxml import etree
from datetime import datetime, timedelta
import math
import geopy
import geopy.distance
from coordinateToolkit import *

class Track:
    def __init__(self,
        start_time = datetime.now(),
        start_coord = {"lat": 0.0, "lng": 0.0},
        trkpt_time_interval = 1,
        moving_speed=60,
        instructions=[]):
        """
        args:
            - start_time: A `datetime.datetime` object. The starting time of the track. Default to be datetime.now().
            - end_time: A `datetime.datetime` object. The ending time of the track. Default to be datetime.now().
            - start_coord: A dictionary with keys "lat" and "lng". The coordinate of the starting point of the track. Default to be {"lat": 25.0167, "lng": 121.5333}, which is the coordinate of National Taiwan University.
            - trkpt_time_interval: An integer. The time interval between each track points in seconds. Default to be 60 (sec).
            - moving_speed: A float. The moving speed of the entity in kilometer per hour. Default to be 60 km/h.
            - instructions: An array. [(bearing, distance)]
        """
        self.start_time = start_time
        self.trkpt_time_interval = trkpt_time_interval
        self.start_coord = start_coord
        self.moving_speed = moving_speed
        self.instructions = instructions

    def get_next_coord(self, cur_coord, time_interval, bearing):
        """
            Returns a dictionary (lng, lat) which is the coordinate of next point of the track.
        """
        dist = geopy.distance.distance(kilometers=self.moving_speed / 3600 * time_interval)
        origin = geopy.Point(cur_coord["lat"], cur_coord["lng"])
        next_coord = dist.destination(point=origin, bearing=bearing) 
        return {"lat": next_coord[0], "lng": next_coord[1]}
    
    def create_trkpt_tag(self, coord, ele=0.0, time=datetime.now()):
        """
            Creates a trkpt tag.
            Args:
                - coord: A dictionary containing key "lng" and "lat". The coordinate of this trkpt.
                - ele: A float. The elevation of this trkpt.
                - time: A `datetime.datetime` object. The time of this trkpt.
        """
        trkpt_parent_tag = etree.Element("trkpt", lat=str(coord["lat"]), lon=str(coord["lng"]))
        ele_child_tag = etree.Element("ele")
        ele_child_tag.text = str(ele)
        time_child_tag = etree.Element("time")
        time_child_tag.text = time.strftime('%Y-%m-%dT%H:%M:%SZ')
        trkpt_parent_tag.append(ele_child_tag)
        trkpt_parent_tag.append(time_child_tag)

        return trkpt_parent_tag
    
    def create_gpx_by_instructions(self, gpx_tag_attribute = {"creator" : "CPS Lab"}):
        # Setup gpx xml tag
        gpx_tag = etree.Element("gpx", gpx_tag_attribute)
        gpx_tag.append(etree.Element("trk"))
        trkseg_tag = etree.Element("trkseg")

        # Get initial gpx time and coordinate
        cur_time = self.start_time
        cur_coord = self.start_coord

        # Calculate moving distance in an interval
        distance_move_interval = self.trkpt_time_interval * (self.moving_speed / 3600)
        for instruction in self.instructions:
            bearing = instruction[0]
            distance = instruction[1]
            while distance > 0:
                trkpt_tag = self.create_trkpt_tag(coord=cur_coord, ele=0.0, time=cur_time)
                trkseg_tag.append(trkpt_tag)
                cur_coord = self.get_next_coord(cur_coord=cur_coord, time_interval=self.trkpt_time_interval, bearing=bearing)
                print(cur_coord)
                cur_time += timedelta(seconds = self.trkpt_time_interval)
                distance -= distance_move_interval

        gpx_tag.getchildren()[0].append(trkseg_tag)

        return gpx_tag


def point2coord(point):
    # This function transfers point (x, y) to (latitude, longitude).
    # Started from (lat, lng) = (0, 0), go x km along west/east and go y km along north/south.
    x = point[0]
    y = point[1]
    horizontal_bearing = calculate_bearing((0, 0), (x, 0))
    horizontal_dist = geopy.distance.distance(kilometers=x) 
    vertical_bearing = calculate_bearing((0, 0), (0, y))
    vertical_dist = geopy.distance.distance(kilometers=y)
    tmp_coord = horizontal_dist.destination(point=geopy.Point(0, 0), bearing=horizontal_bearing)
    coord = vertical_dist.destination(point=geopy.Point(tmp_coord[0], tmp_coord[1]), bearing=vertical_bearing)
    return {"lng": coord[0], "lat": coord[1]}


'''
    How to use?
    Given input below, this script will generate a gpx file.
    The gpx files can be repeatedly used in any experiment once it was generated.
    
    TODO:
        - Define a higher level config to set the parameters.
        - Now the path is hardcoded! Should not be like this!
''' 

# User input -----------------------------------------------------
start_time = datetime(2020, 10, 10, 10, 0, 0)
start_coord = point2coord((3.5, 5)) # (x, y): From the oirgin, move x km horizontally, and move y km vertically.
instructions = [(180, 1.5), (270, 1.5), (180, 1), (270, 2)] # [(bearing, distance)]
moving_speed = 50 # km/h
gpx_tag_attribute = {}
track_name = 'track6'
directory_path = "./tracks/general_20201205/"
# User input end -------------------------------------------------

t = Track(
    start_time=start_time,
    start_coord=start_coord,
    trkpt_time_interval=1, # seconds
    moving_speed=moving_speed, # km/h
    instructions=instructions
)

gpx = t.create_gpx_by_instructions(gpx_tag_attribute=gpx_tag_attribute)
file_name = directory_path + track_name + '.gpx'
with open(file_name, "w") as f:
    f.write(etree.tostring(gpx, pretty_print=True, encoding="unicode"))



