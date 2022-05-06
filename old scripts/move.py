#!/usr/bin/env python3

import rospy
from geometry_msgs.msg import PoseStamped
from time import sleep

def talker():
    pub = rospy.Publisher('/red/tracker/input_pose', PoseStamped, queue_size=10)
    rospy.init_node('pose_pub', anonymous=True)
    rate = rospy.Rate(10) 
    #while not rospy.is_shutdown():
    pose = PoseStamped()
    pose.pose.position.x = -9.982971
    pose.pose.position.y = -0.044320
    pose.pose.position.z = 10.0
    pub.publish(pose)
    sleep(3)    
    pose.pose.position.x = 0.0
    pose.pose.position.y = 0.0
    pose.pose.position.z = 10.0
    pub.publish(pose)
    sleep(1)    
    pose.pose.position.x = 10.0
    pose.pose.position.y = -3.0
    pose.pose.position.z = 2.0
    pub.publish(pose)
        
    rate.sleep()

if __name__ == '__main__':
    try:
        talker()
    except rospy.ROSInterruptException:
        pass
