# -*- coding: utf-8 -*-

import os
import cv2
import sys
import time
import shutil

import numpy as np
import PIL.Image as Image

from PyQt5.QtCore import pyqtSlot
from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtWidgets import *
from PyQt5.QtCore import QTimer, QThread, pyqtSignal, Qt
from PyQt5.QtWidgets import QFileDialog,QTabWidget
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtWidgets import QLabel,QWidget

from Ui_Fitness import Ui_MainWindow
from densepose import densepose
import densepose_noskip
from densepose_coach import densepose_coach
from classify_count import classify_count
import argparse

# /home/ww/DensePose/densepose/configs/DensePoseKeyPointsMask_ResNet50_FPN_s1x-e2e.yaml
# /home/ww/DensePose/densepose/configs/DensePoseKeyPointsMask_ResNet50_FPN_s1x-e2e.pkl
# /home/ww/DensePose/video/video_out/
# /home/ww/DensePose/video/test1.mp4
def parse_args():
    parser = argparse.ArgumentParser(description='End-to-end inference')
    parser.add_argument(
        '--cfg',
        dest='cfg',
        help='cfg model file (/path/to/model_config.yaml)',
        default='/home/ww/DensePose/densepose/configs/DensePoseKeyPointsMask_ResNet50_FPN_s1x-e2e.yaml',
        type=str
    )
    parser.add_argument(
        '--wts',
        dest='weights',
        help='weights model file (/path/to/model_weights.pkl)',
        default='/home/ww/DensePose/densepose/configs/DensePoseKeyPointsMask_ResNet50_FPN_s1x-e2e.pkl',
        type=str
    )
    parser.add_argument(
        '--output-dir',
        dest='output_dir',
        help='directory for visualization pdfs (default: /tmp/infer_simple)',
        default='/home/ww/DensePose/video/video_out/',
        type=str
    )
    # parser.add_argument(
    #     '--image-ext',
    #     dest='image_ext',
    #     help='image file name extension (default: jpg)',
    #     default='jpg',
    #     type=str
    # )
    # parser.add_argument(
    #     'im_or_folder', help='image or folder of images', default=None
    # )
    parser.add_argument(
        '--video', help='input video', default='/home/ww/DensePose/video/test1.mp4'
    )
    # if len(sys.argv) == 1:
    #     parser.print_help()
    #     sys.exit(1)
        # print(parser.parse_args())
    return parser.parse_args()


