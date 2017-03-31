import xml.etree.ElementTree as ET

def parseXML(f):
    tree = ET.parse(f)
    root = tree.getroot()
    
    # xmlstr = ET.tostring(root, encoding='utf8', method='xml')
    # print(xmlstr)
    ER = {}
    ER['entity'] = [];
    for entity in root.findall('entity'):
        temp_entity = {}
        temp_entity['id'] = entity.attrib['id']
        temp_entity['name'] = entity.attrib['name']
        temp_entity['attribute'] = []
        for attribute in entity.findall('attribute'):
            temp_attribute = {}
            temp_attribute['id'] = attribute.attrib['id'];
            if 'name' in attribute.attrib:
                temp_attribute['name'] = attribute.attrib['name'];
            if 'type' in attribute.attrib:
                temp_attribute['type'] = attribute.attrib['type'];
            if 'relation_id' in attribute.attrib:
                temp_attribute['relation_id'] = attribute.attrib['relation_id'];
            temp_entity['attribute'].append(temp_attribute)
        temp_entity['key'] = []
        for key in entity.findall('key'):
            temp_entity['key'].append(key.text.split(','))
        ER['entity'].append(temp_entity)

    ER['relation'] = [];
    for entity in root.findall('relationship'):
        temp_relation = {}
        temp_relation['id'] = entity.attrib['id']
        temp_relation['name'] = entity.attrib['name']
        temp_relation['attribute'] = [];
        for attribute in entity.findall('attribute'):
            temp_attribute = {}
            if 'name' in attribute.attrib:
                temp_attribute['name'] = attribute.attrib['name'];
            if 'entity_id' in attribute.attrib:
                temp_attribute['entity_id'] = attribute.attrib['entity_id'];
            if 'relation_id' in attribute.attrib:
                temp_attribute['relation_id'] = attribute.attrib['relation_id'];
            if 'min_participation' in attribute.attrib:
                temp_attribute['min_participation'] = attribute.attrib['min_participation'];
            if 'max_participation' in attribute.attrib:
                temp_attribute['max_participation'] = attribute.attrib['max_participation'];
            temp_relation['attribute'].append(temp_attribute)
        ER['relation'].append(temp_relation)
    return ER

