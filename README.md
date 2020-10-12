# So Simple Mobility Simulation (SSMS)
A simple implementation of simulation of vehicular network offloading using [YAFS](https://github.com/acsicuib/YAFS) .

## Running Simulation

## Simulation Environment

## Results

## Tracks
GPX tracks of vehicles are generated using the python script `src/examples/SSMS/gpxCreator.py`, and the created gpx files are located in the directory `src/examples/SSMS/Tracks`. 

10 vehicles move along **a straight path** sequentially, with the car distance being 0.5 kilometers. The vehicles all move at the speed of 60 kilometer per hour. The gpx tracks record the track points within an 10-minute-period (all gpx tracks have the identical starting time, ending time and time interval).

## Possible Bugs Discovered in YAFS
* In `coverage.py`, the member function `CircleCoverage.__geodesic_point_buffer(self, lon, lat, km)` should be `CircleCoverage.__geodesic_point_buffer(self, lat, lon, km)`.