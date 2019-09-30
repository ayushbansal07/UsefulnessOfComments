import sys
import xml.etree.ElementTree as ET
import pandas as pd
import numpy as np


def getKnowledgeBase(knowledge_base_path):
    csv_file = pd.read_csv(knowledge_base_path)
    csv_np = np.array(csv_file)
    knowledge_base = []
    for comment in csv_np:
        if "Copyright (c)" in comment[2]:
            continue
        else:
            knowledge_base.append([comment[2], comment[4], comment[7], comment[8], comment[15]])
    return knowledge_base

def createXML(project_name, project_path, file_name, file_location, knowledge_base_path, output_xml_file):
    root = ET.Element('COMMENTS')
    root.set('project_name', project_name)
    root.set('project_path', project_path)
    root.set('file_name', file_name)
    root.set('file_path', file_location)
    knowledge_base = getKnowledgeBase(knowledge_base_path)
    for comment in knowledge_base:
        comment_node = ET.SubElement(root, 'COMMENT')

        comment_node.set('comment_text', comment[0])
        scope = comment[1].split(":")
        assert len(scope) == 2, "Scope does not contain exactly 2 integers!"
        comment_node.set('comment_scope_start', scope[0].strip())
        comment_node.set('comment_scope_end', scope[1].strip())
        if comment[2] != comment[2]:
            continue
        identifier_symbols = comment[2].split(" |||")
        identifier_symbols = [x.strip() for x in identifier_symbols]
        identifier_types = comment[3].split(" |||")
        identifier_ids = comment[4].split(" |||")
        identifier_ids = [x.strip() for x in identifier_ids]
        assert len(identifier_symbols) == len(identifier_types), ("Length of identifier_symbols and identifier_types DONOT match!", len(identifier_symbols), len(identifier_types))

        for i in range(len(identifier_symbols)):
            identifier_type = identifier_types[i].split(":")
            identifier_type = [x.strip() for x in identifier_type]
            identifier_node = ET.SubElement(comment_node, identifier_type[0])
            identifier_node.set('type', identifier_type[1])
            identifier_node.set('spelling', identifier_symbols[i])
            identifier_node.set('id', identifier_ids[i])

    xml_data = ET.tostring(root)
    with open(output_xml_file,'wb') as f:
        f.write(xml_data)

if len(sys.argv) != 7:
    print "Give 6 Arguments: project_name, project_path, file_name, file_location, knowledge_base_path, output_xml_file"
    exit(-1)

createXML(sys.argv[1],sys.argv[2],sys.argv[3],sys.argv[4], sys.argv[5], sys.argv[6])
exit(0)
