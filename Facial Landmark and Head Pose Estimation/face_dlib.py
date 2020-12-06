#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Oct 23 13:03:40 2018

@author: kahin
"""

from imutils import face_utils
from imutils import resize
import sys,traceback
import time
import dlib
import cv2
import numpy as np
from math import sqrt

K = [6.5308391993466671e+002, 0.0, 3.1950000000000000e+002,
     0.0, 6.5308391993466671e+002, 2.3950000000000000e+002,
     0.0, 0.0, 1.0]
D = [7.0834633684407095e-002, 6.9140193737175351e-002, 0.0, 0.0, -1.3073460323689292e+000]

cam_matrix = np.array(K).reshape(3, 3).astype(np.float32)
dist_coeffs = np.array(D).reshape(5, 1).astype(np.float32)

#//fill in 3D ref points(world coordinates), model referenced from 
#http://aifi.isr.uc.pt/Downloads/OpenGL/glAnthropometric3DModel.cpp

object_pts = np.float32([[6.825897, 6.760612, 4.402142], #33 left brow left corner
                         [1.330353, 7.122144, 6.903745], #29 left brow right corner
                         [-1.330353, 7.122144, 6.903745], #34 right brow left corner
                         [-6.825897, 6.760612, 4.402142], #38 right brow right corner
                         [5.311432, 5.485328, 3.987654], #13 left eye left corner
                         [1.789930, 5.393625, 4.413414], #17 left eye right corner
                         [-1.789930, 5.393625, 4.413414], #25 right eye left corner
                         [-5.311432, 5.485328, 3.987654], #21 right eye right corner
                         [2.005628, 1.409845, 6.165652], #55 nose left corner
                         [-2.005628, 1.409845, 6.165652], #49 nose right corner
                         [2.774015, -2.080775, 5.048531], #43 mouth left corner
                         [-2.774015, -2.080775, 5.048531], #39 mouth right corner
                         [0.000000, -3.116408, 6.097667], #45 mouth central bottom corner
                         [0.000000, -7.415691, 4.070434]]) #6 chin corner

 
reprojectsrc = np.float32([[5.0, 5.0, 5.0], # origin
                           [-5.0, 5.0, 5.0], # x axis
                           [5.0, -5.0, 5.0], #-y axis
                           [5.0, 5.0, 10.0]]) #z axis
                           
                           

line_pairs = [[0, 1], [0, 2], [0, 3]]

def get_head_pose(shape):
    image_pts = np.float32([shape[17], shape[21], shape[22], shape[26], shape[36],
                            shape[39], shape[42], shape[45], shape[31], shape[35],
                            shape[48], shape[54], shape[57], shape[8]])

    _, rotation_vec, translation_vec = cv2.solvePnP(object_pts, image_pts, cam_matrix, dist_coeffs)

    reprojectdst, _ = cv2.projectPoints(reprojectsrc, rotation_vec, translation_vec, cam_matrix, dist_coeffs)

    reprojectdst = tuple(map(tuple, reprojectdst.reshape(4,2)))

    # calc euler angle
    rotation_mat, _ = cv2.Rodrigues(rotation_vec)
    pose_mat = cv2.hconcat((rotation_mat, translation_vec))
    _, _, _, _, _, _, euler_angle = cv2.decomposeProjectionMatrix(pose_mat)

    return reprojectdst, euler_angle

def distance(p1,p2):
    dist = sqrt( (p1[0] - p2[0])**2 + (p1[1] - p1[1])**2 )*1.4
    return np.array([dist],dtype='float32')[0]


# initialize dlib's face detector (HOG-based) and then create
# the facial landmark predictor
print("[INFO] loading facial landmark predictor...")
detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")

with open('hist','rb') as histogram_avg_file:
    histogram_avg = np.fromfile(histogram_avg_file, dtype='float32')

# initialize the video stream and allow the cammera sensor to warmup
print("[INFO] camera sensor warming up...")
vs = cv2.VideoCapture(0)
time.sleep(2.0)

# Define the codec and create VideoWriter object
#fourcc = cv2.VideoWriter_fourcc(*'XVID')
#out = cv2.VideoWriter('output.avi',fourcc, 20.0, (640,480))

# loop over the frames from the video stream
while True:
    # grab the frame from the threaded video stream, resize it to
    # have a maximum width of 400 pixels, and convert it to
    # grayscale
    ret, frame = vs.read()
    frame = cv2.flip( frame, 1 )
    frame = resize(frame, width=720)
    gray_image = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
 
    # detect faces in the grayscale frame
    faces = detector(gray_image, 0)
    
    # draw face rectangle
    if(len(faces) > 0):
        x = faces[0].left()
        y = faces[0].top()
        w = faces[0].right()
        h = faces[0].bottom()
        cv2.rectangle(frame, (x, y), (w, h), (0, 255, 0), 0);
    
    # loop over the face detections
    for face in faces:
        # determine the facial landmarks for the face region, then
        # convert the facial landmark (x, y)-coordinates to a NumPy
        # array
        shape = predictor(gray_image, face)
        shape = face_utils.shape_to_np(shape)

        reprojectdst, euler_angle = get_head_pose(shape)

        reproject_diff = distance(reprojectdst[2],shape[31])
#        colors = [(0, 0, 255),(0, 255, 0),(255, 0, 0)]
#        for (start, end), color in zip(line_pairs,colors):
#            start_point = reprojectdst[start]
#            stop_point = reprojectdst[end]
#            cv2.line(frame, start_point, stop_point, color,2)
            

        color = (0, 255, 0)
        start_point = reprojectdst[line_pairs[2][0]]
        stop_point = reprojectdst[line_pairs[2][1]]
        
        #move
        start_point = (start_point[0]+reproject_diff,start_point[1])
        stop_point = (stop_point[0]+reproject_diff,stop_point[1])
        
        cv2.line(frame, start_point, stop_point, color,2)

        cv2.putText(frame, "X: " + "{:7.2f}".format(euler_angle[0, 0]), (frame.shape[0]-20, 20), cv2.FONT_HERSHEY_SIMPLEX,
                    0.75, (0, 0, 0), thickness=2)
        cv2.putText(frame, "Y: " + "{:7.2f}".format(euler_angle[1, 0]), (frame.shape[0]-20, 50), cv2.FONT_HERSHEY_SIMPLEX,
                    0.75, (0, 0, 0), thickness=2)
        cv2.putText(frame, "Z: " + "{:7.2f}".format(euler_angle[2, 0]), (frame.shape[0]-20, 80), cv2.FONT_HERSHEY_SIMPLEX,
                    0.75, (0, 0, 0), thickness=2)

        
        
        #shape array has facial landmarks detected
        #1-17 stands for face contour
        #18-22 for left eyebrow
        #23-27 for right eyebrow
        #28-31 nose height
        #32-36 nose bottom width
        #37-42 indexes stands for left eye
        #43-48 indexes stands for rigth eye
        #49-68 for mouth
        
        face_contour = []
        eyebrows = [[],[]]
        nose = [[],[]]
        eyes = [[],[]]
        mouth = []


        # extract face landmarks
        for ((x, y), cnt) in zip(shape,range(1,68)):
            
            #extract face contour
            if(cnt > 0 and cnt <= 17):
                face_contour.append((x,y))
                
            elif(cnt > 17 and cnt <= 22):
                eyebrows[0].append((x,y))
            elif(cnt > 22 and cnt <= 27):
                eyebrows[1].append((x,y))
                
            elif(cnt > 27 and cnt <= 31):
                nose[0].append((x,y))
            elif(cnt > 31 and cnt <= 36):
                nose[1].append((x,y))
                
            elif(cnt > 36 and cnt <= 42):
                eyes[0].append((x,y))
            elif(cnt > 42 and cnt <= 48):
                eyes[1].append((x,y))
                  
            else:
                mouth.append((x,y))
        
        
        # loop over the (x, y)-coordinates for the facial landmarks
		# and draw them on the image
        for x,y in face_contour:
            cv2.circle(frame, (x, y), 1, (0, 0, 255), -1)
            
        for x,y in mouth:
            cv2.circle(frame, (x, y), 1, (50, 0, 150), -1)
            
        for eyebrow in eyebrows:
            for x,y in eyebrow:
                cv2.circle(frame, (x, y), 1, (255, 0, 255), -1) 
        
        for _nose in nose:
            for x,y in _nose:
                cv2.circle(frame, (x, y), 1, (100, 100, 255), -1) 
        
        
        try:
            eye_diff=0
            for eye in eyes:
                rightmost_pt = 0
                leftmost_pt = 2*frame.shape[0]
                top_pt = 2*frame.shape[1]
                bottom_pt = 0
                for x,y in eye:
                    leftmost_pt = min(x, leftmost_pt)
                    rightmost_pt = max(x, rightmost_pt)
                    bottom_pt = max(y, bottom_pt)
                    top_pt = min(y, top_pt)
                    
                    cv2.circle(frame, (x, y), 1, (255, 255, 255), -1)
                    
#                cv2.rectangle(frame, (leftmost_pt, top_pt), (rightmost_pt, bottom_pt), (100, 100, 0), 1);
                            

                # get eye bounds
                eye_pixels = gray_image[top_pt:bottom_pt,leftmost_pt:rightmost_pt]
                
                eye_pixels = cv2.equalizeHist(eye_pixels)
                
                eye_pixels_mask = eye_pixels.copy()
                eye_pixels_mask *= 0
                
                eye_contours = np.array( [[x-leftmost_pt,y-top_pt] for x,y in eye] )              
                cv2.fillPoly(eye_pixels_mask, pts=[eye_contours], color=255)
                
                shape = eye_pixels.shape
                eye_pixels_mask = eye_pixels_mask.flatten()
                eye_pixels = eye_pixels.flatten()
                for i in range(0,len(eye_pixels)):
                    if eye_pixels_mask[i]==0:
                        eye_pixels[i] = 255
                
                eye_pixels_mask = eye_pixels_mask.reshape(shape)
                eye_pixels = eye_pixels.reshape(shape)
                
                
                
                
                gray_start_x = 0
                gray_stop_x = bottom_pt-top_pt
                gray_start_y = 0 + eye_diff
                gray_stop_y = rightmost_pt-leftmost_pt + eye_diff
                
                frame[gray_start_x:gray_stop_x, gray_start_y:gray_stop_y, 0] = eye_pixels
                frame[gray_start_x:gray_stop_x, gray_start_y:gray_stop_y, 1] = eye_pixels
                frame[gray_start_x:gray_stop_x, gray_start_y:gray_stop_y, 2] = eye_pixels
                
                #small improvement after thresholding
                kernel = np.ones((3,3),np.uint8)
                eye_pixels = cv2.erode(eye_pixels, kernel, iterations=2)
                eye_pixels = cv2.dilate(eye_pixels, kernel, iterations=1)
                
                

                
                M = cv2.moments(eye_pixels)
                if(M["m00"] != 0):
                    cX = int(M["m10"] / M["m00"])
                    cY = int(M["m01"] / M["m00"])
                    cv2.circle(frame, (leftmost_pt+cX, top_pt+cY), 1, (0, 255, 0), -1)

                
                #mask
                frame[gray_start_x+25:gray_stop_x+25, gray_start_y:gray_stop_y,0] = eye_pixels
                frame[gray_start_x+25:gray_stop_x+25, gray_start_y:gray_stop_y,1] = eye_pixels
                frame[gray_start_x+25:gray_stop_x+25, gray_start_y:gray_stop_y,2] = eye_pixels
                
                
                
                eye_diff = 100
            
        except Exception as e:
            print(e)
            traceback.print_exc(file=sys.stdout)
     
            
#    out.write(frame)    

    cv2.imshow("Frame", frame)
    key = cv2.waitKey(1) & 0xFF
 
	# if the `q` key was pressed, break from the loop
    if key == ord("q"):
        break
    elif key == ord("s"):
        cv2.imwrite('captured.png',frame)

vs.release()
#out.release()
cv2.destroyAllWindows()
     
    