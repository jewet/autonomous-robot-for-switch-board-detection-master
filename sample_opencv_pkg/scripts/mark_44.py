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

frame = None


data = [0, 0, 0, 0, 0, 0]


def talker():
    global data
    pub=rospy.Publisher('array_values', Int16MultiArray,queue_size = 6)
    #rospy.init_node('pub_marray')
    r = rospy.Rate(0.001)
    while not rospy.is_shutdown():
        print ("LOOP running")
        m = Int16MultiArray(data=data)
        rospy.loginfo(data)
        pub.publish(m)
        time.sleep(0.1)
        #r.sleep()


def Imagecallback(ros_image):
    global frame
    global data
    bridge = CvBridge()
    frame1 = bridge.imgmsg_to_cv2(ros_image, "32FC1")
    frame1 = np.array(frame1, dtype=np.float32)
    cv2.normalize(frame1, frame1, 0, 1, cv2.NORM_MINMAX)
    frame2 = frame1
    frame1 = cv2.resize(frame1, (0, 0), fx=0.033, fy=0.1)
    height, width= frame1.shape
    sum_l = 0
    sum_r = 0
    for j in range(int(height/3), int(2*height/3)):
        for i in range(0, width/2):
            sum_l += frame1[j][i]
    for j in range(int(height / 3), int(2 * height / 3)):
        for i in range(width / 2, width):
            sum_r += frame1[j][i]
    sum_l=sum_l/(height*width/2)
    sum_r=sum_r/(height*width/2)
    # print 'sum_l: ', sum_l
    # print 'sum_r: ', sum_r
    if sum_r < 0.05 and sum_r < 0.05:
        print ("Move Backward")
        data = [130, 130, 0, 1, 1, 0]
    elif abs(sum_l - sum_r) < 0.02:
        print ("Move forward")
        data = [130, 130, 1, 0, 1, 0]
    elif sum_l > sum_r:
        data=[130,130,0,0,1,0]
        print ('Take Left')
    elif sum_r > sum_l:
        data = [130,130, 1, 0, 0, 0]
        print("Take right")
    height, width= frame2.shape

    cv2.rectangle(frame2, (0,height/3), (width,2*height/3), (255), 5)
    cv2.imshow('frame', frame2)
    cv.WaitKey(1)
    #frame=frame1
    # cv2.namedWindow('frame', cv2.WINDOW_NORMAL)
    # print frame
    # print"%.4f" % np.max(frame)


if __name__ == '__main__':
    try:
        rospy.init_node("Edge_detetcion")
        image_sub = rospy.Subscriber("/kinect2/sd/image_depth_rect", Image, Imagecallback)
        time.sleep(2)
        # while True:
            # str2 = raw_input("Waiting: ")
            # file1 = open('depth%s' % time.time() + '.txt', 'w+')
            # for row in frame:
            #     file1.write("[")
            #     for element in row:
            #         file1.write(str("%.2f" % element) + "\t")
            #     file1.write("]\n")
        thread.start_new_thread(talker,())
        rospy.spin()
    except KeyboardInterrupt:
        print"Shutting down vision node."
        cv.DestroyAllWindows()
