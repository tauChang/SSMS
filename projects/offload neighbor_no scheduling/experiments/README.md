# Experiments
## `exp_kongo`
### Network Definition (Topology)
* Possible entities:
    * cloud server
    * fog server
    * car

### Application
Source --(Task)--> [ Reception --(Task)--> Computation ] --(Result)--> Actuator

### Placement
* A car contains two modules: Source and Actuator
* A server (fog or edge) contains two modules: Reception and Computation

### Selection
* Shortest path. Provided by networkx


