#!/usr/bin/env python3

import threading
import cv2
import queue
import os
import time
import shutil

# filename of clip to load
filename = 'clip.mp4'
outDir = 'outputFrames' #directory to output frames that are captured and converted
vidCapture = cv2.VideoCapture(filename)
q1 = queue.Queue(10)
q2 = queue.Queue(10)
framDelay = 42

class ExtractFrames(threading.Thread):
	def __init__(self, semaphore1, semaphore2, lock1):
		super(ExtractFrames, self).__init__()
		self.sem1 = semaphore1 # semaphore for when queue is empty
		self.sem2 = semaphore2 # semaphore for when queue is full
		self.lock1 = lock1
	#create output directory if it doesn't exist
	if not os.path.exists(outDir):
		print("Output directory for frames, {}, created...".format(outDir))
		os.makedirs(outDir)

	def run(self):
		count = 0
		
		while True:
			success, image = vidCapture.read() #outputs tuple
			if success:
				cv2.imwrite("{}/frame_{:04d}.jpg".format(outDir, count), image) #write the image into the output directory
				print("Reading frame {}".format(count))
				self.sem2.acquire() 
				self.lock1.acquire()
				q1.put(image) #put image into queue
				self.lock1.release()
				self.sem1.release() 
				count += 1
			else:
				print("Export Complete!!!!!")
				break

class ConvertToGray(threading.Thread):
	def __init__(self,  semaphore1, semaphore2, semaphore3, semaphore4, lock1, lock2):
		super(ConvertToGray, self).__init__()
		self.sem1 = semaphore1 # semaphore for when queue is empty
		self.sem2 = semaphore2 # semaphore for when queue is full
		self.sem3 = semaphore3 # semaphore for when second queue is empty
		self.sem4 = semaphore4 # semaphore for when second queue is full
		self.lock1 = lock1
		self.lock2 = lock2 #mutexes
	def run(self):
		count = 0
		while True:
			self.sem1.acquire() 
			self.lock1.acquire()
			image = q1.get() #from the queue grab the next image
			self.lock1.release()
			self.sem2.release() 
			inFileName = "{}/frame_{:04d}.jpg".format(outDir, count)
			inputFrame = cv2.imread(inFileName, cv2.IMREAD_COLOR) #read the image

			if(inputFrame is not None):
				print("Converting frame {}".format(count))
				grayscaleFrame = cv2.cvtColor(inputFrame, cv2.COLOR_BGR2GRAY) #convert image to grayscale
				outFrameName = "{}/grayscale_{:04d}.jpg".format(outDir, count)
				self.sem4.acquire()
				self.lock2.acquire()
				q2.put(cv2.imwrite(outFrameName, grayscaleFrame)) #write and insert the grayscale image into the next queue
				self.lock2.release()
				self.sem3.release()
				if os.path.exists(inFileName): #delete the color image thats been converted from the output directory
					os.remove(inFileName)
				count += 1
				inFileName = "{}/grayscale_{:04d}.jpg".format(outDir, count) 
				success, jpgImage = cv2.imencode('.jpg', image) #encode the image
			
			if q1.empty(): # once queue one is empty break and should only be empty if done exporting thanks to semaphores
				break


class DisplayVideo(threading.Thread):
	def __init__(self,  semaphore3, semaphore4, lock2):
		super(DisplayVideo, self).__init__()
		self.sem3 = semaphore3 # semaphore for when second queue is empty
		self.sem4 = semaphore4 # semaphore for when second queue is full
		self.lock2 = lock2
	def run(self):
		count = 0
		while True:
			self.sem3.acquire() # prevents from taking from empty queue
			self.lock2.acquire()
			q2.get() #grab grayscale image/frame from second queue
			self.lock2.release()
			self.sem4.release()
			startTime = time.time() #timer for playing
			frameName = "{}/grayscale_{:04d}.jpg".format(outDir, count)
			frame = cv2.imread(frameName) #read the frame
			if frame is not None:
				print("Displaying frame {}".format(count))
				cv2.imshow(filename, frame) #display frame

				elapsedTime = int((time.time()-startTime) * 1000)
				print("Time to process frame is {}".format(elapsedTime)) #time elapsed for frame to be processed
				
				timeToWait = max(1, framDelay - elapsedTime) #amount of time to wait to quit
				count += 1

				if cv2.waitKey(timeToWait) and 0xFF == ord("q"): # allow users to quit during frame delay
					break

					startTime = time.time() # next frame time
					count += 1
					frameName = "{}/grayscale_{:04d}.jpg".format(outDir, count) # read next frame
					frame = cv2.imread(frameName)
					cv2.destroyAllWindows()
			if q2.empty(): # should never be empty unless we are done displaying thanks to semaphores
				try:
					shutil.rmtree.(outDir)
				except:
					print("could not remove directory outputFrames")

				print("Video is done playing...")
				cv2.destroyAllWindows() #closes video gui window 
				break

if __name__ == '__main__':

	semaphore1 = threading.Semaphore(0)
	semaphore2 = threading.Semaphore(10)
	semaphore3 = threading.Semaphore(0)
	semaphore4 = threading.Semaphore(10)
	lck1 = threading.Lock()
	lck2 = threading.Lock()

	extract = ExtractFrames(semaphore1, semaphore2, lck1)
	convert = ConvertToGray(semaphore1, semaphore2, semaphore3, semaphore4, lck1, lck2)
	video = DisplayVideo(semaphore3, semaphore4, lck2)

	extract.start()
	convert.start()
	video.start()
