import math
import geopy
import geopy.distance

def calculate_bearing(pointA, pointB):
    """
    Credit: https://gist.github.com/jeromer/2005586

    Calculates the bearing between two points.
    The formulae used is the following:
        θ = atan2(sin(Δlong).cos(lat2),
                  cos(lat1).sin(lat2) − sin(lat1).cos(lat2).cos(Δlong))
    :Parameters:
      - `pointA: The tuple representing the latitude/longitude for the
        first point. Latitude and longitude must be in decimal degrees
      - `pointB: The tuple representing the latitude/longitude for the
        second point. Latitude and longitude must be in decimal degrees
    :Returns:
      The bearing in degrees
    :Returns Type:
      float
    """
    if (type(pointA) not in [tuple, geopy.point.Point]) or (type(pointB) not in [tuple, geopy.point.Point]):
        raise TypeError("Only tuples and geopy.point.Point are supported as arguments")

    lat1 = math.radians(pointA[0])
    lat2 = math.radians(pointB[0])

    diffLong = math.radians(pointB[1] - pointA[1])

    x = math.sin(diffLong) * math.cos(lat2)
    y = math.cos(lat1) * math.sin(lat2) - (math.sin(lat1)
            * math.cos(lat2) * math.cos(diffLong))

    initial_bearing = math.atan2(x, y)

    # Now we have the initial bearing but math.atan2 return values
    # from -180° to + 180° which is not what we want for a compass bearing
    # The solution is to normalize the initial bearing as shown below
    initial_bearing = math.degrees(initial_bearing)
    compass_bearing = (initial_bearing + 360) % 360

    return compass_bearing

def calculate_distance(pointA, pointB):
    """
    Return distance between two coordinate points. The distance is in kilometer.
    pointA and pointB should be tuple of format (lat, lng)
    """
    if (type(pointA) not in [tuple, geopy.point.Point]) or (type(pointB) not in [tuple, geopy.point.Point]):
        raise TypeError("Only tuples and geopy.point.Point are supported as arguments")

    return geopy.distance.distance(pointA, pointB).km

def get_next_coordinate(origin, distance, bearing):
    """
    Get the point (a geopy.point.Point) which is bearing and distance from the origin.
    distance is in kilometer.
    """
    if type(origin) not in [tuple, geopy.point.Point]:
        raise TypeError("Only tuples and geopy.point.Point are supported as arguments")
    
    dist = geopy.distance.distance(kilometers=distance)
    return dist.destination(point=origin, bearing=bearing) 