# hexlet-servers

demo https://www.youtube.com/watch?v=0_0UvTdsnRA

# Usage
The client will expect the first server to listen on port 50000, the second server on port 50001, the third on 50002 and so on.
On client startup, the servers should be already listening.

### start servers
python server.py <port> <cores>

port: the port where the server should listen.
cores (int [1..100]): the number of simulated cores; the higher the number the faster the server computes.

### start client
python client.py <servers_count>
servers_count: int, >1, whatever you like, but you should have the same amount of servers listening.

### assign tasks
once started, the client will connect to servers and prompt to enter a command.
the command has the following syntax:
<story_points(int[1..100])> <description(string)>
story points: the task complexity
description: any string, but not an empty string, and it will be considered until \r, \n

Each task will be forwarded to the server with the lowest load.


