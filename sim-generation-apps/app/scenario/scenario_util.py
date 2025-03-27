import re
import xml.etree.ElementTree as ET
import xml.dom.minidom as minidom

def save_xml_data(root, output_path):
    xml_data = ET.tostring(root, encoding='unicode')
    # xmlデータのフォーマットを整える
    reparsed = minidom.parseString(xml_data)
    pretty_string = reparsed.toprettyxml(indent="    ")
    pretty_string = "\n".join([line for line in pretty_string.split('\n') if line.strip()])

    # 修正されたXMLデータをファイルに保存
    with open(output_path, "w", encoding='utf-8') as file:
        file.write(pretty_string)
    

def extract_number_from_filename(filename):
    if "route" not in filename:
        return None
    
    if "self" in filename:
        return "self"
    else:
        match = re.search(r'_(\d+)+', filename)
        if match:
            return match.group(1)
    return None

def find_object_id(root, tag):
    objects = root.find('space').find('objects')
    for object_node in objects.findall('object'):
        id = object_node.get('id')
        if tag in id:
            return id
    
    return None

def get_current_event_id(event_root):
    entitys = event_root.findall('entity')
    id_list = []
    for entity in entitys:
        event = entity.find('event')
        if event is None:
            continue

        event_id_str = event.get('id')
        if event_id_str is None:
            continue

        match = re.search(r'_(\d+)+', event_id_str)
        if match:
            id_list.append(int(match.group(1)))

    # 空いているIDを探す
    max_id = max(id_list)
    for id in range(1, max_id):
        if id not in id_list:
            return str(id)
    return max_id + 1

def get_current_action_id(entity_root):
    actinos = entity_root.find('event').findall('action')
    id_list = []
    for action in actinos:

        action_idx = action.get('index')
        if action_idx is None:
            continue

        id_list.append(int(action_idx))

    # 空いているIDを探す
    max_id = max(id_list)
    for id in range(1, max_id):
        if id not in id_list:
            return str(id)
    return max_id + 1
            

def create_initialize_entity(object_id: str, event_id: int, route_id: str):
    init_entity = ET.fromstring(
        f'''
        <entity id="{object_id}" type="object">
            <event id="event_{event_id}" index="0">
                <action index="0">
                    <position x="0.0000000000" y="0.0000000000" z="0.0000000000"/>
                </action>
                <action index="1">
                    <attitude x="0.0000000000" y="0.0000000000" z="0.0000000000"/>
                </action>
                <action index="2">
                    <route id="{route_id}"/>
                </action>
            </event>
        </entity>
        '''
    )
    return init_entity

def create_execution_entity(object_id: str, event_id: int, index):
    execute_entity = ET.fromstring(
        f'''
        <entity id="{object_id}" type="object">
            <event id="event_{event_id}" index="{index}">
            </event>
        </entity>
        '''
    )
    return execute_entity

def set_action_value(entity_tree, event_type, x=0, y=0, z=0, speed=0):
    event = entity_tree.find('event')
    for action in event.findall('action'):
        action_type = action.find(event_type)
        if action_type is None:
            continue
        if event_type == "position" or event_type == "attitude":
            if action_type.get('x') is None or \
               action_type.get('y') is None or \
               action_type.get('z') is None:
                continue
            
            # set value
            action_type.set('x', str(x))
            action_type.set('y', str(y))
            action_type.set('z', str(z))
            return
        elif event_type == "speed":
            if action_type.get('value') is None:
                continue
            # set value is speed divided by 3.6
            action_type.set('value', str(speed / 3.6))
            return

def print_tree(element: ET.Element, level=0):
    indent = "  " * level
    print(f"{indent}{element.tag}: {element.attrib}")
    for child in element:
        print_tree(child, level + 1)