class MainWindow(QMainWindow, Ui_MainWindow):
    """
    Class documentation goes here.
    """
    def __init__(self, parent=None):
        """
        Constructor

        @param parent reference to the parent widget
        @type QWidget
        """
        super(MainWindow, self).__init__(parent)
        self.setupUi(self)
        self.CAM = 0
        self.SkipFra = False
        self.coachpara = False
        global files_para
        files_para = []

    def videoprocessing(self):
        print("gogo")
        global videoName #在这里设置全局变量以便在线程中使用
        videoName,videoType= QFileDialog.getOpenFileName(self,
                                    "打开视频",
                                   "",
                                    #" *.jpg;;*.png;;*.jpeg;;*.bmp")
                                    " *.mp4;;*.avi;;All Files (*)")
        #cap = cv2.VideoCapture(str(videoName))
        th = Thread(self)
        th.changePixmap.connect(self.setImage)
        th.start()
    def setImage(self, image):
        self.label_3.setPixmap(QPixmap.fromImage(image))

    def videoprocessing2(self):
        print("gogo")
        global videoName2 #在这里设置全局变量以便在线程中使用
        #videoName2,videoType= QFileDialog.getOpenFileName(self,
        #                            "打开视频",
        #                            "",
        #                            #" *.jpg;;*.png;;*.jpeg;;*.bmp")
        #                            " *.mp4;;*.avi;;All Files (*)")
        videoName2 = '/home/ww/DensePose/video/video_out/test1.mp4'
        #cap = cv2.VideoCapture(str(videoName))
        th2 = Thread2(self)
        th2.changePixmap.connect(self.setImage2)
        th2.start()
    def setImage2(self, image):
        self.label_4.setPixmap(QPixmap.fromImage(image))

    def Add_CoachVideo(self):
        global CoachVideoFile
        ###单个文件###
        """
        CoachVideoFile,videoType= QFileDialog.getOpenFileName(self,
                                    "打开视频",
                                    "/home/ww/DensePose/video/biaozhun/",
                                    #" *.jpg;;*.png;;*.jpeg;;*.bmp")
                                    " *.mp4;;*.avi;;All Files (*)")
        ###多个文件###
        """
        #"""
        files, ok1 = QFileDialog.getOpenFileNames(self,
                                    "多文件选择",
                                    "/home/ww/DensePose/video/biaozhun/",
                                    "*.mp4;;*.avi;;All Files(*)" )
        print(files,ok1)
        # print(ok1)
        #"""
        ###文件夹###
        """
        directory1 = QFileDialog.getExistingDirectory(self,
                                                      "选取文件夹",
                                                      "/home/ww/DensePose/video/biaozhun")  # 起始路径
        print(directory1)
        """

        # 选择好视频文件后，生成教练参数
        args2 = parse_args()
        args2.video = files[0]
        print files
        action_classify, action_count, maxList, maxheight, start_frame, data1 = densepose_coach(args2)
        sum_maxList = 0
        sum_shoulder = 0
        sum_hand = 0
        sum_foot = 0
        # /home/ww/DensePose/video/coach_para/
        with open("/home/server010/server010/FitNess/output_txt/" + time.strftime('%Y-%m-%d-%H-%M',time.localtime(time.time())) + "coach_para_output.txt", "w") as f:
            f.write("教练身高： %d\n" %maxheight)
            for i in range(len(maxList)):
                sum_maxList += maxList[i]
                sum_shoulder += abs(data1[start_frame[i]][0][5] - data1[start_frame[i]][0][6])
                sum_hand += abs(data1[start_frame[i]][0][9] - data1[start_frame[i]][0][10])
                sum_foot += abs(data1[start_frame[i]][0][15] - data1[start_frame[i]][0][16])
            f.write("教练下蹲距离： %.2f\n" %(sum_maxList / (len(maxList))))
            f.write("教练动作下蹲距离占身高比例： %.3f \n" %((sum_maxList / (len(maxList))) / (maxheight)))
            f.write("教练两肩距离： %.2f\n" %(sum_shoulder / (len(maxList))))
            f.write("教练两手距离： %.2f\n" %(sum_hand / (len(maxList))))
            f.write("教练两脚距离： %.2f\n" %(sum_foot / (len(maxList))))


    def Add_CoachPara(self):
         ###单个文件###
        """
        CoachVideoFile,videoType= QFileDialog.getOpenFileName(self,
                                    "打开视频",
                                    "/home/ww/DensePose/video/biaozhun/",
                                    #" *.jpg;;*.png;;*.jpeg;;*.bmp")
                                    #" *.mp4;;*.avi;;All Files (*)")
                                    "All Files (*);;Text Files (*.txt)")
        """

        ###多个文件###
        #"""
        global files_para
        files_para, ok1 = QFileDialog.getOpenFileNames(self,
                                                  "多文件选择",
                                                  "/home/ww/DensePose/video/biaozhun/",
                                                  "All Files (*);;Text Files (*.txt)")
        print(files_para, ok1)
        #"""

        ###文件夹###
        """
        directory1 = QFileDialog.getExistingDirectory(self,
                                                      "选取文件夹",
                                                      "/home/ww/DensePose/video/biaozhun/")  # 起始路径
        print(directory1)
        """

    #摄像头显示程序
    def Camera_Start(self):
        time.sleep(3)
        global label_5
        #if self.CAM == 0:
            #self.pushButton_2.setText(u'关闭相机')
        th4 = Thread4(self)
        th4.trigger.connect(self.Camera_Show)
        th4.start()
        #self.CAM = 1
        #else:
            #th4.wait()
            #self.pushButton_2.setText(u'打开相机')
            #self.CAM = 0
    def Camera_Show(self, showImage):
        #if self.CAM == 0:
        self.label_5.setPixmap(QtGui.QPixmap.fromImage(showImage))


    #这里时densepose程序
    def Pose_Start(self):
        global SkipFra1    ###是否跳帧、选教练
        SkipFra1 = 0
        self.textBrowser.setPlainText('')
        if (self.SkipFra == False) & (self.coachpara == False):
            SkipFra1 = 0
            print "模式1"
        elif (self.SkipFra == True) & (self.coachpara == False):
            SkipFra1 = 1
            print "模式2"
        elif (self.SkipFra == False) & (self.coachpara == True):
            SkipFra1 = 0 # 2
            print "模式3"
        elif (self.SkipFra == True) & (self.coachpara == True):
            SkipFra1 = 1 # 3
            print "模式4"
        th3 = Thread3(self)
        th3.trigger.connect(self.Pose_Score)
        th3.start()
        #### 线程结束隐藏progressbar
        #self.progressBar.hide()
    def Pose_Score(self, file_in):
        time.sleep(0.03)
        self.textBrowser.append(file_in)
    def Skip_Fra(self, s):
        self.checkBox = self.sender()
        if s == QtCore.Qt.Unchecked:
            self.SkipFra = False
        elif s == QtCore.Qt.Checked: # 选中=不跳帧
            self.SkipFra = True
    def Coach(self, text):
        #print text
        if text == u'>>>>>>>>>>>>>>>>>>>>>>>>> [教练A] <<<<<<<<<<<<<<<<<<<<<<<': #默认教练A
            self.coachpara = False
            print self.coachpara
        elif text == u'>>>>>>>>>>>>>>>>>>>>>>>>> [教练B] <<<<<<<<<<<<<<<<<<<<<<<':
            self.coachpara = True
            print self.coachpara


