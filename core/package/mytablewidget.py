# -*- coding: utf-8 -*-

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import traceback
from functools import partial


# class MyTableWidget(QTableWidget):
#     update_table_tooltip_signal = pyqtSignal(object)
#
#     def __init__(self, row, col):
#         super(MyTableWidget, self).__init__()
#         self.setRowCount(row)
#         self.setColumnCount(col)
#         self.ini_table()
#
#     def ini_table(self):
#         """---------初始化表格的常用选项(按需修改)------------"""
#         QTableWidget.resizeColumnsToContents(self)
#         QTableWidget.resizeRowsToContents(self)
#         self.setSelectionMode(QAbstractItemView.NoSelection)
#         self.horizontalHeader().setSectionResizeMode(
#             QHeaderView.Stretch)  # 列宽自动分配
#         self.verticalHeader().setSectionResizeMode(
#             QHeaderView.Stretch)  # 行高自动分配
#         # self.verticalHeader().stretchLastSection()                         #自动拓展最后一行适应表格高度
#         self.horizontalHeader().setVisible(False)
#         self.verticalHeader().setVisible(False)
#         self.setEditTriggers(QAbstractItemView.NoEditTriggers)
#
#         """------------关键代码--------------"""
#         self.vertical_scrollbar = QScrollBar()
#         self.horizon_scrollbar = QScrollBar()
#         self.vertical_scrollbar.valueChanged.connect(
#             partial(self.scollbar_change_slot, "vertical"))
#         self.horizon_scrollbar.valueChanged.connect(
#             partial(self.scollbar_change_slot, "horizon"))
#         self.setVerticalScrollBar(self.vertical_scrollbar)
#         self.setHorizontalScrollBar(self.horizon_scrollbar)
#         self.init_row = 0
#         self.init_col = 0
#         self.tool_tip = ""
#         self.update_table_tooltip_signal.connect(
#             self.update_table_tooltip_slot)
#         self.title_row_height = 0
#
#     # 设置表格列标题
#     def set_horizon_title(self, title_list):
#         self.horizontalHeader().setDefaultAlignment(Qt.AlignLeft)
#         self.horizontalHeader().setVisible(True)
#         col = 0
#         for item in title_list:
#             item = QTableWidgetItem(str(item))
#             item.setSizeHint(QSize(200, 45))  # 这里默认设置了列标题的宽和高分别为200、45,可根据需要修改
#             self.setHorizontalHeaderItem(col, item)
#             col += 1
#
#         self.title_row_height = 45  # (关键值)这里的值设置为列标题高
#
#     # 为TableWidget安装事件过滤器
#     def install_eventFilter(self):
#         self.installEventFilter(self)
#         self.setMouseTracking(True)
#
#     # 改变滚动条时重置当前页面的初始行和列
#     def scollbar_change_slot(self, type):
#         if type == "vertical":
#             value = self.verticalScrollBar().value()
#             self.init_row = value
#             # print("垂直滚动条当前的值为:",value)
#             # print("当前页面的起始行为:",self.init_row)
#         else:
#             value = self.horizontalScrollBar().value()
#             self.init_col = value
#             # print("水平滚动条当前的值为:",value)
#             # print("当前页面的起始列为:",self.init_col)
#
#     # 通过计算坐标确定当前位置所属单元格
#     def update_table_tooltip_slot(self, posit):
#         self.tool_tip = ""
#         self.mouse_x = posit.x()
#         self.mouse_y = posit.y()
#         self.row_height = self.title_row_height  # 累计行高,初始值为列标题行高
#         for r in range(self.rowCount()):
#             current_row_height = self.rowHeight(r)
#             self.col_width = 0  # 累计列宽
#             if self.row_height <= self.mouse_y <= self.row_height + current_row_height:
#                 for c in range(self.columnCount()):
#                     current_col_width = self.columnWidth(c)
#                     if self.col_width <= self.mouse_x <= self.col_width + current_col_width:
#                         r = self.init_row + r
#                         c = self.init_col + c
#                         print("鼠标当前所在的行和列为:({},{})".format(r, c))
#                         item = self.item(r, c)
#                         if item != None:
#                             self.tool_tip = item.text()
#                         else:
#                             self.tool_tip = ""
#                         return self.tool_tip
#                     else:
#                         self.col_width = self.col_width + current_col_width
#             else:
#                 if self.mouse_y < self.row_height:
#                     break
#                 else:
#                     self.row_height = self.row_height + current_row_height
#
#     # 事件过滤器
#     def eventFilter(self, object, event):
#         try:
#             if event.type() == QEvent.ToolTip:
#                 self.setCursor(Qt.ArrowCursor)
#                 print("当前鼠标位置为:", event.pos())
#                 self.update_table_tooltip_signal.emit(event.pos())
#                 # 设置提示气泡显示范围矩形框,当鼠标离开该区域则ToolTip消失
#                 rect = QRect(self.mouse_x, self.mouse_y, 30,
#                              10)  # QRect(x,y,width,height)
#                 # 设置QSS样式
#                 self.setStyleSheet(
#                     """QToolTip{border:10px;
#                        border-top-left-radius:5px;
#                        border-top-right-radius:5px;
#                        border-bottom-left-radius:5px;
#                        border-bottom-right-radius:5px;
#                        background:#4F4F4F;
#                        color:#00BFFF;
#                        font-size:18px;
#                        font-family:"微软雅黑";
#                     }""")
#                 QApplication.processEvents()
#                 # 在指定位置展示ToolTip
#                 QToolTip.showText(QCursor.pos(), self.tool_tip, self, rect,
#                                   1500)
#
#                 """
#                 showText(QPoint, str, QWidget, QRect, int)
#                 #############参数详解###########
#                 #QPoint指定tooptip显示的绝对坐标,QCursor.pos()返回当前鼠标所在位置
#                 #str为设定的tooptip
#                 #QWidget为要展示tooltip的控件
#                 #QRect指定tooltip显示的矩形框范围,当鼠标移出该范围,tooltip隐藏,使用该参数必须指定Qwidget!
#                 #int用于指定tooltip显示的时长(毫秒)
#                 """
#             return QWidget.eventFilter(self, object, event)
#         except Exception as e:
#             traceback.print_exc()

class MyTableWidget(QTableWidget):
    def __init__(self):
        super(MyTableWidget, self).__init__()

    def showToolTip(self, index):
        """
        提示完整文本信息
        :param index: QModelIndex
        :return:
        """
        if index.isValid():
            QToolTip.showText(QCursor.pos(), str(index.data()))
