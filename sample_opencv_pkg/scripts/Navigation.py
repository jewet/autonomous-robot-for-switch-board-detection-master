#! /usr/bin/env python

import rospy
import cv2
import cv2.cv as cv
from sensor_msgs.msg import Image, CameraInfo
from std_msgs.msg import Int16MultiArray
from cv_bridge import CvBridge, CvBridgeError
import numpy as np
import time
import thread
import requests
import json

frame = None
coord = None
frame_depth=None
data = [0, 0, 0, 0, 0, 0]
url = "http://10.24.5.78:5000/livestream"
content_type = 'image/jpeg'
headers = {'content-type': content_type}

def talker():
    global data
    pub=rospy.Publisher('array_values',Int16MultiArray,queue_size = 10)
    #rospy.init_node('pub_marray')
    r = rospy.Rate(0.1)
    while not rospy.is_shutdown():
        print ("LOOP running")
        m = Int16MultiArray(data=data)
        rospy.loginfo(data)
        pub.publish(m)
        time.sleep(0.1)
        #r.sleep()



def Imagecallback(ros_image):
    global frame
    bridge = CvBridge()
    frame = bridge.imgmsg_to_cv2(ros_image, "bgr8")
    frame = np.array(frame, dtype=np.uint8)
    cv2.imshow('frame', frame)
    cv2.waitKey(1)


def Imagecallback_depth(ros_image):
    global frame_depth
    global data
    bridge = CvBridge()
    frame_depth = bridge.imgmsg_to_cv2(ros_image, "32FC1")
    frame_depth = np.array(frame_depth, dtype=np.float32)
    cv2.normalize(frame_depth, frame_depth, 0, 255, cv2.NORM_MINMAX)
    height, width = frame_depth.shape
    
    #CHECK IF THE COORDINATE IS WITHIN THE RANGE IN THE ARRAY
    if coord:
        sum_d = 0 #intialize the increase variable to zero
        for j in range(coord[0][0], coord[1][0]):
            for i in range(coord[0][1], coord[1][1]):
                sum_d += frame_depth[i][j]
        #Average is the sum cumulative divided by start - end 
        avg = sum_d/((coord[1][0]- coord[0][0])*(coord[1][1]- coord[0][1])) 
        cv2.circle(frame_depth, ((coord[1][0]+coord[0][0])/2,(coord[1][1]+coord[0][1])/2), 63, 0, -1)
        # print 'Distance: ', avg
        # print "Position: ", (coord[1][0]+coord[0][0])/2
        # print '---------------------',frame_depth[(coord[0][1]+coord[1][1])/2,(coord[1][0]+coord[0][0])/2]
        if frame_depth[(coord[1][1]+coord[0][1])/2,(coord[1][0]+coord[0][0])/2]>135 :
            data=[0,0,0,0,0,0]
        elif (coord[1][0]+coord[0][0])/2 < width/3:
            print ('Take Left')
            data=[130,130,0,0,1,0]
        elif (coord[1][0]+coord[0][0])/2 > 2*width/3:
            print ('Take right')
            data = [130, 130, 1, 0, 0, 0]
        else:
            print ('Move forward')
            data = [130, 130, 1, 0, 1, 0]
    else:
        data = [0,0,0,0,0,0]
        pass
    #cv2.imshow('depth', frame_depth)
    #cv2.waitKey(1)
    print ('Data: ', data)



def client_side():
    global coord
    while True:
        _, img_encoded = cv2.imencode('.jpg', frame)
        response = requests.post(url, data=img_encoded.tostring(), headers=headers)
        coord = json.loads(response.text)

        if coord:
            coord = [[int(coord[0][0]), int(coord[0][1])], [int(coord[1][0]), int(coord[1][1])]]
            print (coord)
            print ('I am here')
            frame2 = frame
            cv2.rectangle(frame2, (int(coord[0][0]), int(coord[0][1])), (int(coord[1][0]), int(coord[1][1])), (0,0, 255), 5)
            cv2.imshow('frame2', frame2)
            cv2.waitKey(1)


if __name__ == '__main__':
    try:
        rospy.init_node("client_detetcion")
        image_sub = rospy.Subscriber("/kinect2/qhd/image_color", Image, Imagecallback)
        image_sub = rospy.Subscriber("/kinect2/qhd/image_depth_rect", Image, Imagecallback_depth)
        time.sleep(2)
        thread.start_new_thread(client_side,())
        thread.start_new_thread(talker,())
        rospy.spin()
    except KeyboardInterrupt:
        print("Shutting down vision node.")
        cv.DestroyAllWindows()


