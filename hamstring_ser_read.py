import sys
import serial
import struct
from threading import Thread
import time
import csv
from datetime import datetime
import numpy as np
from PyQt5 import QtWidgets, QtGui,QtCore
import pandas as df
from scipy import signal
import matplotlib.pyplot as plt
import numpy as np
from scipy.signal import lfilter, lfilter_zi, butter
from numpy import ones

class SerialPort(object):
    # Contains functions that enable communication between the docking station and the IMU watches
    def __init__(self, serialport="COM12", serialrate=115200):
        self.c=0
        self.ad='0'
        self.count = 0
        self.plSz = 0
        self.payload = bytearray()
        self.sw=0
        self.w=[]
        self.l=np.zeros((5,1000))
        self.l1=np.zeros((1000,5))
        self.y=[0,0,0,0,0]
        self.q=[]
        self.s=0
        self.fs = 200.0  # Sample frequency (Hz)
        self.f0 = 50.0  # Frequency to be removed from signal (Hz)
        self.Q = 30.0  # Quality factor
        # Initialise serial port
        self.serialport = serialport
        self.ser = serial.Serial(serialport, serialrate)
        self.b_notch, self.a_notch = butter(7, 0.1)
        self.zi = lfilter_zi(self.b_notch, self.a_notch)
        # self.b_notch, self.a_notch = signal.iirnotch(self.f0, self.Q, self.fs)
        self.emg_1=[]
        self.emg_2=[]

        
    def show_data(self):
        chksum=0
        _chksum=1
        payload=[]
        y1=[]
        x=[]
        current_date_time = datetime.now()
        while self.s==1:     
            start = time.time()
            trl=self.ser.read(2000)
            # print("read it!")
            # print(trl)
            # print(f'Time: {time.time() - start}')
            x.append(trl)
            y1=y1+list(x[:][0])
            x=[]
            for i in range(10000):
               
                if y1[0]==255 and y1[1]==255:
                    
                    if len(y1)>23:
                        chksum = 255 + 255
                        plSz = y1[2]
                        chksum += plSz
                        y2=bytes(y1[3:23])
                        self.payload = y2
                        chksum += sum(y1[3:23])
                        chksum = bytes([chksum % 256])
                        _chksum = bytes([y1[23]%256])
                        if chksum==_chksum:  
                            self.force_=  list(struct.unpack("f", self.payload[0:4]))
                            self.emg_chnl_1 =list(struct.unpack("f", self.payload[4:8]))
                            self.emg_chnl_2 = list(struct.unpack("f", self.payload[8:12]))
                            self.enc_ = list(struct.unpack("L", self.payload[12:16]))
                            self.Tim_val_ = list(struct.unpack("L", self.payload[16:20]))
                            # [self.emg_1.append(i) for i in self.emg_chnl_1]
                            # [self.emg_2.append(i) for i in self.emg_chnl_2]

                            # self.out = lfilter(self.b_notch, self.a_notch, self.emg_chnl_1,zi=self.zi*self.emg_chnl_1[0])
                            # self.out_ = lfilter(self.b_notch, self.a_notch, self.out, zi=self.zi*self.out[0])

                            # self.out1 = lfilter(self.b_notch, self.a_notch, self.emg_chnl_2,zi=self.zi*self.emg_chnl_2[0])
                            # self.out1_ = lfilter(self.b_notch, self.a_notch, self.out1, zi=self.zi*self.out[0])
                            

                            # print(self.emg_chnl_1[0])  
                            # self.c=[self.force_,self.out_,self.out1_,self.enc_,self.Tim_val_]
                            self.c=[self.force_,self.emg_chnl_1,self.emg_chnl_2,self.enc_,self.Tim_val_]
                            # print(self.c)
                            
                            # self.c_=[self.force_[0]]
                            self.q.append(self.c)
                            # print(self.c_)
                            if len(self.q)>10000:
                                self.q=self.q[1:10001]
                            if self.sw :
                                
                                self.writer.writerow([self.force_,self.emg_chnl_1,self.emg_chnl_2,self.angle,self.Tim_val_])
                                # print([self.force_[0],self.emg_chnl_1[0],self.emg_chnl_2[0],self.enc_[0],self.Tim_val_[0]])
                            y1=y1[24:]
                            if len(y1)<24:
                                break
                        else:
                            y1=y1[24:]
                            if len(y1)<24:
                                break
                    else:
                        break       
                else:
                    y1=y1[i+1:]
                    if len(y1)<4:
                        break

    def kill_switch(self, sw,path3,angle):
        self.angle = angle
        if sw:
            header=['force','eng_chnl_1','emg_chnl_2',"angle",'Time']
            
            self.f=open(path3, 'w',newline='')
            self.writer = csv.writer(self.f)
            self.writer.writerow(header)
            #self.f.truncate(480)
            self.sw = 1
        if not sw:
            self.f.close()
            self.sw = 0
            
    def connect1(self):
        if self.ser.isOpen():
            self.show=Thread(target=self.show_data,args=())
            self.show.start() 





