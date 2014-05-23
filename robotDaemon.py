# -*- coding: utf-8 -*-
import urllib
import json
import urllib2
import RPi.GPIO as GPIO
import time
import os
import requests
import threading
'''
@Author:ATF
@Date:2014-5-22 16:28:20
@Update:
      ID  Modify      Date         Description      
      1   ATF    2014/5/22 16:43   add another order to response the order.
                                   both the camera order and the camera order enabled.
                                   To make sure the two progress parallel response.So
                                   is to the robot control Unit.



'''

#define the car movement
forwardTuple=(1,0,1,0) #前进
backwardTuple=(0,1,0,1)#后退
leftTurnTuple=(0,0,1,0)#左轴转 ,其实是向右转圈的
rightTurnTuple=(1,0,0,0)#右轴转
stopTuple=(0,0,0,0)#停止

#定义命令延迟时间，根据网络情况自动设定延迟长短
ORDER_MS_DELAY=0.05#micro short delay 5ms
ORDER_S_DELAY=0.1#short delay 100ms
ORDER_M_DELAY=0.5#midlle delay
ORDER_L_DELAY=1.0#long delay
ORDER_XL_DELAY=1.5#extent long delay

#define the robot daemon start or stop
ROBOT_FLAG=False

#define the camera start or stop
CAMERA_FLAG=False

#defione the root URL and local URL to request
#URL="http://nb.kusu.cn/atf/"
#URL="http://rrcontrol.sinaapp.com/atf/"
URL="http://192.168.252.1/netbug/atf/"

#defin the GPIO output Tuple
gpioPinTuple=(7,8,23,24)
GPIO.setmode(GPIO.BCM)
#GPIO.setup(25, GPIO.OUT)

#init the GPIO
for pid in gpioPinTuple:
    GPIO.setup(pid,GPIO.OUT)
    GPIO.output(pid,1)

'''
定义一个函数，做到根据指令调用不同的Tuple，然后根据Tuple中的值去设定
GPIO口的高低电平。
'''
def robotMove(t):
    for (x,y) in zip(gpioPinTuple,t):
        #print ('pin',x,'io out is:',y)
        GPIO.output(x,y)
class postCapture(threading.Thread):
    def __init__(self,capicity):
        threading.Thread.__init__(self)
        self.capicity = capicity
        self.thread_stop = False
    #overwrite
    def run(self):
        while not self.thread_stop:
            print (self.capicity)
            files = {'file':open('/home/pi/images/capture.jpg')}
            os.system("/home/pi/cDir/capture /home/pi/images/capture.jpg "+ str(self.capicity))
            r = requests.post(postUrl,files=files)
            self.thread_stop = True
            print (r.text)          
while(True):

    orderUrl=URL+'orderOutMemory.php'
    postUrl=URL+'upload.php'

    #use the json format order to charge eg:jsonData['robot'] get the robot order
    jsonData=json.loads(urllib.urlopen(orderUrl).read())
    #print rs
    '''
    ps:python has no  switch case. python theme: simple

       according to the transport protocol :
              0x0*   robot control
              0x1*   sensor control 
              0x2*   camera control
              0x3*   relay control
              0x4*   led control
              0x5*   audio control
              ...
        eg:{"robot":"0x00","sensor":"0x10","camera":"0x20","relay":"0x30","led":"0x40","audio":"0x50"}
        so i classify all the orders use the third character.that is rs[2].
    '''
    
    print jsonData
    #robot control
    if(jsonData['robot'][3] == '0'):
        robotMove(stopTuple)
    else:
        if(jsonData['robot'] == '0x01'):
            robotMove(forwardTuple)
        elif(jsonData['robot'] == '0x02'):
            robotMove(backwardTuple)
        elif(jsonData['robot'] == '0x03'):
            robotMove(leftTurnTuple)    
        elif(jsonData['robot'] == '0x04'):
            robotMove(rightTurnTuple)   
    #sensor control     
    if(jsonData['sensor'][3] == '0'):
        print('have no order now,wait for ATF')
    #camera control
    if(jsonData['camera'][3] != '0'):
        files = {'file':open('/home/pi/images/capture.jpg')}
        if(jsonData['camera'][3] == 'A'):
            #os.system("/home/pi/cDir/capture /home/pi/images/capture.jpg 100")
            postCapture(100).start()
        else:
            #os.system("/home/pi/cDir/capture /home/pi/images/capture.jpg "+str(int(jsonData['camera'][3])*10))
            postCapture(int(jsonData['camera'][3])*10).start()
        #r = requests.post(postUrl,files=files)
        #print (r.text)
    else:
        print ('camera closed')
 

    #default the GPIO to stop the action from lasting for  a long time
    #for n in gpioPinTuple:
    #    GPIO.output(n,0)    
    
    time.sleep(ORDER_MS_DELAY) #next order to request
    #print 'next order to request'
#reset the default setting
GPIO.cleanup()
'''
*urllib2.urlopen()得到的其实是一个object,并不是response之类的文字信息
*返回的object有两个方法:1.geturl()返回真正的url;2.info()返回类似头信息的数据
*参考:http://www.crifan.com/resolved_python_with_urllib2urlopen_picurl_othersite_returns_the_result_amplt_addinfourl_at_27548688_whose_fp__amplt_socket_fileobject_object_at_0x019cdb30_ampgt_ampgt_what_does_it_mean/
'''

        
