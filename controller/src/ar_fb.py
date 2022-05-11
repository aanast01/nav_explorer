#!/usr/bin/env python3
"""
 rostopic echo /ar_pose_marker/markers[0]/pose/pose/position/x -n1
"""

import rospy
import cv2 as cv
from cv_bridge import CvBridge
from ar_track_alvar_msgs.msg import AlvarMarkers
from geometry_msgs.msg import PoseStamped, Point
from std_msgs.msg import Float32, Bool, String
from sensor_msgs.msg import Image

rateHz = 1
start_flag = False
pose_start_flag = False
dronePose = PoseStamped()

def start_callback(flag):
    global start_flag
    start_flag = flag.data

def pose_callback(pose):
    global dronePos, pose_start_flag
    dronePos = pose
    if pose.pose.position.y >= 4.8 and pose.pose.position.y <= 5.2:
        pose_start_flag=True

def image_callback(image_message):
    global cv_image
    bridge = CvBridge()
    cv_image = bridge.imgmsg_to_cv2(image_message, desired_encoding='bgr8')

def callback(data):
    try:
        if data.markers[0]:
            print(data.markers)
            pose = PoseStamped()
            pose.pose.position.x = data.markers[0].pose.pose.x
            pose.pose.position.y = data.markers[0].pose.pose.y
            pose.pose.position.z = 0.0
            #pub.publish(pose)
    except:
        rospy.wait_for_message("/ar_pose_marker", PoseStamped)

def throw_ball(ar_tag_pose):
    global ballRelease, pub, ar_pose_pub, ar_image_pub,dronePos, counter, cv_image
    ar_tag_pose_point = Point()
    ar_tag_pose_point.x = ar_tag_pose.markers[0].pose.pose.position.x
    ar_tag_pose_point.y = ar_tag_pose.markers[0].pose.pose.position.y
    ar_tag_pose_point.z = ar_tag_pose.markers[0].pose.pose.position.z
    ar_pose_pub.publish(ar_tag_pose_point)
    cv_image2 = cv_image.copy()
    text = "x:" + str(ar_tag_pose_point.x) + " y:" + str(ar_tag_pose_point.y) + " z:" + str(ar_tag_pose_point.z)
    cv.putText(cv_image2, text,(10,50), cv.FONT_HERSHEY_SIMPLEX, 0.5, (255,255,255), 2, cv.LINE_AA)
    cv.imwrite('./tag_image.jpg', cv_image2)
    #cv.imshow('test',cv_image2)
    #cv.waitKey(1)
    #rospy.sleep(20)
    bridge = CvBridge()
    image_message = bridge.cv2_to_imgmsg(cv_image2, encoding="bgr8")
    ar_image_pub.publish(image_message)
    pose = PoseStamped()
    pose.pose.position.x = ar_tag_pose.markers[0].pose.pose.position.x - (0.85 if (counter>=3 and counter<=7) else 0)
    pose.pose.position.y = ar_tag_pose.markers[0].pose.pose.position.y - (((ar_tag_pose.markers[0].pose.pose.position.y/abs(ar_tag_pose.markers[0].pose.pose.position.y))  * 0.95) if (counter<=2 or counter>=8) else 0)
    if pose.pose.position.y < -7:
        pose.pose.position.y = -6.8
    elif pose.pose.position.y > 7:
        pose.pose.position.y = 6.8
    pose.pose.position.z = ar_tag_pose.markers[0].pose.pose.position.z + 1.0
    pose.pose.orientation.w = dronePos.pose.orientation.w
    pose.pose.orientation.z = dronePos.pose.orientation.z
    print(pose)
    pub.publish(pose)
    while (dronePos.pose.position.z <= pose.pose.position.z-0.2) or (abs(dronePos.pose.position.y) <= abs(pose.pose.position.y)-0.3) or (dronePos.pose.position.x <= pose.pose.position.x-0.3):
        rospy.sleep(0.2)
    #rospy.sleep(3.0)
    ballRelease.publish(0.0)
    rospy.sleep(1)
    print("KIOS UCY DONE!!!")
    exit(0)


