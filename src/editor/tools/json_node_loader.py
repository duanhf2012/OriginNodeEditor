import json
import os


from vg_node import Node
from vg_node_port import NodeInput, NodeOutput
from vg_dtypes import VGDtypes
from tools.vg_tools import PrintHelper


class JSONNodeLoader:
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
            if not is_pure:
                input_pins.append(NodeInput(pin_type='exec'))

            for input_def in node_def.get('inputs', []):
                pin_name = input_def.get('name', '')
                pin_type = input_def.get('type', 'data')
                data_type = input_def.get('data_type', 'Any')
                has_input = input_def.get('has_input', True)

                pin_class = VGDtypes.get_dtype_by_name(data_type)

                input_pins.append(NodeInput(
                    pin_name=pin_name,
                    pin_type=pin_type,
                    pin_class=pin_class,
                    has_input=has_input
                ))

            # 创建输出端口
            output_pins = []
            if not is_pure:
                output_pins.append(NodeOutput(pin_type='exec'))

            for output_def in node_def.get('outputs', []):
                pin_name = output_def.get('name', '')
                pin_type = output_def.get('type', 'data')
                data_type = output_def.get('data_type', 'Any')

                pin_class = VGDtypes.get_dtype_by_name(data_type)

                output_pins.append(NodeOutput(
                    pin_name=pin_name,
                    pin_type=pin_type,
                    pin_class=pin_class
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
            cls_name = f'json_nodes.{node_name}'
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

        for filename in os.listdir(json_dir):
            if filename.endswith('.json'):
                json_path = os.path.join(json_dir, filename)
                JSONNodeLoader.load_nodes_from_json(json_path)