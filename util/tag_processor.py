"""读取tag_sc_map.csv并提供将tag翻译成中文的功能"""
import csv
import os
import logging

from typing import Optional
from avdc.config import Config
from avdc.util.file_mgmt import get_project_root

CSV_FNAME = "data/tag_sc_map.csv"

tag_dict = {}
ignore_tag = set()
known_tag = set()

def __parse_sc_map():
    logging.debug('试图载入标签文件。')
    csv_path = os.path.join(get_project_root(), CSV_FNAME)
    with open(csv_path, 'r') as f:
        tagreader = csv.reader(f)
        headers = next(tagreader)
        for row in tagreader:
            if len(row) < 2:
                continue
            tag = row[0].strip()
            target = row[1].strip()
            if target == '删除':
                ignore_tag.add(tag)
            elif tag in tag_dict:
                logging.warn(f'重复标签 {tag}')
            else:
                tag_dict[tag] = target
                known_tag.add(target)

    logging.debug(f'成功载入标签{tag_dict}')
    logging.debug(f'成功载入忽略标签{ignore_tag}')

def __translate_tag_to_sc(tag: str) -> Optional[str]:
    if not tag_dict:
        __parse_sc_map()

    if tag in ignore_tag:
        return None
    elif tag in tag_dict:
        return tag_dict[tag]
    elif tag in known_tag:
        return tag
    else:
        logging.warn(f'缺失标签 {tag}')
        return tag

def process_tags(tags: [str]) -> [str]:
    config = Config.get_instance()
    translate_to_sc = config.translate_to_sc()

    tags = [i.strip() for i in tags]
    tags = [i for i in tags if i]
    logging.debug(f'输入标签 {tags}')
    if translate_to_sc:
        tags = [__translate_tag_to_sc(t) for t in tags]
        tags = [i for i in tags if i]
    output = list(set(tags))
    logging.debug(f'输出标签 {output}')
    return output
