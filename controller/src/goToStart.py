#!/usr/bin/env python3
#icuas 22 competition 
#script for manually go back in zone 0
#auth: Anastasiou Andreas
#date: February 2022
import rospy
from geometry_msgs.msg import PoseStamped
from std_msgs.msg import Float32
from std_srvs.srv import Empty

try:
	rospy.init_node('testingNode', anonymous=True)
	posePub = rospy.Publisher('/red/tracker/input_pose', PoseStamped, queue_size=10)
	ballRelease = rospy.Publisher('/red/ball/magnet/gain', Float32, queue_size=10)
	ballSpawn = rospy.ServiceProxy('/red/spawn_ball', Empty)
	rospy.sleep(1)
	
	pos0 = PoseStamped()
	pos0.pose.position.x = -10
	pos0.pose.position.y = 0
	pos0.pose.position.z =  10 #3
	
	pos1 = PoseStamped()
	pos1.pose.position.x = 0
	pos1.pose.position.y = 0
	pos1.pose.position.z = 10 #4
	
	pos2 = PoseStamped()
	pos2.pose.position.x = -10 #10
	pos2.pose.position.y = 0 #-3
	pos2.pose.position.z = 2.539  #10 #3
	
	posePub.publish(pos1)
	rospy.sleep(3)
	posePub.publish(pos0)
	rospy.sleep(3)
	posePub.publish(pos2)
	rospy.sleep(3)
	ballRelease.publish(1.0)
	rospy.sleep(4)
	ballSpawn.call()
except Exception as e:
	print(e)
