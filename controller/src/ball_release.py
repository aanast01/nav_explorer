#!/usr/bin/env python3

import rospy
from geometry_msgs.msg import PoseStamped
from std_msgs.msg import Float32
from std_srvs.srv import Empty
from time import sleep

def talker():
	rospy.init_node('testingNode', anonymous=True)
	posePub = rospy.Publisher('/red/tracker/input_pose', PoseStamped, queue_size=10)
	ballRelease = rospy.Publisher('/red/ball/magnet/gain', Float32, queue_size=10)
	ballSpawn = rospy.ServiceProxy('/red/spawn_ball', Empty)
	rospy.sleep(1)
	
	pos0 = PoseStamped() # zone1
	pos0.pose.position.x = -10
	pos0.pose.position.y = 0
	pos0.pose.position.z =  10 #3
	
	pos1 = PoseStamped() # zone2
	pos1.pose.position.x = 0
	pos1.pose.position.y = 0
	pos1.pose.position.z = 10 #4
	
	pos2 = PoseStamped()  # zone3
	pos2.pose.position.x = 10
	pos2.pose.position.y = -3
	pos2.pose.position.z = 10 #3
	
	posePub.publish(pos2)
	rospy.sleep(3)
#	posePub.publish(pos0)
#	rospy.sleep(3)
	ballRelease.publish(0.0) #1
	rospy.sleep(4)
	ballSpawn.call()

if __name__ == '__main__':
    try:
        talker()
    except rospy.ROSInterruptException:
        pass
