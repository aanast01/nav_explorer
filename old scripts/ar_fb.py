#!/usr/bin/env python3
import rospy
from ar_track_alvar_msgs.msg import AlvarMarkers

def callback(data):
    val = data.markers[0].pose.pose.x
    print(val)
    
def listener():

    rospy.init_node('listener', anonymous=True)

    rospy.Subscriber("ar_pose_marker", AlvarMarkers, callback)

    # spin() simply keeps python from exiting until this node is stopped
    rospy.spin()

if __name__ == '__main__':
    listener()

