# So Simple Mobility Simulation (SSMS)
A simple implementation of simulation of vehicular network offloading using [YAFS](https://github.com/acsicuib/YAFS) .


## Directory Structure
```js
SSMS
├── README.md
├── projects
│   └── strategy1
│       ├── README.md
│       ├── experiments
│       │   ├── __init__.py
│       │   └── exp1
│       │       ├── README.md
│       │       ├── config.json
│       │       ├── main.py
│       │       ├── run.sh
│       │       ├── appDefinition.json
│       │       ├── networkDefinition.json
│       │       ├── customPlacement.py
│       │       ├── customSelection.py
│       │       └── straightline_10cars
|       │               ├── result
|       │               │   ├── Results_one_0.csv
│       │               │   ├── Results_one_0_link.csv
│       │               │   ├── normalized_trajectories.csv
│       │               │   ├── snap_00000.png
│       │               │   └── (**omitted**)
│       │               └── trajectory
│       │                   ├── 10000.gpx
│       │                   └── (**omitted**)
│       ├── src
│       │   ├── README.md
│       │   ├── __init__.py
│       │   ├── logging.ini
│       │   ├── trackanimation
│       │   │   └── (**omitted**)
│       │   └── yafs
│       │       └── (**omitted**)
│       └── tools
│           ├── someCoolTools.py
│           └── (**omitted**)
└── template\ src
    ├── README.md
    ├── __init__.py
    ├── logging.ini
    ├── trackanimation
    │   ├── __init__.py
    │   ├── animation.py
    │   ├── animation_backup.py
    │   ├── animation_backup2.py
    │   ├── icon
    │   │   ├── car.png
    │   │   ├── car_endpoint.png
    │   │   └── endpoint.png
    │   ├── tracking.py
    │   └── utils.py
    └── yafs
        ├── __init__.py
        ├── action.py
        ├── application.py
        ├── core.py
        ├── coverage.py
        ├── customMovement.py
        ├── distribution.py
        ├── logging.ini
        ├── metrics.py
        ├── mobileEntity.py
        ├── placement.py
        ├── population.py
        ├── selection.py
        ├── stats.py
        ├── topology.py
        └── utils.py
```

* `SSMS/template src` contains the template source code with basic functionalities provided by YAFS and some modifications made by us. When the user is creating a new project, he/she could copy the content of this directory and place it at `SSMS/projects/myNewProject/src`. A README is provided as to introduce the modification and extension made by us.

* `SSMS/projects` contains subdirectories, where each subdirectory represents a **strategy**. A strategy is a method devised to optimize some goal (e.g. latency) under **non-specific** topology. For example, `SSMS/projects/offload to neighbor_no scheduling` could be a strategy of performing offloading only to its neighboring servers, and within a server, there is no scheduling of tasks. We recommmed to create a `README` for `SSMS/projects` to give a brief introduction on each subdirectory(strategy).

* `SSMS/projects/some_strategy` should contain
  * `README`: a file of detail description of this strategy
  * `src/`: a directory that contains the YAFS source code of performing simulation. A `README` should be created in this directory to specify what modifications are made.
  * `experiments/`: a directory that contains subdirectories, where each subdirectory represents a single experiment. We recommmed to create a `README` for `experiments/` to give a brief introduction on each subdirectory (experiment). Detail below.
  * `tools/`: a directory that contains tools (likely scripts) to create topologies, applications, gpx files etc.

* `SSMS/projects/some_strategy/experiments/exp1` represents a single experiment. All simulations ran under a single experiment should have be under the same
  * network definition "model name"
  * application
  * placment
  * population
  * selection
  * number of car trajectories
  
  whereas simulations ran under a single experiment could have different
  * network definition (as long as their "model name" is the same. So could actually have different number of servers and cars.)
  * types of car trajectories

  We recommend to create a `README` for a detailed description of this experiment.

## Possible Bugs Discovered in YAFS
* In `coverage.py`, the member function `CircleCoverage.__geodesic_point_buffer(self, lon, lat, km)` should be `CircleCoverage.__geodesic_point_buffer(self, lat, lon, km)`.