class Thread(QThread):#采用线程来播放视频

    changePixmap = pyqtSignal(QtGui.QImage)

    def run(self):
        cap = cv2.VideoCapture(videoName)
        count = cap.get(7)
        print(videoName)
        while (cap.isOpened()==True):
            ret, frame = cap.read()
            if count:
                rgbImage = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                convertToQtFormat = QtGui.QImage(rgbImage.data, rgbImage.shape[1], rgbImage.shape[0], QImage.Format_RGB888)#在这里可以对每帧图像进行处理，
                p = convertToQtFormat.scaled(640, 360, Qt.KeepAspectRatio)
                self.changePixmap.emit(p)
                time.sleep(0.03) #控制视频播放的速度
                count = count - 1
            else:
                count = cap.get(7)
                cap = cv2.VideoCapture(videoName)

class Thread2(QThread):#采用线程来播放视频

    changePixmap = pyqtSignal(QtGui.QImage)
    def run(self):
        cap = cv2.VideoCapture(videoName2)
        print(videoName2)
        count2 = cap.get(7)
        while (cap.isOpened()==True):
            ret, frame = cap.read()
            if count2:
                rgbImage = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                convertToQtFormat = QtGui.QImage(rgbImage.data, rgbImage.shape[1], rgbImage.shape[0], QImage.Format_RGB888)#在这里可以对每帧图像进行处理，
                p = convertToQtFormat.scaled(640, 360, Qt.KeepAspectRatio)
                self.changePixmap.emit(p)
                time.sleep(0.03) #控制视频播放的速度
                count2 = count2 - 1
            else:
                count2 = cap.get(7)
                cap = cv2.VideoCapture(videoName2)