def listener():
    global start_flag,rateHz,dronePos, ballRelease, pub, ar_pose_pub, ar_image_pub,counter,pose_start_flag
    rospy.init_node('listener', anonymous=True)
    #rospy.Subscriber("ar_pose_marker", AlvarMarkers, callback)
    pub = rospy.Publisher('/red/tracker/input_pose', PoseStamped, queue_size=10)
    rospy.Subscriber("/red/avoider/done", Bool, start_callback)
    rospy.Subscriber("/red/camera/color/image_raw", Image, image_callback)
    ballRelease = rospy.Publisher('/red/uav_magnet/gain', Float32, queue_size=10)
    ar_pose_pub = rospy.Publisher('/red/tag_position_reconstructed', Point, queue_size=10)
    ar_image_pub = rospy.Publisher('/red/tag_image_annotated', Image, queue_size=10)
    rospy.Subscriber("/red/pose", PoseStamped, pose_callback)
    rate = rospy.Rate(rateHz)  # 10Hz
    log_pub = rospy.Publisher('/debug_logger', String, queue_size=10)

    print('WAITING FOR START FLAG')
    while not start_flag:
        rate.sleep()
    print('AR TAG DETECTION STARTING')

    counter=0
    overall_couter=0
    while True:
        try:
            print('WAITING FOR AR TAG POSE')
            while not pose_start_flag:
                rate.sleep()
            ar_tag_pose = rospy.wait_for_message("/ar_pose_marker", AlvarMarkers)
            ar_tag_pose2 = rospy.wait_for_message("/ar_pose_marker", AlvarMarkers)
            if len(ar_tag_pose.markers)>0:
                throw_ball(ar_tag_pose)
                rospy.sleep(1)
            elif len(ar_tag_pose2.markers)>0:
                throw_ball(ar_tag_pose2)
                rospy.sleep(1)
            else:
                if counter==0:
                    pose = PoseStamped()
                    pose.pose.position.x = dronePos.pose.position.x + 3.5
                    pose.pose.position.y = dronePos.pose.position.y
                    pose.pose.position.z = dronePos.pose.position.z
                    pose.pose.orientation.w = dronePos.pose.orientation.w
                    pose.pose.orientation.z = dronePos.pose.orientation.z
                    pub.publish(pose)
                    print('CHANGING POSITION')
                    rospy.sleep(3)
                    counter+=1
                    log_pub.publish(str(counter))
                elif counter==1:
                    pose = PoseStamped()
                    pose.pose.position.x = dronePos.pose.position.x + 3.5
                    pose.pose.position.y = dronePos.pose.position.y
                    pose.pose.position.z = dronePos.pose.position.z
                    pose.pose.orientation.w = dronePos.pose.orientation.w
                    pose.pose.orientation.z = dronePos.pose.orientation.z
                    pub.publish(pose)
                    print('CHANGING POSITION')
                    rospy.sleep(3)
                    counter+=1
                    log_pub.publish(str(counter))
                elif counter==2:
                    pose = PoseStamped()
                    pose.pose.position.x = dronePos.pose.position.x
                    pose.pose.position.y = dronePos.pose.position.y
                    pose.pose.position.z = dronePos.pose.position.z
                    pose.pose.orientation.w = 1.0
                    pose.pose.orientation.z = 0.0
                    pub.publish(pose)
                    print('CHANGING POSITION')
                    rospy.sleep(2.5)
                    counter+=1
                    log_pub.publish(str(counter))
                elif counter==3:
                    pose = PoseStamped()
                    pose.pose.position.x = dronePos.pose.position.x 
                    pose.pose.position.y =  dronePos.pose.position.y - 2.5
                    pose.pose.position.z = dronePos.pose.position.z
                    pose.pose.orientation.w = dronePos.pose.orientation.w
                    pose.pose.orientation.z = dronePos.pose.orientation.z
                    pub.publish(pose)
                    print('CHANGING POSITION')
                    rospy.sleep(2.75)
                    counter+=1
                    log_pub.publish(str(counter))
                elif counter==4:
                    pose = PoseStamped()
                    pose.pose.position.x = dronePos.pose.position.x 
                    pose.pose.position.y = dronePos.pose.position.y - 2.5
                    pose.pose.position.z = dronePos.pose.position.z
                    pose.pose.orientation.w = dronePos.pose.orientation.w
                    pose.pose.orientation.z = dronePos.pose.orientation.z
                    pub.publish(pose)
                    print('CHANGING POSITION')
                    rospy.sleep(2.75)
                    counter+=1
                    log_pub.publish(str(counter))
                elif counter==5:
                    pose = PoseStamped()
                    pose.pose.position.x = dronePos.pose.position.x 
                    pose.pose.position.y =  dronePos.pose.position.y - 2.5
                    pose.pose.position.z = dronePos.pose.position.z
                    pose.pose.orientation.w = dronePos.pose.orientation.w
                    pose.pose.orientation.z = dronePos.pose.orientation.z
                    pub.publish(pose)
                    print('CHANGING POSITION')
                    rospy.sleep(2.75)
                    counter+=1
                    log_pub.publish(str(counter))
                elif counter==6:
                    pose = PoseStamped()
                    pose.pose.position.x = dronePos.pose.position.x 
                    pose.pose.position.y = dronePos.pose.position.y - 2.5
                    pose.pose.position.z = dronePos.pose.position.z
                    pose.pose.orientation.w = dronePos.pose.orientation.w
                    pose.pose.orientation.z = dronePos.pose.orientation.z
                    pub.publish(pose)
                    print('CHANGING POSITION')
                    rospy.sleep(2.75)
                    counter+=1
                    log_pub.publish(str(counter))
                elif counter==7:
                    pose = PoseStamped()
                    pose.pose.position.x = dronePos.pose.position.x
                    pose.pose.position.y = dronePos.pose.position.y
                    pose.pose.position.z = dronePos.pose.position.z
                    pose.pose.orientation.w = 1.57079632679
                    pose.pose.orientation.z = -1.57079632679
                    pub.publish(pose)
                    print('CHANGING POSITION')
                    rospy.sleep(2.5)
                    counter+=1
                    log_pub.publish(str(counter))
                elif counter==8:
                    pose = PoseStamped()
                    pose.pose.position.x = dronePos.pose.position.x - 3.5
                    pose.pose.position.y = dronePos.pose.position.y
                    pose.pose.position.z = dronePos.pose.position.z
                    pose.pose.orientation.w = dronePos.pose.orientation.w
                    pose.pose.orientation.z = dronePos.pose.orientation.z
                    pub.publish(pose)
                    print('CHANGING POSITION')
                    rospy.sleep(3)
                    counter+=1
                    log_pub.publish(str(counter))
                elif counter==9:
                    pose = PoseStamped()
                    pose.pose.position.x = dronePos.pose.position.x - 3.5
                    pose.pose.position.y = dronePos.pose.position.y
                    pose.pose.position.z = dronePos.pose.position.z
                    pose.pose.orientation.w = dronePos.pose.orientation.w
                    pose.pose.orientation.z = dronePos.pose.orientation.z
                    pub.publish(pose)
                    print('CHANGING POSITION')
                    rospy.sleep(3)
                    counter+=1
                    log_pub.publish(str(counter))
                elif counter==10:
                    print("TAG NOT FOUND!!! STARTING AGAIN!!!")
                    pose = PoseStamped()
                    pose.pose.position.x = 2.0
                    pose.pose.position.y = 5.0
                    pose.pose.position.z = 2.5
                    pose.pose.orientation.w = 1.57079632679
                    pose.pose.orientation.z = 1.57079632679
                    pub.publish(pose)
                    rospy.sleep(1)
                    pose_start_flag=False
                    #ballRelease.publish(0.0)
                    #exit(0)
                    counter=0
                    log_pub.publish(str(counter))
                    overall_counter+=1
                    if overall_counter==2:
                        print("I GIVE UP!!!")
                        exit(0)
        except Exception as e:
            print(e)











    

if __name__ == '__main__':
    try:
        listener()
    except rospy.ROSInterruptException:
        pass
