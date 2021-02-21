"""读取 actor_dupe_map.csv中的数据并提供女优映射。"""

import logging
import os

from avdc.util.csv_utils import read_csv
from avdc.util.project_root import get_project_root

CSV_FNAME = 'data/actor_dupe_map.csv'

actor_map = {}
logger = logging.getLogger(__name__)


def process_actors(actors: list[str]) -> list[str]:
    """输入女优列表，输出重名映射过的女优列表。"""
    return [_process_actor(a) for a in actors]


def _parse_actor_map():
    logger.debug('试图载入女优查重文件。')
    csv_path = os.path.join(get_project_root(), CSV_FNAME)

    for row in read_csv(csv_path):
        first, *rest = row
        for a in rest:
            actor_map[a] = first
    logger.debug(f'成功载入{len(actor_map)}个女优映射。')


def _process_actor(actor: str) -> str:
    if not actor_map:
        _parse_actor_map()

    if actor in actor_map:
        return actor_map[actor]
    else:
        return actor
