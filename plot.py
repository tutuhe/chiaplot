import datetime
import os
import signal
import threading
import time
from multiprocessing import Process
from PyQt5.QtGui import QColor, QBrush, QFont
from PyQt5.QtWidgets import QTableWidgetItem, QHBoxLayout
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPainter, QPen, QColor
from PyQt5.QtWidgets import (QWidget)

class PlotArg():
    def __init__(self, k:int=32, u:int=128, b:int=3390, r:int=2, n:int=1, t:str='./', d:str='./', delay:int=0):
        self.arg_k = k
        self.arg_u = u
        self.arg_b = b
        self.arg_r = r
        self.arg_n = n
        self.arg_t = t
        self.arg_d = d
        self.arg_delay = delay

    def toCmd(self):
        cmd = '-k %d -u %d -b %d -r %d -n %d -t %s -d %s' % \
              (self.arg_k, self.arg_u, self.arg_b, self.arg_r, self.arg_n, self.arg_t, self.arg_d)
        return cmd

class PlotInfo():
    def __init__(self):
        self.lines = ''
        self.started = False
        self.t_start = 0
        self.id = None
        self.t_f1 = 0
        self.t_p1 = 0
        self.t_p2 = 0
        self.t_p3 = 0
        self.t_p4 = 0
        self.t_total = 0
        self.t_copy = 0
        self.t_end = 0
        self.end = False

    def rLine(self, line:str):
        self.lines += line
        try:
            self.parseLine(line)
        except:
            pass

    def parseLine(self, line:str):
        line = line.strip()
        if line.startswith('Starting plotting progress into temporary dirs'):
            self.started = True
            self.t_start = time.time()
        elif line.startswith('ID: '):
            self.id = line.replace('ID: ', '')
        elif line.startswith('F1 complete, time: '):
            line_strip = line.replace('F1 complete, time: ', '')
            self.t_f1 = float(line_strip.split()[0])
        elif line.startswith('Time for phase 1 = '):
            line_strip = line.replace('Time for phase 1 = ', '')
            self.t_p1 = float(line_strip.split()[0])
        elif line.startswith('Time for phase 2 = '):
            line_strip = line.replace('Time for phase 2 = ', '')
            self.t_p2 = float(line_strip.split()[0])
        elif line.startswith('Time for phase 3 = '):
            line_strip = line.replace('Time for phase 3 = ', '')
            self.t_p3 = float(line_strip.split()[0])
        elif line.startswith('Time for phase 4 = '):
            line_strip = line.replace('Time for phase 4 = ', '')
            self.t_p4 = float(line_strip.split()[0])
        elif line.startswith('Total time = '):
            line_strip = line.replace('Total time = ', '')
            self.t_total = float(line_strip.split()[0])
        elif line.startswith('Copy time = '):
            line_strip = line.replace('Copy time = ', '')
            self.t_copy = float(line_strip.split()[0])
            self.end = True
            self.t_end = time.time()

    def toView(self):
        views = []

        t = time.localtime(self.t_start)
        tstr = time.strftime("%Y-%m-%d %H:%M:%S", t)
        item = QTableWidgetItem(tstr)
        views.append(item)
        item = QTableWidgetItem('%0.3fh' % (self.t_f1 / 3600.0))
        views.append(item)
        item = QTableWidgetItem('%0.3fh' % (self.t_p1 / 3600.0))
        views.append(item)
        item = QTableWidgetItem('%0.3fh' % (self.t_p2 / 3600.0))
        views.append(item)
        item = QTableWidgetItem('%0.3fh' % (self.t_p3 / 3600.0))
        views.append(item)
        item = QTableWidgetItem('%0.3fh' % (self.t_p4 / 3600.0))
        views.append(item)
        item = QTableWidgetItem('%0.3fh' % (self.t_total / 3600.0))
        views.append(item)
        item = QTableWidgetItem('%0.3fh' % (self.t_copy / 3600.0))
        views.append(item)
        item = QTableWidgetItem('%0.3fh' % ((self.t_total +self.t_copy) / 3600.0))
        views.append(item)

        return views

class PlotTask():
    def __init__(self, name:str, parg:PlotArg):
        self.name = name
        self.parg = parg
        self.startTime = time.time()
        self.plots = []
        self.process = None
        self.thread = None

    def taskProcess(self, name:str, parg:PlotArg):
        print(name, parg.toCmd())
        print(parg.arg_delay)
        time.sleep(parg.arg_delay)
        print('delay end')

        #chiapath = 'C:/Users/Administrator/AppData/Local/chia-blockchain/app-1.1.2/resources/app.asar.unpacked/daemon/'
        chiapath = ''
        cmd = '%schia plots create %s >>%s.log 2>&1' % (chiapath, parg.toCmd(), name)
        print(cmd)
        os.system(cmd)
        print(name, 'end')

    def threadStdRead(self):
        plotInfo = PlotInfo()
        self.plots.append(plotInfo)

        while True:
            time.sleep(1)
            try:
                f = open('%s.log'%self.name, 'r', encoding='utf-8')
                break
            except:
                #print('wait log open')
                pass
        #f = open('%s.log' % 'plot', 'r', encoding='utf-8')

        line_r = ''
        while self.thread is not None:
            try:
                line = f.readline()
                if line is not None and len(line) > 0:
                    line_r += line
                    if line_r.endswith('\n'):
                        plotInfo.rLine(line_r)
                        line_r = ''
                        if plotInfo.end:
                            plotInfo = PlotInfo()
                            self.plots.append(plotInfo)
                else:
                    time.sleep(0.5)
            except:
                print('line error')

    def start(self):
        self.process = Process(target=self.taskProcess, name='%s_subtask'%self.name, args=(self.name, self.parg))
        self.process.start()
        if self.thread is None:
            self.thread = threading.Thread(target=self.threadStdRead)
            self.thread.start()


    def pause(self):
        pass

    def stop(self):
        #self.process.terminate()
        #os.kill(self.process.pid, signal.SIGTERM)
        #self.process = None
        pass

    def info(self):
        pass

    def toView(self):
        views = []

        item = QTableWidgetItem(self.name)
        views.append(item)
        item = QTableWidgetItem(self.parg.arg_t)
        views.append(item)
        item = QTableWidgetItem(self.parg.arg_d)
        views.append(item)
        item = QTableWidgetItem(str(self.parg.arg_r))
        views.append(item)
        item = QTableWidgetItem(str(self.parg.arg_b))
        views.append(item)
        item = QTableWidgetItem(str(self.parg.arg_u))
        views.append(item)
        item = QTableWidgetItem(str(len(self.plots)))
        views.append(item)

        runTime = time.time() - self.startTime
        runTimeAvg = runTime/len(self.plots)
        item = QTableWidgetItem('%0.3fh'%(runTime/3600.0))
        views.append(item)
        item = QTableWidgetItem('%0.3fh'%(runTimeAvg/3600.0))
        views.append(item)

        if self.process.is_alive():
            item = QTableWidgetItem('Runing')
        else:
            item = QTableWidgetItem('Stoped')
        views.append(item)
        return views