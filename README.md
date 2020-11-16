# So Simple Mobility Simulation (SSMS)
A simple implementation of simulation of vehicular network offloading using [YAFS](https://github.com/acsicuib/YAFS) .

## Running Simulation
Run the bash script `src/run.sh`. Please remember to change the path.

To deactivate offloading, please comment out line 580 and 581 in `src/yafs/core.py`.
To generate animation, please uncoment line 132 in `src/examples/SSMS/main.py`.

## Simulation Environment
![Network Diagram](src/examples/SSMS/Topology%20Diagram.png)

There is 1 cloud server. Along the road, there are 10 fog servers sequentially, with a distance of 600 meters between one another. There are 10 vehicles driving north sequentially at a speed of 60 KM/hr, with a distance of 500 meters between one another. 

Each fog server is connected directly to the cloud server, and each fog server is connected to its adjacent neighbor (i.e., the second fog server is connected to the first and the third fog server). A vehicle will be connected to a fog server when it is in its network coverage, which is a circle coverage with a radius of 500 meters.
The simulation is conducted for 10 minutes (simulation time). A vehicle generates a task (message) every 100 ms.

A server (cloud and fog) adopts an offloading strategy. When number of tasks in the queue exceeds the offloading threshold, the tasks that arrived late would be offloaded to the closest (in network topology, not distance) fog server available. The offloading threshold is set to be 10.

Detailed configuration are listed below (Note: Memory size of devices is not considered in SSMS).

* Device

Device Type | MIPS | Computation Time of Task (ms)
----------- | ---: | -----------------------:
cloud-server| 2000 | 25 (=50 / 2000)
fog-server  | 800  | 62.5 (=50 / 800)

Note: Computation time of task is calculated as (`Task` Size) divided by (Device Computing Power)

* Link

End Point 1 | End Point 2 | Bandwidth (Mbpms) | Propagation Delay (ms)
----------- | ----------- | ----------------: | ---------------------:
cloud-server| fog-server  | 1 | 15
fog-server  | car         | 10 | 10

Note: This configuration may be somehow unrealistic. The bandwidth of link between `fog-server` and `car` and that between `cloud-server` and `fog-server` should not differ by that much?

* Message

Message Type | Million Instructions | Size (Mbits)
------------ | -------------------: | -----------:
Task | 50 | 150
Result | 10 (Not processed) | 50


## Application Model
![Application Model](https://i.ibb.co/ZGXqC7S/application-model.png)

There are three modules: `Source`, `Computation`, and `Actuator`. `Source` generates messages of type `Task`, which is then received by `Computation` to perform computing. `Computation` then sends messages of type `Result` to `Actuator`.

`Source` and `Actuator` are placed on the device type `car`. `Computation` are placed on the device type `cloud-server` and `fog-server`.

## Results
There are 3 sets of results. 
* `src/examples/SSMS/exp/results_cloud_no_offloading` contains the result of a simulation environment where only the cloud server performs computation.
* `src/examples/SSMS/exp/results_fog_no_offloading` contains the result of a simulation environment where the cloud server and the 10 fog servers performs computation, and no offloading strategy is adopted.
* `src/examples/SSMS/exp/results_fog_offloading` contains the result of a simulation environment where the cloud server and the 10 fog servers performs computation, and offloading strategy is adopted.
* Summary

Environment |  Average Latency (ms) | Worst-case Latency (ms) | Latency Standard Deviation (ms) | Number of `Task`s Completed 
------------| ---------------------:| -----------------------:| ------------------------------: | -------------------------:
Fog Offloading | 281 | 770 | 274 | 37706
Fog No Offloading | 775 | 4620 | 1030 | 37409
Cloud No Offloading | 75335 | 260350 | 69196 | 18532
Fog Offload to Front | 331 | 772 |  296 | 33216


## Tracks
GPX tracks of vehicles are generated using the python script `src/examples/SSMS/gpxCreator.py`, and the created gpx files are located in the directory `src/examples/SSMS/Tracks`. 

10 vehicles move along **a straight path** sequentially, with the car distance being 0.5 kilometers. The vehicles all move at the speed of 60 kilometer per hour. The gpx tracks record the track points within an 10-minute-period and with a time interval of 1 second (all gpx tracks have the identical starting time, ending time and time interval).

#### 2020/11/11 Edited by Goodhat
A new directory `Tracks` is established. 
There are two new scripts:
- `generalGpxCreator.py`
  - This script can generate .gpx files that can be used repeatedly in the later experiments.
  -  The setting of parameters is directly in the script. **(TODO: Probably should have a higher level config.)**
  -  Run `python3 generalTrackCreator.py` to generate a gpx file. The file will be save in another subdirectory called `tracks`.

- `expGpxCreator.py`
  - This script extends one .gpx file into a set of .gpx files, in order to generate multiple vehicles in experiments.
  - The setting of parameters is directly in the script. **(TODO: Probably should have a higher level config.)**
  - The script will create a directory with suffix `_sets`, and save the generated files in it.
  - The script will also record the config info in `gpx_config.json` in the same directory.

**Example**:
If we generated a gpx file with `generalGpxCreator.py` called `ladder.gpx`, and then extend it by `expGpxCreator.py`, the file structure in `Tracks` will be like:

```js
Tracks                                  
├─ ladder_sets                          
│  ├─ gpx_config.json                   
│  ├─ ladder_0.gpx                      
│  ├─ ladder_1.gpx                      
│  ├─ ladder_2.gpx
│  └─  ...            
├─ tracks                               
│  └─ ladder.gpx                        
├─ coordinateToolkit.py                 
├─ expGpxCreator.py                     
└─ generalGpxCreator.py                 
```

⚠️ Note that the path parameters in the scripts are all hardcoded. Scripts will only run correctly in the directory.  
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
