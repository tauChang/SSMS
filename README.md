# So Simple Mobility Simulation (SSMS)
A simple implementation of simulation of vehicular network offloading using [YAFS](https://github.com/acsicuib/YAFS) .

## Running Simulation
Run the bash script `src/run.sh`. Please remember to change the path.

To deactivate offloading, please comment out line 580 and 581 in `src/yafs/core.py`.
To generate animation, please uncoment line 132 in `src/examples/SSMS/main.py`.

## Simulation Environment
There is 1 cloud server. Along the road, there are 10 fog servers sequentially, with a distance of 600 meters between one another. There are 10 vehicles driving north sequentially at a speed of 60 KM/hr, with a distance of 500 meters between one another. 

Each fog server is connected directly to the cloud server, and each fog server is connected to its adjacent neighbor (i.e., the second fog server is connected to the first and the third fog server). A vehicle will be connected to a fog server when it is in its network coverage, which is a circle coverage with a radius of 500 meters.
The simulation is conducted for 10 minutes (simulation time). A vehicle generates a task (message) every 100 ms.

A server (cloud and fog) adopts an offloading strategy. When number of tasks in the queue exceeds the offloading threshold, the tasks that arrived late would be offloaded to the closest (in network topology, not distance) fog server available. The offloading threshold is set to be 10.

## Results
There are 3 sets of results. 
* `src/examples/SSMS/exp/results_cloud_no_offloading` contains the result of a simulation environment where only the cloud server performs computation.
* `src/examples/SSMS/exp/results_fog_no_offloading` contains the result of a simulation environment where the cloud server and the 10 fog servers performs computation, and no offloading strategy is adopted.
* `src/examples/SSMS/exp/results_fog_offloading` contains the result of a simulation environment where the cloud server and the 10 fog servers performs computation, and offloading strategy is adopted.

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

### Offloading
* In `core.py`, the member function `__offload()` is added to support offloading, which is called in `__add_consumer_module()`.
* In `core.py`, the variable `OFFLOAD_METRIC` is added. This is used in `__update_node_metrics()` to determine the processing time of an offloaded message, which is 0.