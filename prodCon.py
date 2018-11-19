#!/usr/bin/env python3

import threading
import cv2
import queue
import os
import time
import random

# filename of clip to load
filename = 'clip.mp4'
outDir = 'outputFrames'
vidCapture = cv2.VideoCapture(filename)
q1 = queue.Queue(10)
q2 = queue.Queue(10)
framDelay = 42

class ExtractFrames(threading.Thread):
	def __init__(self, target=None, name=None):
		super(ExtractFrames, self).__init__()
		self.target = target
		self.name = name

	if not os.path.exists(outDir):
		print("Output directory for frames, {}, created...".format(outDir))
		os.makedirs(outDir)

	def run(self):
		count = 0
		
		while True:
			if not q1.full():
				success, image = vidCapture.read()
				if success:
					q1.put(image)
					cv2.imwrite("{}/frame_{:04d}.jpg".format(outDir, count), image)
					print("Reading frame {}".format(count))
					count += 1
				else:
					print("Export Complete")
					break
		return

class ConvertToGray(threading.Thread):
	def __init__(self, target=None, name=None):
		super(ConvertToGray, self).__init__()
		self.target = target
		self.name = name

	def run(self):
		count = 0
		while True:
			if not q1.empty():
				image = q1.get()
				inFileName = "{}/frame_{:04d}.jpg".format(outDir, count)
				inputFrame = cv2.imread(inFileName, cv2.IMREAD_COLOR)

				if(inputFrame is not None):
					print("Converting frame {}".format(count))
					grayscaleFrame = cv2.cvtColor(inputFrame, cv2.COLOR_BGR2GRAY)
					outFrameName = "{}/grayscale_{:04d}.jpg".format(outDir, count)
					q2.put(cv2.imwrite(outFrameName, grayscaleFrame))
					if os.path.exists(inFileName):
						os.remove(inFileName)
					count += 1
					inFileName = "{}/grayscale_{:04d}.jpg".format(outDir, count)
					success, jpgImage = cv2.imencode('.jpg', image)

		return

class DisplayVideo(threading.Thread):
	def __init__(self, target=None, name=None):
		super(DisplayVideo, self).__init__()
		self.target = target
		self.name = name

	def run(self):
		count = 0
		while True:
			if not q2.full():
				q2.get()
				startTime = time.time()
				frameName = "{}/grayscale_{:04d}.jpg".format(outDir, count)
				frame = cv2.imread(frameName)
				if frame is not None:
					print("Displaying frame {}".format(count))
					cv2.imshow("Video", frame)

					elapsedTime = int((time.time()-startTime) * 1000)
					print("Time to process frame is {}".format(elapsedTime))
					
					timeToWait = max(1, framDelay - elapsedTime)
					count += 1

					if cv2.waitKey(timeToWait) and 0xFF == ord("q"):
						break

						startTime = time.time()
						count += 1
						frameName = "{}/grayscale_{:04d}.jpg".format(outDir, count)
						frame = cv2.imread(frameName)
						cv2.destroyAllWindows()
				else:
					print("Video is done playing...")
					break

if __name__ == '__main__':
	extract = ExtractFrames(name='extract')
	convert = ConvertToGray(name='convert')
	video = DisplayVideo(name='video')

	extract.start()
	convert.start()
	video.start()

