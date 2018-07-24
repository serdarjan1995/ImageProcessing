import os
import glob
import pandas as pd
import xml.etree.ElementTree as ET


def xml_to_csv(folder):
    xml_list = []
    for path in glob.glob(folder+'/*'):
        for xml_file in glob.glob(path + '/*.xml'):
            print(xml_file)
            tree = ET.parse(xml_file)
            root = tree.getroot()
            for member in root.findall('object'):
                value = (path+'/'+root.find('filename').text,
    #                     int(root.find('size')[0].text),
    #                     int(root.find('size')[1].text),
                         
                         int(member[4][0].text),
                         int(member[4][1].text),
                         int(member[4][2].text),
                         int(member[4][3].text),
                         member[0].text
                         )
                xml_list.append(value)
#    column_name = ['filename', 'width', 'height', 'class', 'xmin', 'ymin', 'xmax', 'ymax']
    column_name = ['filename', 'xmin', 'ymin', 'xmax', 'ymax', 'class']
#    print(xml_list)
    xml_df = pd.DataFrame(xml_list)
    return xml_df


def main():
    for folder in ['data/train','data/valid']:
        print('#'+folder)
        xml_df = xml_to_csv(folder)
        xml_df.to_csv((folder + '_labels.csv'), index=None,header=False)


main()
