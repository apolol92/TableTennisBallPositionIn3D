import socket
import cv2
import numpy as np
import scipy.spatial
# Just a little script which measures the distance between webcam and a table tennis ball and send the data to a client.
# It was a personal preperation for practical semester
# if there is any bug pls comment.. its a old script
# FUN-Fact: Put the table tennis ball on your google cardboard and couple it with your virtual reality game :)
# TODO: CALIBRATION.. sorry printer was damaged :)
# TODO: SET focal length in px for your webcam

def get_ball_data(img):
    # max dista
    points = []
    rowNumbers = np.where(np.any(img>0, axis=1))
    # get points
    for r in rowNumbers[0]:
        for c in range(0,img.shape[1]):
            if(img[r,c]>0):
                points.append(np.array([r,c]))
    if(len(points)>0):
            X = np.array(points)
            Y = scipy.spatial.distance.pdist(X,'euclidean')
            v = scipy.spatial.distance.squareform(Y)
            s,e = np.unravel_index(v.argmax(), v.shape)
            #print np.array(v[s,e])
            Mx = (points[s][1]+points[e][1])/2.0
            My = (points[s][0]+points[e][0])/2.0
            return np.array([v[s,e],Mx,My])
    return None

#CONFIGURATION COMPUTER_VISION################################
#[18, 202, 179] [20, 255, 217]
#[4, 143, 195] [7, 188, 255]
hsv_min1 = np.array([18, 202, 179])
hsv_max1 = np.array([20, 255, 217])
#[15, 164, 232] [23, 255, 255]
#[5, 144, 255] [6, 173, 255]
#[17, 243, 147] [20, 255, 169]
hsv_min2 = np.array([17, 243, 147])
hsv_max2 = np.array([20, 255, 169])
#[16, 160, 215] [18, 222, 255]

hsv_min3 = np.array([16, 160, 215])
hsv_max3 = np.array([18, 222, 255])

light = True

if light:
    hsv_min3 = np.array([16, 131, 206])
    hsv_max3 = np.array([26, 255, 255])

f = 83/2

#END CONFIGURATION############################################

#Setup Webcam
cap = cv2.VideoCapture(0)
cap.set(3, 320)
cap.set(4, 240)

#Setup server
sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
sock.bind(("127.0.0.1", 8000))
sock.listen(2)
(client,(ip,port)) = sock.accept()
print "Client connected.."
while True:
    ret, frame = cap.read()
    hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    thresholded1 = cv2.inRange(hsv_frame, hsv_min1, hsv_max1)
    thresholded2 = cv2.inRange(hsv_frame, hsv_min2, hsv_max2)
    thresholded3 = cv2.inRange(hsv_frame, hsv_min3, hsv_max3)
    thresholded = cv2.bitwise_or(thresholded1, thresholded2)
    thresholded = cv2.bitwise_or(thresholded,thresholded3)
    thresholded = cv2.GaussianBlur(thresholded,(5,5),0)
    cv2.imshow("test",thresholded)
    #canny = cv2.Canny(thresholded,50,300)
    #cv2.imshow('Canny',canny)
    ball_data = get_ball_data(thresholded)
    if ball_data != None:
        px_diameter = ball_data[0]
        z = 40.0*f/float(px_diameter)
        x = z * (ball_data[1]-(frame.shape[1]/2))/f
        y = z * (ball_data[2]-(frame.shape[0]/2))/f * (-1)
        print x,y,z
        ball_position = str(x)+" "+str(y)+" "+str(z)
        client.send(ball_position)
    #cv2.imshow('Output',frame)
    cv2.waitKey(1)