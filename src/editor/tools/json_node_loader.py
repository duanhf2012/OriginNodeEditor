import json
import os


from vg_node import Node
from vg_node_port import NodeInput, NodeOutput
from vg_dtypes import VGDtypes
from tools.vg_tools import PrintHelper

# 导入所有支持的widget类
from widgets.PortWidget import StringInputWdg, IntInputWdg, FloatInputWdg, CheckboxWdg
from widgets.PortWidget import StringArrayWdg, IntegerArrayWdg

class JSONNodeLoader:
    # Widget名称到widget类的映射
    WIDGET_MAP = {
        'StringInputWdg': StringInputWdg,
        'IntInputWdg': IntInputWdg,
        'FloatInputWdg': FloatInputWdg,
        'CheckboxWdg': CheckboxWdg,
        'StringArrayWdg': StringArrayWdg,
        'IntegerArrayWdg': IntegerArrayWdg,
        # 可以继续添加其他widget映射
    }

    @staticmethod
    def _get_widget_class(widget_name):
        """根据widget名称获取widget类"""
        if widget_name is None:
            return None

        # 如果已经是类对象，直接返回
        if not isinstance(widget_name, str):
            return widget_name

        # 从映射中获取widget类
        return JSONNodeLoader.WIDGET_MAP.get(widget_name)

    @staticmethod
    def load_nodes_from_json(json_file_path):
        """从JSON文件加载节点定义"""
        if not os.path.exists(json_file_path):
            PrintHelper.printError(f"JSON节点文件不存在: {json_file_path}")
            return

        try:
            with open(json_file_path, 'r', encoding='utf-8') as f:
                node_definitions = json.load(f)

            for node_def in node_definitions:
                JSONNodeLoader.create_node_from_definition(node_def)

            PrintHelper.debugPrint(f"从 {json_file_path} 成功加载 {len(node_definitions)} 个节点定义")

        except Exception as e:
            PrintHelper.printError(f"加载JSON节点定义失败: {e}")

    @staticmethod
    def create_node_from_definition(node_def):
        """根据JSON定义创建节点类"""
        try:
            # 解析节点定义
            node_name = node_def.get('name', '')
            package_name = node_def.get('package', 'Custom Nodes')
            node_title = node_def.get('title', node_name)
            description = node_def.get('description', '')
            is_pure = node_def.get('is_pure', False)

            # 创建输入端口
            input_pins = []
            input_port_ids = set()  # 用于检测输入端口ID重复

            if not is_pure:
                input_pins.append(NodeInput(pin_type='exec'))

            for input_def in node_def.get('inputs', []):
                pin_name = input_def.get('name', '')
                pin_type = input_def.get('type', 'data')
                data_type = input_def.get('data_type', 'Any')
                has_input = input_def.get('has_input', True)
                pin_class = VGDtypes.get_dtype_by_name(data_type)

                # 获取端口ID配置
                port_id = input_def.get('port_id',None)
                # 检测输入端口ID重复
                if port_id is not None:
                    if port_id in input_port_ids:
                        PrintHelper.printError(f"节点 {node_title} 的输入端口ID重复: {port_id}")
                        return
                    input_port_ids.add(port_id)

                pin_widget = input_def.get('pin_widget', None)
                # 将字符串widget名称转换为widget类
                if pin_widget is not None:
                    pin_widget = JSONNodeLoader._get_widget_class(pin_widget)
                    if pin_widget is None:
                        PrintHelper.printError(f"未知的widget类型: {input_def.get('pin_widget')}")
                        pin_widget = None

                input_pins.append(NodeInput(
                    pin_name=pin_name,
                    pin_type=pin_type,
                    pin_class=pin_class,
                    has_input=has_input,
                    pin_widget=pin_widget,
                    port_id=port_id  # 传递端口ID配置
                ))

            # 创建输出端口
            output_pins = []
            output_port_ids = set()  # 用于检测输出端口ID重复
            if not is_pure:
                output_pins.append(NodeOutput(pin_type='exec'))

            for output_def in node_def.get('outputs', []):
                pin_name = output_def.get('name', '')
                pin_type = output_def.get('type', 'data')
                data_type = output_def.get('data_type', 'Any')
                hide_icon = output_def.get('hide_icon', False)  # 获取hide_icon属性
                port_id = output_def.get('port_id', None)  # 获取端口ID配置

                # 检测输出端口ID重复
                if port_id is not None:
                    if port_id in output_port_ids:
                        PrintHelper.printError(f"节点 {node_title} 的输出端口ID重复: {port_id}")
                        return  # 跳过重复的端口
                    output_port_ids.add(port_id)

                pin_class = VGDtypes.get_dtype_by_name(data_type)

                output_pins.append(NodeOutput(
                    pin_name=pin_name,
                    pin_type=pin_type,
                    pin_class=pin_class,
                    hide_icon=hide_icon,  # 传递hide_icon参数
                    port_id=port_id  # 传递端口ID配置
                ))

            # 创建节点类
            node_cls = type(node_name, (Node,), {
                'package_name': package_name,
                'node_title': node_title,
                'node_description': description,
                'is_pure': is_pure,
                'input_pins': input_pins,
                'output_pins': output_pins,
                'stored': True
            })

            # 注册节点
            cls_name = f'tools.json_node_loader.{node_name}'
            from vg_env import VG_ENV
            VG_ENV.add_cls_to_lib(cls_name, node_cls)

            PrintHelper.debugPrint(f"创建JSON节点: {node_title}")

        except Exception as e:
            PrintHelper.printError(f"创建节点 {node_def.get('name', 'unknown')} 失败: {e}")

    @staticmethod
    def load_all_json_nodes(json_dir='./json'):
        """加载指定目录下的所有JSON节点定义文件"""
        if not os.path.exists(json_dir):
            os.makedirs(json_dir)
            PrintHelper.debugPrint(f"创建JSON节点目录: {json_dir}")
            return

        root_dir = "./json"  # 根目录设置为 ./json
        # 递归遍历所有目录及子目录
        for dirpath, _, filenames in os.walk(root_dir):
            for filename in filenames:
                # 筛选 .json 后缀的文件
                if filename.lower().endswith(".json"):
                    file_path = os.path.join(dirpath, filename)
                    JSONNodeLoader.load_nodes_from_json(file_path)

        # for filename in os.listdir(json_dir):
        #     if filename.endswith('.json'):
        #         json_path = os.path.join(json_dir, filename)
        #         JSONNodeLoader.load_nodes_from_json(json_path)