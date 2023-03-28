
import os
import sys
import csv
from PyQt5.uic import loadUi
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QDialog, QApplication
from PyQt5 import QtWidgets, QtGui
import time
from PyQt5.QtCore import QTimer
from hamstring_ser_read  import SerialPort
from PyQt5.QtWidgets import *
from threading import Thread
from PyQt5.QtCore import QObject, pyqtSignal
from random import randint
import numpy as np
import pyqtgraph as pg
import serial.tools.list_ports
from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from OpenGL.GL import *
file_name="main_window.ui"

class SignalCommunicate(QObject):
    request_graph_update = pyqtSignal()
    invoke=pyqtSignal(int)
       

    



class Shoulder(QDialog):
    def __init__(self):
        super(Shoulder, self).__init__()
        self.path_= os.path.abspath(file_name)
        print(self.path_)
        
        loadUi(self.path_, self)
        # self.ls=[(255, 0, 0),(0,255, 0),(0, 0, 255)]
        self.serial_ports=[]
        self.serial_hwid=[]
        self.obj = []
        for i in range(3):
            self.obj.append(pg.PlotWidget())
        layout1=QGridLayout()
        for j in range(3):
            layout1.addWidget(self.obj[j], j, 0)  
        self.pen = pg.mkPen(color=(255, 0, 0))
        self.plot.setLayout(layout1)
        self.ports = serial.tools.list_ports.comports()
        self.x = list(range(1000)) # 1000 time points
        self.y = [randint(0, 1000) for _ in range(1000)] 
        
        for port, desc, hwid in sorted(self.ports):
            self.serial_ports.append(port)
            self.serial_hwid.append(hwid)
            # print(hwid)
            print("{}: {} [{}]".format(port, desc, hwid))
        self.indx = self.serial_hwid.index("USB VID:PID=16C0:0483 SER=8032500 LOCATION=1-1:x.0")
        self.port_number = self.serial_ports[self.indx]
        self.ref=[]
        for l in range(3):
            self.ref.append(self.obj[l].plot(self.x, self.y, pen=self.pen))
        self.a = SerialPort(self.port_number,115200) #self.port_number
        self.a.s=1
        self.c=0
        self.sw=0
        self.d=[]
        self.counter=0
        self.counter1=0
        self.dummy=0
        self.counter2=0
        self.a.connect1()
        self.sec.setText("0")
        self.min.setText("0")
        self.hour.setText("0")
        self.enc_lbl.setText("0")
        self.serial_=SerialPort
        self.startrecording.clicked.connect(self.count2)
        # self.restart.clicked.connect(self.restart_)
        self.signalComm = SignalCommunicate()
        self.signalComm.request_graph_update.connect(self.update_plot_data)
        self.show_new_window()



    def create_file_and_folder(self):
        print(os.path)
        
        if not os.path.exists(str(self.inp_txt.text())):
            os.makedirs(str(self.inp_txt.text()))
            self.file_write=True
            if self.zero.isChecked():
                self.selected_angle = "zero"
            if self.fifteen.isChecked():
                self.selected_angle = "fifteen"
            if self.thirty.isChecked():
                self.selected_angle = "thirty"
            if self.fourty_five.isChecked():
                self.selected_angle = "fourty_five"
            if self.sixty.isChecked():
                self.selected_angle = "sixty"
            if self.seventy_five.isChecked():
                self.selected_angle = "seventy_five"
        
            self.csv_path = os.path.join(str(self.inp_txt.text()) + "\\" + self.selected_angle + ".csv")
            self.a.kill_switch(1,self.csv_path)
            # print(self.csv_path)
            # self.csv_file = open(self.csv_path, "w", newline='')
            # self.csv =csv.writer(self.csv_file)

        elif os.path.exists(str(self.inp_txt.text())):
            print(os.path)
            # os.makedirs(str(self.textbox.text()))
            self.file_write=True
            if self.zero.isChecked():
                self.selected_angle = "zero"
            if self.fifteen.isChecked():
                self.selected_angle = "fifteen"
            if self.thirty.isChecked():
                self.selected_angle = "thirty"
            if self.fourty_five.isChecked():
                self.selected_angle = "fourty_five"
            if self.sixty.isChecked():
                self.selected_angle = "sixty"
            if self.seventy_five.isChecked():
                self.selected_angle = "seventy_five"
        
            self.csv_path = os.path.join(str(self.inp_txt.text()) + "\\" + self.selected_angle + ".csv")
            self.a.kill_switch(1,self.csv_path)
            # print(self.csv_path)
            # self.csv_file = open(self.csv_path, "w", newline='')
            # self.csv =csv.writer(self.csv_file)


              
    def update_plot_data(self):
        
        if len(self.a.q)==10001:
            self.p=self.a.q[1:10001]
        else:
            self.p=self.a.q  
        
        self.t=np.transpose(self.p)
        self.enc_lbl.setText(str((list(self.t[0][3]))[0]))
        # self.enc_lbl.setText("CONNECTED")
        
        for i in range(3):
            if len(list(self.t[0][i]))==10000:
                # sel.[j for j in range(len(self.ls))]
                self.ref[i].setData(np.array(list(range(10000))),self.t[0][i],pen=pg.mkPen(color=i))
                

    def count2(self):
        self.c+=1
        if self.c % 2 == 1:
            self.start_record()
            
        else:
            self.stop_record()

    def stop_record(self):
        self.a.kill_switch(0,self.csv_path)
        self.timer1.stop()
        self.counter=0
        self.counter1=0
        self.counter2=0
 
        self.sec.setText(" %d" % self.counter)
        self.min.setText(" %d" % self.counter1)
        self.hour.setText(" %d" % self.counter2)
        self.startrecording.setText('Start Recording')
        print("Recording stopped")

    def recurring_timer(self):
        self.counter += 1
        self.sec.setText(" %d" % self.counter)
        if self.counter>=60:
            self.counter1+=1
            self.min.setText(" %d" % self.counter1)
            self.counter=0
            self.sec.setText(" %d" % self.counter)
            if self.counter1>=60:
                self.counter2+=1
                self.hour.setText(" %d" % self.counter2)
                self.counter=0
                self.sec.setText(" %d" % self.counter)
                self.counter1=0
                self.min.setText(" %d" % self.counter1)

    def start_record(self):
        self.create_file_and_folder()
        
        self.timer1 = QTimer()
        self.timer1.setInterval(1000)
        self.timer1.timeout.connect(self.recurring_timer)
        self.timer1.start()
        self.startrecording.setText('Stop Recording')
        print("Recording started")
   
    def show_new_window(self):
        reader1 = Thread(target=self.connectnow,args=())
        reader1.start()
     
    def connectnow(self):
        while 1:
            time.sleep(0.5)
            self.signalComm.request_graph_update.emit() 
            
# main

app = QApplication(sys.argv)
# window = QMainWindow()

welcome = Shoulder()
widget = QtWidgets.QStackedWidget()
widget.addWidget(welcome)
widget.setFixedHeight(800)
widget.setFixedWidth(1150)
widget.setWindowTitle('Hamsring And Quadriceps Force Measurements')
widget.setWindowIcon(QtGui.QIcon('favicon.ico'))
# widget.setWindowIcon(QIcon("favicon.ico"))
widget.show()
try:
    sys.exit(app.exec_())
except:
    print("Exiting")