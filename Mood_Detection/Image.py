#!/usr/bin/python

'''Image class has all methods used on training dataset'''

import cv2
import glob
import os
import sys
import numpy as np
import math

class Image:
	
	def __init__(self, cascade = ''):
		self.CASCADE_PATH = cascade
		#self.IMG_PATH = img
		
	def identify(self, **kwargs):
		Cascade = cv2.CascadeClassifier(self.CASCADE_PATH)
		#os.chdir(self.IMG_PATH)
		parameters = {}
		for filename, image in kwargs.iteritems():
			#image = cv2.imread(str(filename))
			gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
			objects = Cascade.detectMultiScale(
			    gray,
			    scaleFactor=1.1,
			    minNeighbors=5,
			    minSize=(30, 30),
			    flags = cv2.cv.CV_HAAR_SCALE_IMAGE
			)
			print "Found {0} objects!".format(len(objects))
			for (x, y, w, h) in objects:
				if filename not in parameters: parameters[filename] = [(x, y, w, h)]
				else: parameters[filename].append((x, y, w, h))
		#print len(parameters)
		return parameters
		
	def cropImg(self, **kwargs):
		crop_img = []
		for filename, list_of_parameters in self.identify(**kwargs).iteritems():
			for (x, y, w, h) in list_of_parameters:
				crop_img.append(kwargs[filename][y:y+h , x:x+w])
		return crop_img
			
	def saveImg(self, PATH, *args):
		os.chdir(PATH)
		for i, image in enumerate(args):
			print "Saved {0} image".format(i)
			cv2.imwrite(str(i) + '.bmp' , image)
		return
		
	def cornerDetect(self, img):
		'''img is a dictionary with filename as key and image as value'''
		for key in img:	gray = cv2.cvtColor(img[key],cv2.COLOR_BGR2GRAY)
		gray = np.float32(gray)
		dst = cv2.cornerHarris(gray,2,3,0.04)
		#(x, y, w, h) = identify(img)
		#result is dilated for marking the corners, not important
		dst = cv2.dilate(dst,None)
		# Threshold for an optimal value, it may vary depending on the image.
		#if j,i lies in y:y+h , x:x+w; use those coordinates
		corners= []
		for filename, list_of_parameters in self.identify(**img).iteritems():
			for (x, y, w, h) in list_of_parameters:
				count = 0.
				X = 0
				Y = 0
				for i in range(x,x+w):
					for j in range(y,y+h):
						if dst[i][j] > 0.5*dst.max():
							X += i
							Y += j
							count += 1
				corners.append([X/count , Y/count])
		return corners
		
	
	def rotateImage(self, image, angle):
  		image_center = tuple(np.array(image.shape)/2)
  		rot_mat = cv2.getRotationMatrix2D((image_center[0], image_center[1]),angle,1.0)
  		result = cv2.warpAffine(image, rot_mat, (image.shape[0], image.shape[1]),flags=cv2.INTER_LINEAR)
  		#result = cv2.resize(result, tuple(reversed(image.shape[:2])))
  		return result
	
	
	def alignEyes(self, **kwargs):
		'''args has images'''
		aligned = {}
		for filename, image in kwargs.iteritems():
			corners = self.cornerDetect({filename:image})
			if len(corners) == 2:
				tangent = (corners[0][1] - corners[1][1])/(corners[0][0] - corners[1][0])
				angle = math.degrees(math.atan(tangent))
				aligned[filename] = self.rotateImage(image, angle)
			else: aligned[filename] = image
		return aligned
				
				
	def alignImg(self, *args):
		'''Align eyes and mouth in all images
		First rotate the images to align the eyes
		Then change (x,y,w,h) to align all the eyes in the dataset to a fixed point'''
		pass

	def average(self, *args):
		'''Find average of all images in args'''
		pass
		

			
if __name__ == '__main__':
	if 'crop' in sys.argv:
		img = Image(str(os.getcwd()) + '/haarcascades/haarcascade_frontalface_alt.xml')
		BASE_IMG_PATH = str(sys.argv[2])
		images = {}
		for filename in glob.glob(BASE_IMG_PATH + '/*.bmp'):
			images[filename] = cv2.imread(filename)
		cropped = img.cropImg(**images)
		img.saveImg(str(os.getcwd()) + '/cropped', *cropped)
		
	if 'rotate' in sys.argv:
		x = Image()
		img = x.rotateImage(cv2.imread(str(os.getcwd()) + '/male/EMBmale20happy.bmp'), 45)
		cv2.imshow('rotated', img)
		cv2.waitKey(0)
	
	if 'align' in sys.argv:
		eye = Image(str(os.getcwd()) + '/haarcascades/haarcascade_eye.xml')
		face = Image(str(os.getcwd()) + '/haarcascades/haarcascade_frontalface_alt.xml')
		images = {}
		for filename in glob.glob(str(os.getcwd()) + '/male/*.bmp'):
			images[filename] = cv2.imread(filename)
		aligned = eye.alignEyes(**images)
		cropped = face.cropImg(**aligned)
		face.saveImg(str(os.getcwd()) + '/cropped', *cropped)
	
