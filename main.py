import datetime
import multiprocessing
import os
import sys
import threading
import time
import webbrowser

import psutil as psutil
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QTextCursor
from PyQt5.QtWidgets import QDialog, QHeaderView, QTableWidgetItem, QFileDialog

from log import logger
from mainwindow_ui import Ui_mainwindow



# pyrcc5 -o mainwindow_rc.py ./resources/mainwindow.qrc
# pyuic5 -o mainwindow_ui.py ./resources/mainwindow.ui
# pyinstaller -F main.py -i ./start.ico
from plot import PlotArg, PlotTask


class MainWindow(QDialog, Ui_mainwindow):
    _table_signal = QtCore.pyqtSignal(str)

    def __init__(self):
        QDialog.__init__(self)
        Ui_mainwindow.__init__(self)
        self.setupUi(self)
        self.setWindowFlags(Qt.WindowMinimizeButtonHint | Qt.WindowMaximizeButtonHint | Qt.WindowCloseButtonHint)

        self.bt_taskRun.clicked.connect(self.bt_taskRun_clicked)
        self.bt_taskStop.clicked.connect(self.bt_taskStop_clicked)
        self.table_task.currentItemChanged.connect(self.tb_plot_update)
        self.table_plot.currentItemChanged.connect(self.text_info_update)
        self._table_signal.connect(self.tableUpdate)

        self.le_arg_toView(PlotArg())

        self.ptasks = []
        threading.Thread(target=self.threadTableUpdate).start()



    def le_arg_toView(self, parg:PlotArg):
        self.le_k.setText(str(parg.arg_k))
        self.le_u.setText(str(parg.arg_u))
        self.le_b.setText(str(parg.arg_b))
        self.le_r.setText(str(parg.arg_r))
        self.le_n.setText(str(parg.arg_n))
        self.le_t.setText(parg.arg_t)
        self.le_d.setText(parg.arg_d)
        self.le_delay.setText(str(parg.arg_delay))


    def le_arg_fromView(self):
        k = int(self.le_k.text())
        u = int(self.le_u.text())
        b = int(self.le_b.text())
        r = int(self.le_r.text())
        n = int(self.le_n.text())
        t = (self.le_t.text())
        d = (self.le_d.text())
        delay = int(self.le_delay.text())
        return PlotArg(k, u, b, r, n, t, d, delay)

    def tb_task_update(self):
        self.table_task.setRowCount(len(self.ptasks))
        for i, ptask in enumerate(self.ptasks):
            vs = ptask.toView()
            for j, v in enumerate(vs):
                if type(v) is QTableWidgetItem:
                    self.table_task.setItem(i, j, v)
                else:
                    self.table_task.setCellWidget(i, j, v)

        self.table_task.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
        self.table_task.resizeColumnsToContents()
        self.table_task.resizeRowsToContents()

    def tb_plot_update(self, QModelIndex=None, QModelIndex_1=None):
        row = self.table_task.currentRow()
        if row < 0:
            self.table_plot.setRowCount(0)
            return None

        plots = self.ptasks[row].plots
        self.table_plot.setRowCount(len(plots))
        for i, plot in enumerate(plots):
            vs = plot.toView()
            for j, v in enumerate(vs):
                if type(v) is QTableWidgetItem:
                    self.table_plot.setItem(i, j, v)
                else:
                    self.table_plot.setCellWidget(i, j, v)

        self.table_plot.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
        self.table_plot.resizeColumnsToContents()
        self.table_plot.resizeRowsToContents()

    def text_info_update(self, QModelIndex=None, QModelIndex_1=None):
        row = self.table_task.currentRow()
        if row < 0:
            self.table_plot.setRowCount(0)
            return None
        plots = self.ptasks[row].plots

        row = self.table_plot.currentRow()
        self.text_info.setText('')
        if row < 0:
            return None
        plot = plots[row]

        self.text_info.setText(plot.lines)
        self.text_info.moveCursor(QTextCursor.End)

    def threadTableUpdate(self):
        while True:
            time.sleep(2)
            self._table_signal.emit('')

    def tableUpdate(self):
        self.tb_task_update()
        self.tb_plot_update()
        self.text_info_update()

    def bt_taskRun_clicked(self):
        parg = self.le_arg_fromView()
        print(parg.toCmd())
        tcmd = datetime.datetime.now().strftime('%Y_%m_%d-%H_%M_%S')
        ptask = PlotTask('ptask_'+tcmd, parg)
        ptask.start()
        self.ptasks.append(ptask)
        self.tb_task_update()


    def bt_taskStop_clicked(self):
        row = self.table_task.currentRow()
        ptask = self.ptasks[row]
        ptask.stop()




if __name__ == '__main__':
    import cgitb
    multiprocessing.freeze_support()
    cgitb.enable(format='text')

    logger.info('start')
    app = QtWidgets.QApplication(sys.argv)
    mainWin = MainWindow()
    mainWin.show()
    sys.exit(app.exec_())