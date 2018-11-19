# Producer Consumer Lab

For this lab we are asked to implement a trivial producer-consumer system using
python threads where all coordination is managed by counting and binary
semaphores for a system of two producers and two consumers. The producers and
consumers form a simple rendering pipeline using multiple threads. One
thread reads frames from a file, a second thread takes those frames
and converts them to grayscale, and the third thread displays those
frames. The threads run concurrently.

## prodCon.py
* Extracts frames from a video file, convert them to grayscale, and display
them in sequence
* has three functions
  * One function to extract the frames named ExtractFrames
  * One function to convert the frames to grayscale named ConvertToGray
  * One function to display the frames at the original framerate (24fps) name DisplayVideo
* The functions each execute within their own python thread
  * The threads execute concurrently
  * The order threads execute in may not be the same from run to run
* Threads signal that they have completed their task
* Threads process all frames of the video exactly once
* Frames are communicated between threads using producer/consumer idioms
  * Producer/consumer quesues are bounded at ten frames



