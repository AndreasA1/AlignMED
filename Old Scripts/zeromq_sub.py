#
#   Weather update client
#   Connects SUB socket to tcp://localhost:5556
#   Collects weather updates and finds avg temp in zipcode
#

import sys
import zmq


#  Socket to talk to server
context = zmq.Context()
socket = context.socket(zmq.SUB)

print("Collecting updates from weather server...")
socket.connect("tcp://127.0.0.1:6000")

# Subscribe to zipcode, default is NYC, 10001
zip_filter = sys.argv[1] if len(sys.argv) > 1 else "10001"
socket.setsockopt_string(zmq.SUBSCRIBE, "cmd")

# Process 5 updates
total_temp = 0
update_nbr = 1
while True:
    string = socket.recv_string()
    print(string)
    cmd, zipcode, temperature, relhumidity = string.split()
    total_temp += int(temperature)

    print((f"Average temperature for zipcode " 
       f"'{zip_filter}' was {total_temp / (update_nbr+1)} F"))