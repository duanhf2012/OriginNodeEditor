#coding:utf-8
'''
需要重新定义Types,定义转化函数
'''

from PySide6.QtGui import QIcon, QPainter, QPixmap, QColor

from pandas import DataFrame

from widgets.PortWidget import StringInputWdg, IntInputWdg, FloatInputWdg, CheckboxWdg
from widgets.NodeWidget import TablePreviewWidget
import os
import sys
import pandas as pd

class Vector:

    def __init__(self,x,y):
        self.x = x
        self.y = y

    def __repr__(self) -> str:
        return f'Vector({self.x},{self.y})'

class File:


    def __repr__(self) -> str:
        return f'File object<>'

class DataFrame(pd.DataFrame):

    def __repr__(self) -> str:
        return f'Table Object'
    
    

class Column:
    def __repr__(self) -> str:
        return f'Column Object'


class Any:
    def __repr__(self) -> str:
        return str(self)


class VGDtypes:

    # 数据类型
    Integer = int
    Bool = bool
    Float = float
    String = str
    Array = list
    Dict = dict
    Class = object
    Vector = Vector
    File = File
    Table = DataFrame
    Column = Column
    Any = Any

    dtypes = [
        Integer,
        Bool,
        Float,
        String,
        Array,
        Dict,
        Class,
        Vector,
        File,
        Table,
        Column,
        Any
    ]

    Color_Map = {
        Float.__name__: '#2fFF09',
        Integer.__name__: '#008000',
        Bool.__name__: '#ff0606',
        String.__name__: '#be0ba0',
        Array.__name__: '#d4aa24',
        Dict.__name__: '#ed6c03',
        Class.__name__: '#0747bb',
        Vector.__name__: '#055c54',
        File.__name__: '#b92ee6',
        Table.__name__: '#00BFFF',
        Column.__name__: '#00FFFF',
        Any.__name__:'#fff'
    }

    dtypes_clses = {
        Float.__name__: Float,
        Integer.__name__: Integer,
        Bool.__name__: Bool,
        String.__name__: String,
        Array.__name__: Array,
        Dict.__name__: Dict,
        Class.__name__: Class,
        Vector.__name__: Vector,
        File.__name__: File,
        Table.__name__: Table,
        Column.__name__: Column,
        Any.__name__: Any
    }

    @staticmethod
    def get_dtype_color(dtype):
        if not isinstance(dtype, str):
            dtype = dtype.__name__

        return VGDtypes.Color_Map.get(dtype, '#0747bb')

    default_widget = {
        int: IntInputWdg,
        bool: CheckboxWdg,
        str: StringInputWdg,
        float: FloatInputWdg
    }

    preview_widget = {
        DataFrame: TablePreviewWidget
    }

    @staticmethod
    def getPreviewWdgByClass(port_class):
        return VGDtypes.preview_widget.get(port_class,None)

    @staticmethod
    def get_default_value(type):
        if type == VGDtypes.Integer:
            return 0
        elif type == VGDtypes.Float:
            return 0.0
        elif type == VGDtypes.String:
            return ''
        elif type == VGDtypes.Array:
            return []
        elif type == VGDtypes.Dict:
            return {}
        elif type == VGDtypes.Class:
            return None
        elif type == VGDtypes.Vector:
            return [0, 0]
        elif type == VGDtypes.File:
            return None
        elif type == VGDtypes.Bool:
            return False
        else:
            return None

    @staticmethod
    def get_cls_icon(dtype) -> QIcon:
        pixmap = QPixmap(resource_path('./src/editor/icons/white_cls.png'))
        painter = QPainter(pixmap)
        painter.setCompositionMode(QPainter.CompositionMode_SourceIn)

        color = QColor(VGDtypes.get_dtype_color(dtype))
        painter.setBrush(color)
        painter.setPen(color)

        painter.drawRect(pixmap.rect())
        painter.end()

        return QIcon(pixmap)

    @staticmethod
    def get_dtypes_icons():
        data = []
        for dtype in VGDtypes.Color_Map.keys():

            dtype_name = dtype
            if not isinstance(dtype, str):
                dtype_name = dtype.__name__

            data.append({
                'icon': VGDtypes.get_cls_icon(dtype),
                'value': dtype_name
            })

        return data

    @staticmethod
    def get_dtype_by_name(dtype_name):
        """根据数据类型名称获取对应的数据类型类"""
        # 处理大小写不敏感的情况
        dtype_name = dtype_name.lower()

        # 映射数据类型名称到对应的类
        dtype_map = {
            'int': VGDtypes.Integer,
            'integer': VGDtypes.Integer,
            'bool': VGDtypes.Bool,
            'boolean': VGDtypes.Bool,
            'float': VGDtypes.Float,
            'double': VGDtypes.Float,
            'str': VGDtypes.String,
            'string': VGDtypes.String,
            'list': VGDtypes.Array,
            'array': VGDtypes.Array,
            'dict': VGDtypes.Dict,
            'dictionary': VGDtypes.Dict,
            'class': VGDtypes.Class,
            'object': VGDtypes.Class,
            'vector': VGDtypes.Vector,
            'file': VGDtypes.File,
            'table': VGDtypes.Table,
            'dataframe': VGDtypes.Table,
            'column': VGDtypes.Column,
            'any': VGDtypes.Any
        }

        # 返回对应的数据类型类，如果找不到则返回Any类型
        return dtype_map.get(dtype_name, VGDtypes.Any)

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    path = os.path.join(base_path, relative_path)
    return path
