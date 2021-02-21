"""读取tag_sc_map.csv并提供将tag翻译成中文的功能"""
import os
from avdc.util.logging_config import get_logger

from avdc.config import Config
from avdc.util.project_root import get_project_root
from avdc.util.csv_utils import read_csv

CSV_FNAME = os.path.join('data','tag_sc_map.csv')
logger = get_logger(__name__)

tag_dict = {}
ignore_tag = set()
known_tag = set()
unknown_tag = set()


def process_tags(tags: list[str]) -> list[str]:
    config = Config.get_instance()
    translate_to_sc = config.translate_to_sc()

    tags = [i.strip() for i in tags]
    tags = [i for i in tags if i]

    if translate_to_sc:
        tags = [translate_tag_to_sc(t) for t in tags]
        tags = [t for t in tags if t]

    output = list(set(tags))
    return output

def _parse_sc_map():
    csv_path = os.path.join(get_project_root(), CSV_FNAME)
    logger.debug(f'试图载入标签文件: {csv_path}')
    for row in read_csv(csv_path):
        first, *rest = row
        if first != '删除':
            tag_dict[first] = first

        for tag in rest:
            tag = tag.strip()
            if first == '删除':
                ignore_tag.add(tag)
            elif tag in tag_dict:
                logger.warn(f'发现重复标签 {tag}')
            else:
                tag_dict[tag] = first

    logger.debug(f'成功载入{len(tag_dict)}个标签映射。')
    logger.debug(f'成功载入{len(ignore_tag)}个忽略标签。')

def debug_unknown_tags():
    for tag in unknown_tag:
        logger.debug(f'未登记标签 {tag}')


def translate_tag_to_sc(tag: str) -> str:
    if not tag_dict:
        _parse_sc_map()

    if tag in ignore_tag:
        return ''
    elif tag in tag_dict:
        return tag_dict[tag]
    else:
        unknown_tag.add(tag)
        return tag
