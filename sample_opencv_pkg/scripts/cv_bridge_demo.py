#! /usr/bin/env python

import rospy
import cv2
import cv2.cv as cv
from sensor_msgs.msg import Image, CameraInfo
from cv_bridge import CvBridge, CvBridgeError
import numpy as np
import time


class cvBridgeDemo():
    def __init__(self):
            flag=True
            i=0
            self.node_name = "cv_bridge_demo"
            #Initialize the ros node
            rospy.init_node(self.node_name)

            # What we do during shutdown
            rospy.on_shutdown(self.cleanup)

            # Create the OpenCV display window for the RGB image
            self.cv_window_name = self.node_name
            #cv.NamedWindow(self.cv_window_name, cv.CV_WINDOW_NORMAL)
            #cv.MoveWindow(self.cv_window_name, 25, 75)

            # And one for the depth image
            #cv.NamedWindow("Depth Image", cv.CV_WINDOW_NORMAL)
            #cv.MoveWindow("Depth Image", 25, 350)

            # Create the cv_bridge object
            self.bridge = CvBridge()

            # Subscribe to the camera image and depth topics and set

            # the appropriate callbacks
            #self.image_sub = rospy.Subscriber("/kinect2/sd/image_color_rect", Image, self.image_callback)
            self.depth_sub = rospy.Subscriber("/kinect2/sd/image_depth_rect", Image, self.depth_callback)
            rospy.loginfo("Waiting for image topics...")

    def image_callback(self, ros_image):
            # Use cv_bridge() to convert the ROS image to OpenCV format
            frame = self.bridge.imgmsg_to_cv2(ros_image, "bgr8")
            # Convert the image to a Numpy array since most cv2 functions

            # require Numpy arrays.
            frame = np.array(frame, dtype=np.uint8)

            # Process the frame using the process_image() function
            display_image = self.process_image(frame)

            # Display the image.
            cv2.imshow(self.node_name, display_image)

            # Process any keyboard commands
            self.keystroke = cv.WaitKey(5)

            if 32 <= self.keystroke < 128:
                cc = chr(self.keystroke).lower()

                if cc == 'q':
                    # The user has press the q key, so exit
                    rospy.signal_shutdown("User hit q key to quit.")


    def depth_callback(self, ros_image):
            # Use cv_bridge() to convert the ROS image to OpenCV format
            try:
                # The depth image is a single-channel float32 image
                depth_image = self.bridge.imgmsg_to_cv2(ros_image, "32FC1")
            except CvBridgeError,e:
                print(e)

            # Convert the depth image to a Numpy array since most cv2 functions
            # require Numpy arrays.
            depth_array = np.array(depth_image, dtype=np.float32)
            
            # Normalize the depth image to fall between 0 (black) and 1 (white)
            cv2.normalize(depth_array, depth_array, 0, 255, cv2.NORM_MINMAX)
            frame=cv2.convertScaleAbs(depth_array,alpha=1)
            print (frame)
            # Process the depth image
            depth_display_image = self.process_depth_image(depth_array) 
            
            
            str2 = input("Waiting: ")   
            #depth_display_image = cv2.resize(depth_display_image, (0,0), fx=0.032 , fy=0.075)  
                        
            #file1 = open('Depth_%d'%time.time()+'.txt','w')
            #for row in depth_display_image:
            #    file1.write("[")
            #    for element in row:
            #        file1.write(str("%.2f"%element)+"\t")
                    
            #    file1.write("]\n")
            
           
            print (depth_display_image)
                
            # Display the result
            #cv2.imshow("Depth Image", depth_display_image)

    def process_image(self, frame):
        
            # Convert to grayscale
            grey = cv2.cvtColor(frame, cv.CV_BGR2GRAY)
            # Blur the image
            grey = cv2.blur(grey, (7, 7))
            # Compute edges using the Canny edge filter
            edges = cv2.Canny(grey, 15.0, 30.0)
            return edges


    def process_depth_image(self, frame):
            # Just return the raw image for this demo
            return frame
     
    def cleanup(self):
            print ("Shutting down vision node.")
            cv2.destroyAllWindows()

if __name__ == '__main__':
    try:
        cvBridgeDemo()
        rospy.spin()
    except KeyboardInterrupt:
        print ("Shutting down vision node.")
    cv.DestroyAllWindows()

