# Projects
## `offload neighbor_no scheduling`
* Each server performs offloading, but does not perform in-server task-scheduling.
* The offload threshold is 10. (explained below)
* We define a server's **loading** as the number of tasks waiting in its queue.
* Suppose a server has id 10003. Upon receiving a task request, it first checks its loading is <= 10. If so, it queues the task to compute by itself. If not, it inspects the loading of servers with ids 10002 and 10004, and offload this task to the server with less loading. 
* If a server only has one neighbor, it only inpsects that neighbor.

