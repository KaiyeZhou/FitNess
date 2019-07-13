# -*- coding: UTF-8 -*-

import sys, time
from PyQt5 import QtWidgets
from PyQt5.QtCore import QTimer, QThread, pyqtSignal
from mainwindow import Ui_MainWindow

from densepose import densepose
from classify_count import classify_count
import argparse

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

class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent=parent)
        self.setupUi(self)
        # 初始化一个定时器
        #self.timer = QTimer(self)
        # 定义时间超时连接start_app
        #self.timer.timeout.connect(self.start)
        # 定义时间任务是一次性任务
        #self.timer.setSingleShot(True)
        # 启动时间任务
        #self.timer.start()

    def start(self):
        #time.sleep(2)
        #self.textBrowser.append('test1')
        # 实例化一个线程
        self.work = WorkThread()
        # 多线程的信号触发连接到UpText
        self.work.trigger.connect(self.UpText)
        #启动另一个线程
        self.work.start()


    # 信号与槽函数的连接
    #self.btnStart.clicked.connect(self.slotStart)
    #self.thread.sinOut.connect(self.slotAdd)

    def UpText(self, file_in):
        time.sleep(0.03)
        self.textBrowser.append(file_in)

class WorkThread(QThread):
    # 定义一个信号
    trigger = pyqtSignal(str)

    def __int__(self):
        # 初始化函数，默认
        super(WorkThread, self).__int__()

    def run(self):
        file_out = 'start'
        self.trigger.emit(file_out)
        time_start = time.time()
        action_classify, action_count, maxList = densepose(parse_args())
        #等待5秒，给触发信号，并传递test
        if action_classify == 0 or 1 or 2:
            #self.textBrowser.append('正在做硬拉动作')
            file_out = '正在做硬拉动作'
            self.trigger.emit(file_out)
            #self.textBrowser.append('做了%d 次' % action_count)
            file_out = '做了%d 次' + str(action_count)
            self.trigger.emit(file_out)
            print ("Bingo!")
            for i in range(len(maxList)):
                if maxList[i] > 260:
                    self.textBrowser.append('第%d 个动作完成度： 100 %%' % (i + 1))
                else:
                    percent = maxList[i] / 260 * 100
                    self.textBrowser.append('第%d 个动作完成度： %d %%' % (i + 1, int(percent)))
            if min(maxList) > 260:
                self.textBrowser.append('整体评分： 100 分')
            else:
                self.textBrowser.append('整体评分: %d 分' % (int(min(maxList) / 260 * 100)))
        else:
            file_out = 'aaaaaa'
            self.trigger.emit(file_out)
            file_out = '正在做硬拉动作' + str(action_classify)
            self.trigger.emit(file_out)


"""
        
        
"""



if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec_())