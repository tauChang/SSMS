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
    def __init__(self, start_time = datetime.now(), end_time = datetime.now(), start_coord = {"lat": 25.0167, "lng": 121.5333}, direction_coord = {"lat": 25.0167, "lng": 121.5333}, trkpt_time_interval = 60, moving_speed=60, bearing=None):
        """
        Note:
            - If direction_coord is not provided, bearing must be provided.
            - If direction_coord is provided, bearing is ignored. 
        args:
            - start_time: A `datetime.datetime` object. The starting time of the track. Default to be datetime.now().
            - end_time: A `datetime.datetime` object. The ending time of the track. Default to be datetime.now().
            - start_coord: A dictionary with keys "lat" and "lng". The coordinate of the starting point of the track. Default to be {"lat": 25.0167, "lng": 121.5333}, which is the coordinate of National Taiwan University.
            - direction_coord: A dictionary with keys "lat" and "lng". The coordinate of the direction the entity is moving to along the track. Default to be {"lat": 25.0167, "lng": 121.5333}, which is the coordinate of National Taiwan University.
            - trkpt_time_interval: An integer. The time interval between each track points in seconds. Default to be 60 (sec).
            - moving_speed: A float. The moving speed of the entity in kilometer per hour. Default to be 60 km/h.
            - bearing: A float. The bearing of the moving entity. Default to be None. If not supplied, the bearing of the entity will be calculated from start_coord and direction_coord.
        """
        self.start_time = start_time
        self.end_time = end_time
        self.trkpt_time_interval = trkpt_time_interval
        self.start_coord = start_coord
        self.direction_coord = direction_coord
        self.moving_speed = moving_speed
        
        if direction_coord == None:
            self.bearing = bearing
        else:
            self.bearing = calculate_bearing(
                (start_coord["lat"], start_coord["lng"]), 
                (direction_coord["lat"], direction_coord["lng"])
            )

    def get_next_coord(self, cur_coord, time_interval):
        """
            Returns a dictionary (lng, lat) which is the coordinate of next point of the track.
        """
        # The following commented out section should be used if we hope the last trkpt recorded is definitely direction_coord
        #if(self.direction_coord != None):
        #    time_to_arrival = geopy.distance.distance(cur_coord, self.direction_coord).km / self.moving_speed * 3600
        #    time_interval = min(time_to_arrival, self.trkpt_time_interval)
        dist = geopy.distance.distance(kilometers=self.moving_speed / 3600 * time_interval)
        origin = geopy.Point(cur_coord["lat"], cur_coord["lng"])
        next_coord = dist.destination(point=origin, bearing=self.bearing) 

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
    
    def create_gpx(self, gpx_tag_attribute = {"creator" : "CPS Lab"}):
        """
            Generates a gpx-formatted string based on the specified class instances.
            Returns a etree.Element, which is the root tag of the gpx.
            
            args:
                root_tag_attribute: A dictionary. The attributes in the root gpx tag. Default to contain "CPS Lab" as the creator attribute.
        """
        gpx_tag = etree.Element("gpx", gpx_tag_attribute)
        gpx_tag.append(etree.Element("trk"))
        cur_time = self.start_time
        cur_coord = self.start_coord

        trkseg_tag = etree.Element("trkseg")
        while(cur_time <= self.end_time):
            trkpt_tag = self.create_trkpt_tag(coord=cur_coord, ele=0.0, time=cur_time)
            trkseg_tag.append(trkpt_tag)

            cur_coord = self.get_next_coord(cur_coord=cur_coord, time_interval=self.trkpt_time_interval)
            cur_time += timedelta(seconds = self.trkpt_time_interval)
        
        gpx_tag.getchildren()[0].append(trkseg_tag)

        return gpx_tag

# User input -----------------------------------------------------
car_count = 10
start_time = datetime(2020, 10, 10, 10, 0, 0)
end_time = datetime(2020, 10, 10, 10, 10, 0)
first_car_start_coord = {"lat": 24, "lng": 121}
direction_coord = {"lat": 25, "lng": 121}
trkpt_time_interval=1 # seconds
moving_speed=60 # km/h
car_distance = 0.5 # km
gpx_tag_attribute = {}
directory_path = "/Users/TommyChang/Desktop/So Simple Mobility Simulation/src/examples/SSMS/exp/trajectories/"  # will be appended with _0.gpx, _1.gpx, ...
first_car_id = 10000 # Will be used as the file name. The second car will be first_car_id + 1, etc.

# User input end -------------------------------------------------

gpx_list = []
bearing = calculate_bearing(
    (direction_coord["lat"], direction_coord["lng"]),
    (first_car_start_coord["lat"], first_car_start_coord["lng"])
    )

for i in range(0, car_count):
    dist = geopy.distance.distance(kilometers=car_distance * i) 
    
    coord = dist.destination(
        point=geopy.Point(first_car_start_coord["lat"], first_car_start_coord["lng"]), 
        bearing=bearing)
    print(coord)
    start_coord = {"lat": coord[0], "lng": coord[1]}
    
    t = Track(
        start_time=start_time,
        end_time=end_time,
        start_coord=start_coord,
        direction_coord=direction_coord,
        trkpt_time_interval=trkpt_time_interval, # seconds
        moving_speed=moving_speed, # km/h
        bearing=None
    )

    gpx_list.append(t.create_gpx(gpx_tag_attribute=gpx_tag_attribute))


for i in range(0, car_count):
    file_name = directory_path + "/%d.gpx" %(first_car_id + i) 
    f = open(file_name, "w")
    f.write(etree.tostring(gpx_list[i], pretty_print=True, encoding="unicode"))
    f.close()


