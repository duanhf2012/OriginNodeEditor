#coding:utf-8
'''
visual graph的入口

'''

import sys
from PySide6.QtGui import QIcon
from PySide6.QtCore import QThread
from PySide6.QtWidgets import QApplication
from vg_editor import VisualGraphWindow
from tools.vg_tools import EmittingStream, PrintHelper,StdReceiver
from tools.QssLoader import QSSLoadTool,resource_path
from tools.json_node_loader import JSONNodeLoader

if __name__ == "__main__":
    app = QApplication([])
    app.setStyle('fusion')
    QSSLoadTool.setStyleSheetFile(app,'./src/editor/qss/main.qss')

    # 在适当的位置添加JSON节点加载
    JSONNodeLoader.load_all_json_nodes('./json')

    try:
        editor = VisualGraphWindow()
        editor.setWindowIcon(QIcon(resource_path('./src/editor/icons/icon.ico'))) 
        editor.show()
    except ValueError as e:
        PrintHelper.printError(e)

    sys.exit(app.exec())
