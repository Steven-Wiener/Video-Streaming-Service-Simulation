# Video Streaming Service Simulation
Simulating a client requesting a "movie" from multiple servers.\
For this program, there are three main files: a client with two variations (`GreenClient.py`, `GreenClientScenarioF.py`) and server (`GreenServer.py`), running on five different hosts - one for client and four to simulate four separate servers.

## Getting Started
1. Run `moviegenerator.py` on desired server(s).
  - Modify `GreenClient.py` to reflect the server IP(s) (in our case the VMs had the IPs listed in variables `serverName1-4` in `GreenClient.py`). This will create a `movie.txt` file that serves as our sample movie. _This scripting is more efficient than copying a text file to every server._
2. Run `GreenServer.py` on desired server(s).
3. Run `GreenClient.py` (or `GreenClientScenarioF.py`) on client host.

### Client Code Differences
`GreenClient.py` was used to simulate several different scenarios, such as one or several servers lagging (i.e. high RTT) or shutting down completely during the simulation. This leads to the code adapting to accomidate several cases, listed below.\
`GreenClientScenarioF.py` includes added functionality for simulating rewind/pause/fast-forward at specific frames during the simulation.\
`perfeval.py` contains several functions for evaluating the various scenarios described previously.

## Code Breakdown
### Initialization
To begin the movie streaming service, start by filling the frame buffer before displaying the first frame. Request each packet from a server at random, and if a packet is lost - simply request it again.

