"""读取tag_sc_map.csv并提供将tag翻译成中文的功能"""
import csv
import os
import logging

from typing import Optional
from avdc.config import Config
from avdc.util.project_root import get_project_root
from typing import List

CSV_FNAME = "data/tag_sc_map.csv"

tag_dict = {}
ignore_tag = set()
known_tag = set()

def __parse_sc_map():
    logging.debug('试图载入标签文件。')
    csv_path = os.path.join(get_project_root(), CSV_FNAME)
    with open(csv_path, 'r') as f:
        tagreader = csv.reader(f)
        _ = next(tagreader) # 第一行是header
        for first, *rest in tagreader:
            first = first.strip()
            if first != '删除':
                tag_dict[first] = first
                
            for tag in rest:
                tag = tag.strip()
                if first == '删除':
                    ignore_tag.add(tag)
                elif tag in tag_dict:
                    logging.warn(f'发现重复标签 {tag}')
                else:
                    tag_dict[tag] = first

    logging.debug(f'成功载入标签{tag_dict}')
    logging.debug(f'成功载入忽略标签{ignore_tag}')

def __translate_tag_to_sc(tag: str) -> str:
    if not tag_dict:
        __parse_sc_map()

    if tag in ignore_tag:
        return ''
    elif tag in tag_dict:
        return tag_dict[tag]
    else:
        logging.warn(f'缺失标签 {tag}')
        return tag

def process_tags(tags: List[str]) -> List[str]:
    config = Config.get_instance()
    translate_to_sc = config.translate_to_sc()
    
    tags = [i.strip() for i in tags]
    tags = [i for i in tags if i]
    
    if translate_to_sc:
        tags = [__translate_tag_to_sc(t) for t in tags]
        tags = [t for t in tags if t]

    output = list(set(tags))
    return output