class Thread3(QThread):
    trigger = pyqtSignal(str)

    #def __int__(self):
        # 初始化函数，默认
        #super(Thread3, self).__int__()

    def run(self):
        file_out = 'start'
        self.trigger.emit(file_out)
        time_start = time.time()
        if SkipFra1 == 0:
            action_classify, action_count, maxList, maxheight, start_frame, data1 = densepose(parse_args())
        elif SkipFra1 == 1:
            action_classify, action_count, maxList, maxheight, start_frame, data1 = densepose_noskip.densepose(parse_args())
        # elif SkipFra1 == 2:

        # elif SkipFra1 == 3:
        out_savepath = '/home/ww/DensePose//video/video_out/test1.mp4'
        video_path = '/home/ww/DensePose/video/video_out_save/' + time.strftime('%Y-%m-%d-%H-%M',
                                                                            time.localtime(time.time())) + '.mp4'
        shutil.copyfile(out_savepath, video_path)

        # 选择教练参数文件
        global files_para
        if len(files_para) == 0 and action_classify == 0:
            rate_coach = 0.574
        if len(files_para) == 0 and action_classify == 1:
            rate_coach = 0.353
        # print(files_para[0])
        if len(files_para) != 0:
            with open(files_para[0], "r") as f:
                line = f.readlines()
            rate_coach = float(line[2].split()[1])
        if rate_coach <= 0 or rate_coach >= 1 and action_classify == 0:
            rate_coach = 0.574
        if rate_coach <= 0 or rate_coach >= 1 and action_classify == 1:
            rate_coach = 0.353

        if action_classify == 0:
            # self.textBrowser.append('正在做硬拉动作')
            file_out = '正在做硬拉动作'
            self.trigger.emit(file_out)
            #self.textBrowser.append('做了%d 次' % action_count)
            file_out = '做了' + str(action_count) + '次'
            self.trigger.emit(file_out)

            for i in range(len(maxList)):
                if maxList[i] / maxheight > rate_coach:     # 260 / 453.0  
                    #self.textBrowser.append('第%d 个动作完成度： 100 %%' % (i + 1))
                    file_out = '第' + str(i + 1) + '个动作完成度： 100 %'
                    self.trigger.emit(file_out)
                else:
                    percent = (maxList[i] / maxheight) / (rate_coach) * 100
                    #self.textBrowser.append('第%d 个动作完成度： %d %%' % (i + 1, int(percent)))
                    file_out = '第' + str(i + 1) + '个动作完成度： ' + str(int(percent)) + ' %'
                    self.trigger.emit(file_out)
            if min(maxList) / maxheight > rate_coach:
                #self.textBrowser.append('整体评分： 100 分')
                file_out = '整体评分： 100 分'
                self.trigger.emit(file_out)
            else:
                #self.textBrowser.append('整体评分: %d 分' % (int(min(maxList) / 260 * 100)))
                file_out = '整体评分: ' + str(int((min(maxList) / maxheight) / (rate_coach) * 100)) + ' 分'
                self.trigger.emit(file_out)

            with open("/home/ww/DensePose/video/file_output/" + time.strftime('%Y-%m-%d-%H-%M',time.localtime(time.time())) + "_output.txt", "w") as f:
                # f.write("123 %d" %maxheight)
                f.write("正在做硬拉动作\n")
                f.write("做了%d 次\n" %action_count)
                for i in range(len(maxList)):
                    # if i != len(maxList) - 1:
                    # f.write("第%d 个动作起止时间： %d - %d s\n" %((i + 1) , (start_frame[i] // 5), (start_frame[i + 1] // 5)))
                    if i + 1 < len(start_frame):
                        f.write("第%d 个动作起止时间： %d - %d s\n" %((i + 1) , (start_frame[i] // 5), (start_frame[i + 1] // 5)))
                    else:
                        start_frame.append(start_frame[-1] + 10)
                        f.write("第%d 个动作起止时间： %d - %d s\n" %((i + 1) , (start_frame[i] // 5), (start_frame[i + 1] // 5)))
                    if maxList[i] / maxheight > rate_coach:       #教练身高453
                        f.write("第%d 个动作完成度： 100 %%\n" %(i + 1))
                    else:
                        percent = (maxList[i] / maxheight) / (rate_coach) * 100
                        f.write("第%d 个动作完成度： %d %%\n" %(i + 1, int(percent)))
                if min(maxList) / maxheight> rate_coach:
                    f.write("整体评分： 100 分\n")
                else:
                    f.write("整体评分: %d 分\n" %(int((min(maxList) / maxheight) / (rate_coach) * 100)))

            with open("/home/ww/DensePose/video/error_file_output/" + time.strftime('%Y-%m-%d-%H-%M',time.localtime(time.time())) + "_error_output.txt", "w") as f:
                f.write("正在做硬拉动作\n")
                f.write("做了%d 次\n" %action_count)
                for i in range(len(maxList)):
                    if i < len(start_frame):
                        f.write("第%d 个动作两肩距离： %d \n" %((i + 1) , (abs(data1[start_frame[i]][0][5] - data1[start_frame[i]][0][6]))))
                        f.write("第%d 个动作两手握杆距离： %d \n" %((i + 1) , (abs(data1[start_frame[i]][0][9] - data1[start_frame[i]][0][10]))))
                        f.write("第%d 个动作两脚距离： %d \n" %((i + 1) , (abs(data1[start_frame[i]][0][15] - data1[start_frame[i]][0][16]))))
                        f.write("第%d 个动作下蹲距离占身高比例： %.3f \n" %((i + 1) , (maxList[i] / maxheight)))

        if action_classify == 1:
            #self.textBrowser.append('正在做深蹲动作')
            #self.textBrowser.append('做了%d 次' % action_count)
            file_out = '正在做深蹲动作'
            self.trigger.emit(file_out)
            file_out = '做了' + str(action_count) + '次'
            self.trigger.emit(file_out)

            for i in range(len(maxList)):
                if maxList[i] / maxheight > rate_coach:       #160 / 453.0
                    #self.textBrowser.append('第%d 个动作完成度： 100 %%' % (i + 1))
                    file_out = '第' + str(i + 1) + '个动作完成度： 100 %'
                    self.trigger.emit(file_out)
                else:
                    percent = (maxList[i] / maxheight) / (rate_coach) * 100
                    #self.textBrowser.append('第%d 个动作完成度： %d %%' % (i + 1, int(percent)))
                    file_out = '第' + str(i + 1) + '个动作完成度： ' + str(int(percent)) + ' %'
                    self.trigger.emit(file_out)
            if min(maxList) / maxheight> rate_coach:
                #self.textBrowser.append('整体评分： 100 分')
                file_out = '整体评分： 100 分'
                self.trigger.emit(file_out)
            else:
                #self.textBrowser.append('整体评分: %d 分' % (int(min(maxList) / 160 * 100)))
                file_out = '整体评分: ' + str(int((min(maxList) / maxheight) / (rate_coach) * 100)) + ' 分'
                self.trigger.emit(file_out)

            with open("/home/ww/DensePose/video/file_output/" + time.strftime('%Y-%m-%d-%H-%M',time.localtime(time.time())) + "_output.txt", "w") as f:
                f.write("正在做深蹲动作\n")
                f.write("做了%d 次\n" %action_count)
                for i in range(len(maxList)):
                    if i + 1 < len(start_frame):
                        f.write("第%d 个动作起止时间： %d - %d s\n" %((i + 1) , (start_frame[i] // 5), (start_frame[i + 1] // 5)))
                    else:
                        start_frame.append(start_frame[-1] + 10)
                        f.write("第%d 个动作起止时间： %d - %d s\n" %((i + 1) , (start_frame[i] // 5), (start_frame[i + 1] // 5)))
                    if maxList[i] / maxheight > rate_coach:       #教练身高453
                        f.write("第%d 个动作完成度： 100 %%\n" %(i + 1))
                    else:
                        percent = (maxList[i] / maxheight) / (rate_coach) * 100
                        f.write("第%d 个动作完成度： %d %%\n" %(i + 1, int(percent)))
                if min(maxList) / maxheight> rate_coach:
                    f.write("整体评分： 100 分\n")
                else:
                    f.write("整体评分: %d 分\n" %(int((min(maxList) / maxheight) / (rate_coach) * 100)))

            with open("/home/ww/DensePose/video/error_file_output/" + time.strftime('%Y-%m-%d-%H-%M',time.localtime(time.time())) + "_error_output.txt", "w") as f:
                f.write("正在做深蹲动作\n")
                f.write("做了%d 次\n" %action_count)
                for i in range(len(maxList)):
                    if i < len(start_frame):
                        f.write("第%d 个动作两肩距离： %d \n" %((i + 1) , (abs(data1[start_frame[i]][0][5] - data1[start_frame[i]][0][6]))))
                        f.write("第%d 个动作两手握杆距离： %d \n" %((i + 1) , (abs(data1[start_frame[i]][0][9] - data1[start_frame[i]][0][10]))))
                        f.write("第%d 个动作两脚距离： %d \n" %((i + 1) , (abs(data1[start_frame[i]][0][15] - data1[start_frame[i]][0][16]))))
                        f.write("第%d 个动作下蹲距离占身高比例： %.3f \n" %((i + 1) , (maxList[i] / maxheight)))
        
        score = 0
        if action_classify == 2:
            #self.textBrowser.append('正在做卧推动作')
            #self.textBrowser.append('做了%d 次' % action_count)
            file_out = '正在做卧推动作'
            self.trigger.emit(file_out)
            file_out = '做了' + str(action_count) + '次'
            self.trigger.emit(file_out)

            for i in range(len(maxList)):
                if maxList[i] > 130:
                    #self.textBrowser.append('第%d 个动作完成度： 100 %%' % (i + 1))
                    file_out = '第' + str(i + 1) + '个动作完成度： 100 %'
                    self.trigger.emit(file_out)
                else:
                    percent = maxList[i] / 130 * 100
                    #self.textBrowser.append('第%d 个动作完成度： %d %%' % (i + 1, int(percent)))
                    file_out = '第' + str(i + 1) + '个动作完成度： ' + str(int(percent)) + ' %'
                    self.trigger.emit(file_out)
            #self.textBrowser.append('整体评分: %d 分' % (int(sum(maxList) / (130 * len(maxList)) * 100)))
            if int(sum(maxList) / (130 * len(maxList)) * 100) > 100:
                score = 100
            else:
                score = int(sum(maxList) / (130 * len(maxList)) * 100)
            file_out = '整体评分: ' + str(score) + ' 分'
            self.trigger.emit(file_out)

            with open("/home/ww/DensePose/video/file_output/" + time.strftime('%Y-%m-%d-%H-%M',time.localtime(time.time())) + "_output.txt", "w") as f:
                f.write("正在做卧推动作\n")
                f.write("做了%d 次\n" %action_count)
                for i in range(len(maxList)):
                    # f.write("第%d 个动作起止时间： %d - %d s\n" %((i + 1) , (start_frame[i] // 5), (start_frame[i + 1] // 5)))
                    if i + 1 < len(start_frame):
                        f.write("第%d 个动作起止时间： %d - %d s\n" %((i + 1) , (start_frame[i] // 5), (start_frame[i + 1] // 5)))
                    else:
                        start_frame.append(start_frame[-1] + 10)
                        f.write("第%d 个动作起止时间： %d - %d s\n" %((i + 1) , (start_frame[i] // 5), (start_frame[i + 1] // 5)))
                    if maxList[i] > 130:
                        f.write("第%d 个动作完成度： 100 %%\n" %(i + 1))
                    else:
                        percent = maxList[i] / 130 * 100
                        f.write("第%d 个动作完成度： %d %%\n" %(i + 1, int(percent)))
                f.write("整体评分: %d 分" %(score))

            with open("/home/ww/DensePose/video/error_file_output/" + time.strftime('%Y-%m-%d-%H-%M',time.localtime(time.time())) + "_error_output.txt", "w") as f:
                f.write("正在做卧推动作\n")
                f.write("做了%d 次\n" %action_count)
                for i in range(len(maxList)):
                    if i < len(start_frame):
                        f.write("第%d 个动作两肩距离： %d \n" %((i + 1) , (abs(data1[start_frame[i]][0][5] - data1[start_frame[i]][0][6]))))
                        f.write("第%d 个动作两手握杆距离： %d \n" %((i + 1) , (abs(data1[start_frame[i]][0][9] - data1[start_frame[i]][0][10]))))
                        f.write("第%d 个动作两脚距离： %d \n" %((i + 1) , (abs(data1[start_frame[i]][0][15] - data1[start_frame[i]][0][16]))))
                        f.write("第%d 个动作运动幅度： %d \n" %((i + 1) , (maxList[i])))

        time_end = time.time()
        #self.textBrowser.append('totally cost: {:.3f}s'.format(time_end - time_start))
        file_out = 'totally cost: ' + str(int(time_end - time_start)) + 's'
        self.trigger.emit(file_out)

class Thread4(QThread):
    trigger = pyqtSignal(QtGui.QImage)

    #def __int__(self):
        # 初始化函数，默认
        #super(Thread4, self).__int__()

    def run(self):
        start_time = time.time()
        savepath = '/home/ww/DensePose/video/test1.mp4'
        fourcc = cv2.VideoWriter_fourcc(*'mp4v'.encode('utf-8'))
        out = cv2.VideoWriter(savepath, fourcc, 30, (640, 480))
        delays = 20

        H = 333 # 图片高宽
        W = 480
        x1 = int(W / 3) # 矩形起点
        y1 = 1
        hh = H - 2    # 矩形高宽
        ww = 160
        # x2 = int(W * 2 / 3)
        # y2 = H - 1
        # create a black use numpy,size is:512*512
        rectangle = np.zeros((H, W, 3), np.uint8)
        # fill the image with white
        rectangle.fill(255)

        cv2.rectangle(rectangle, (x1, y1), (x1 + ww, y1 + hh), (255, 0, 0), 3)
        font = cv2.FONT_HERSHEY_SIMPLEX

        cv2.imwrite('./rectangle.png', rectangle)
        rectangle = Image.open('rectangle.png')
        rectangle = rectangle.convert('RGBA')

        color_0 = rectangle.getpixel((0, 0))
        for h in range(H):
            for l in range(W):
                dot = (l, h)
                color_1 = rectangle.getpixel(dot)
                if color_1 == color_0:
                    color_1 = color_1[:-1] + (0,)
                    rectangle.putpixel(dot, color_1)
        rectangle.save('./rectangle.png')

        rectangle = cv2.imread('rectangle.png')
        rows, cols, channels = rectangle.shape
        img2gray = cv2.cvtColor(rectangle, cv2.COLOR_BGR2GRAY)
        ret, mask = cv2.threshold(img2gray, 254, 255, cv2.THRESH_BINARY)  # 这个254很重要
        mask_inv = cv2.bitwise_not(mask)

        self.cap = cv2.VideoCapture()
        flag = self.cap.open(0)
        while(self.cap.isOpened()):
            flag, self.image = self.cap.read()
            show = cv2.resize(self.image, (480, 333))

            #img2 = cv2.resize(img, (show.shape[1], show.shape[0]), interpolation=cv2.INTER_AREA)
            #show = cv2.addWeighted(show, alpha, img, beta, gamma)
            roi = show[0:rows, 0:cols]
            img1_bg = cv2.bitwise_and(roi, roi, mask=mask)
            img2_fg = cv2.bitwise_and(rectangle, rectangle, mask=mask_inv)
            dst = cv2.add(img1_bg, img2_fg)
            show[0:rows, 0:cols] = dst

            show = cv2.cvtColor(show, cv2.COLOR_BGR2RGB)
            showImage = QImage(show.data, show.shape[1], show.shape[0], QtGui.QImage.Format_RGB888)
            self.trigger.emit(showImage)
            out.write(self.image)
            if cv2.waitKey(1) & 0xFF==ord('q') or flag==False or time.time() - \
                    start_time > delays:
                break
        self.cap.release()
        out.release()
        video_path = '/home/ww/DensePose/video/video_save/' + time.strftime('%Y-%m-%d-%H-%M',
                                                                            time.localtime(time.time())) + '.mp4'
        shutil.copyfile(savepath, video_path)



if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    # MainWindow = QtWidgets.QMainWindow()
    ui = MainWindow()
    # ui.setupUi(MainWindow)
    # MainWindow.show()
    ui.show()
    sys.exit(app.exec_())