### Bookkeeping Arrays & Timeout
For congestion detection and request logic we keep track of several things: packet request time, packet receive time, server requested from, number of packets received from each server, and packet dropped by each server. The packet request and receive time is used to calculate the RTT for a given packet. Individual RTTs (or the RTT for individual packets) are used for calculating cumulative average RTT and the average RTT of the last 15 packets received. The cumulative average RTT and RTT of the last 15 packets received are used later to set parameters in the request logic.\
Packets dropped by each server are used for congestion detection. These packets are not necessarily lost, as they could be considered as dropped if they are not received in a reasonable timeframe relative to the RTT.\
RTT and packet dropped are used together to provide information about server performance (congestion on links). From the RTT and packets dropped we are able to make a classification on the performance of a server. Server performance is defined in our algorithm as 1/[last 15 packets' average RTT + (number of packets dropped * by fraction)]. Since the number of packets is an integer value and the average RTT is measured in seconds (usually less than 1), we multiply the packets dropped by a fraction so that it does not  dominate the performance value. To determine if a server is congested, we take the performance value described above and compare it with the mean performance of all the servers subtracted by the standard deviation of the performance across all four servers. If a server's performance value is less than a standard deviation away from the mean performance value, then it is seen as congested. The servers are divided into 2 lists based on their performance value (A 'good' list and a 'bad' list). Future packets are then less likely to be requested from servers on the 'bad' list.\
In order to refresh each server's performance, we decided to use a timeout mechanism. When the timeout is reached, we utilize a method that reduces the immediate RTT of every server to ¾ the mean RTT value and then put every server back on to the 'good' list.

### Request Logic
The main intelligence of our algorithm resides in the requesting logic. We divide this logic into 5 cases below. Cases 1 and 2 deal with frames in the range of the frame buffer. Cases 3 and 4 deal with frames outside of the frame buffer's range but that will need to be displayed within the RTT. Case 5 is for requesting frames needed later than RTT, but will be able to be put into the frame buffer by the time the frames are received. Ideally, requests should only come from Case 5.
![Alt text](./cases.PNG?raw=true "Cases")
- Case 1: When a frame in the frame buffer has not yet been requested yet, add frame to the request queue.
- Case 2: When a frame in the buffer has been requested and it was requested a reasonably long time ago with respect to RTT and has not been received, make a new request for that frame. A reasonably long time is currently set to be the maximum of 1.4 times the server's average RTT and 1.4 times the immediate RTT of the server.
- Case 3: Similar to case 1, this is for requesting frames that haven't yet been requested but will be needed in RTT.
- Case 4: Similar to case 2,  this is for requesting frames that were requested long ago and not received and are needed in RTT but outside of the frame buffer's range.
- Case 5: Used to request unrequested frames outside of the range of case 3 and 4, but can be put into the frame buffer by the time they will be received.

### Issues
Our requesting logic performs very well when testing with short movie length. However, a problem occurs in longer movie length test cases. The boundary of the cases mentioned above are based on some variations of RTT. theoretically, no out-of-bound frames should be received. In reality, there's a very small chance that out-of-bound frames can be received. Since running longer movie length tests was difficult due to time constraints, the algorithm was tested with shorter movie lengths. Thus, the increased probability of out-of-bound frames with longer movie lengths was not realized until later. The main problem with receiving an out-of-bound frame is that when one out-of-bound frame is received (usually just barely out of bound, i.e. frame 33), the packet has to be discarded and re-requested. When the new request happens, the frame is needed in 32*10ms which is much shorter than the RTT. Our algorithm waits for the frame to be received and displayed before allowing later frames to be added to the buffer. This creates a butterfly effect. One frame dropped leads to several frames that were timed to be received and put into the framebuffer being dropped while waiting for the initial dropped frame to be received. More and more frames are dropped and results in a longer waiting time between each frame displayed.

### Attempted Solutions
Our first solution was to decrease the range of frames requested ahead of time. This did solve the issue of out-of-bound frames, but it created a new problem of not requesting frames early enough. In the changing network environment the RTT may fluctuate, so to eliminate the problem by decreasing the range of frames requested resulted in not requesting frames far enough ahead of time occasionally. If the constraints for requesting frames is too harsh, i.e., to completely eliminate the possibility of receiving out of bound frame , some frames will not be received in time and the resulting movie will display slower (longer pauses between frames). On the other hand, if the constraints are too loose then there will still be chance of requesting out-of-bound frames. Even if the probability is small enough that only 1 or 2 out-of-bound frames occur out of 30000 frames, this can still set of the aforementioned butterfly effect.\
Our second solution was to allow the occasional out-of-bound frame, but try to eliminate the chain effect it causes. When an out-of-bound frame occurs, we first calculate how far away from the frame buffer is (for example, 34-32 results in a distance of 2 frames). Next, calculate how much wait time is needed between the dropped frame's supposed display time and when it was actually received. Using this information (for example, if RTT is 600 and the distance is 2, the wait time would be around 600-(2+32)*10ms), we calculate the frames that will not be able to fit into the frame buffer that would otherwise have fitted,  and stop the request for frames in that range for a amount time equal to the wait time. This solution helped to an extent, but didn't completely remove the problem.

### Conclusion
Overall, our algorithm is able to play movies of short length with a 20 ms delay between each frame. This hinges on initializing our buffer, our server performance calculation to determine the best server(s) to request from, and then utilizing our 5 cases to request the correct frames in the correct order. The factors such as those used to calculate the performance of each server and the factor used to calculate a 'reasonable' length of time in our test cases were estimated from the short tests we ran with our algorithm. More testing with both long and short length movies could have resulted in different, more efficient factors.

### Post-Submission Conclusion
Upon reviewing other team projects, it was found that one team had success in requesting packets that may have been previously requested, if only to receive them more quickly from a server operating more efficiently. Our team originally thought this would cause the server to do too much work, but in the simulated case where four servers are serving one client, this may be more optimal.\
Additionally, the same team had success in implementing a round-robin approach, where every fourth frame was requested from every fourth server, ending requests altogether from servers which performed slowly, reducing requests to every third server and so on. Again, while the team performed better in the sample scenario, this does not accomidate a real-life scenario where a server may be underperforming for a short duration.

### Prerequisites
- [Python](https://www.python.org/downloads/)

### Authors: Audrey Gu, Tim Fronsee, Steven Wiener
### Purpose: ECE537 - Communication Networks
### Created: 05.17.19