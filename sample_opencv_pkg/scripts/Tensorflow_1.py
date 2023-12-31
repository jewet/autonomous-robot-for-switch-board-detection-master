#! /usr/bin/env python

import rospy
import cv2
import cv2.cv as cv
from sensor_msgs.msg import Image, CameraInfo
from cv_bridge import CvBridge, CvBridgeError
import os
import numpy as np
import tensorflow as tf
import sys
import time
import thread

# This is needed since the notebook is stored in the object_detection folder.
sys.path.append("/home/apoorva/tensorflow/models/research/object_detection")

# Import utilites
from utils import label_map_util
from utils import visualization_utils as vis_util

frame = None
# def get_frame():
#     global frame
#     while True:
#         print "I am running"
#         ret, frame = video.read()
#
#
# video = cv2.VideoCapture(0)
# ret = video.set(3,640)
# ret = video.set(4,560)
# thread.start_new_thread(get_frame,())



def Imagecallback(ros_image):
    global frame
    bridge = CvBridge()
    frame = bridge.imgmsg_to_cv2(ros_image, "bgr8")
    frame = np.array(frame, dtype=np.uint8)




def detect_obj():
    # Name of the directory containing the object detection module we're using
    MODEL_NAME = '"/home/apoorva/tensorflow/models/research/object_detection/inference_graph'

    # Grab path to current working directory
    CWD_PATH = os.getcwd()

    # Path to frozen detection graph .pb file, which contains the model that is used
    # for object detection.
    PATH_TO_CKPT = os.path.join("/home/apoorva/tensorflow/models/research/object_detection/inference_graph",'frozen_inference_graph.pb')

    # Path to label map file
    PATH_TO_LABELS = os.path.join("/home/apoorva/tensorflow/models/research/object_detection",'training','labelmap.pbtxt')

    # Number of classes the object detector can identify
    NUM_CLASSES = 6

    ## Load the label map.
    # Label maps map indices to category names, so that when our convolution
    # network predicts `5`, we know that this corresponds to `king`.
    # Here we use internal utility functions, but anything that returns a
    # dictionary mapping integers to appropriate string labels would be fine
    label_map = label_map_util.load_labelmap(PATH_TO_LABELS)
    categories = label_map_util.convert_label_map_to_categories(label_map, max_num_classes=NUM_CLASSES, use_display_name=True)
    category_index = label_map_util.create_category_index(categories)

    # Load the Tensorflow model into memory.
    detection_graph = tf.Graph()
    with detection_graph.as_default():
        od_graph_def = tf.GraphDef()
        with tf.gfile.GFile(PATH_TO_CKPT, 'rb') as fid:
            serialized_graph = fid.read()
            od_graph_def.ParseFromString(serialized_graph)
            tf.import_graph_def(od_graph_def, name='')

        sess = tf.Session(graph=detection_graph)


    # Define input and output tensors (i.e. data) for the object detection classifier

    # Input tensor is the image
    image_tensor = detection_graph.get_tensor_by_name('image_tensor:0')

    # Output tensors are the detection boxes, scores, and classes
    # Each box represents a part of the image where a particular object was detected
    detection_boxes = detection_graph.get_tensor_by_name('detection_boxes:0')

    # Each score represents level of confidence for each of the objects.
    # The score is shown on the result image, together with the class label.
    detection_scores = detection_graph.get_tensor_by_name('detection_scores:0')
    detection_classes = detection_graph.get_tensor_by_name('detection_classes:0')

    # Number of objects detected
    num_detections = detection_graph.get_tensor_by_name('num_detections:0')

    # Initialize webcam feed

    while(True):

        # Acquire frame and expand frame dimensions to have shape: [1, None, None, 3]
        # i.e. a single-column array, where each item in the column has the pixel RGB value
        p_time = time.time()
        # # ret, frame = video.read()
        frame_expanded = np.expand_dims(frame, axis=0)
        #
        # Perform the actual detection by running the model with the image as input
        (boxes, scores, classes, num) = sess.run(
            [detection_boxes, detection_scores, detection_classes, num_detections],
            feed_dict={image_tensor: frame_expanded})
        #
        # Draw the results of the detection (aka 'visulaize the results')
        vis_util.visualize_boxes_and_labels_on_image_array(
            frame,
            np.squeeze(boxes),
            np.squeeze(classes).astype(np.int32),
            np.squeeze(scores),
            category_index,
            use_normalized_coordinates=True,
            line_thickness=8,
            min_score_thresh=0.85)
        #
        # # All the results have been drawn on the frame, so it's time to display it.
        cv2.imshow('Object detector', frame)
        print (time.time() -p_time)

        # Press 'q' to quit
        if cv2.waitKey(1) == ord('q'):
            break

    cv2.destroyAllWindows()

try:
    rospy.init_node("Edge_detetcion")
    image_sub = rospy.Subscriber("/kinect2/qhd/image_color", Image, Imagecallback)
    time.sleep(2)
    detect_obj()

    rospy.spin()
except KeyboardInterrupt:
    print("Shutting down vision node.")
    cv.DestroyAllWindows()


