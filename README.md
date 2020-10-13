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

## Changes Made to YAFS
To accomodate our implementation, we made some modification to the main source code of YAFS

### To ensure that the source topology ID that sends the Task is the one who receives the Result
* In `application.py`, the class `Message` is added a class attribue `result_receiver_topo_id` (in `__init__()`).
* In `core.py`, the member function `Sim.__add_source_population()` is added an argument `id_node`, which is set as `msg.result_receiver_topo_id`
* In `core.py`, the member function `Sim.__add_sink_module()` is added an argument `id_node`, to check whether the receiver is as specified in the received message. This is for debug purpose.
* In `core.py`, when the member function `Sim.__add_consumer_module()` is done "processing the input message", it copies the input message's `result_receiver_topo_id` to the output message, so as to inherit the result receiver.