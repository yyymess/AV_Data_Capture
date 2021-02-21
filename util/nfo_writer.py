"""将一个movie对象中的元数据写入对应的nfo文件"""

import os
from avdc.util.logging_config import get_logger
import xml.etree.ElementTree as ET

from avdc.model.movie import Movie

logger = get_logger(__name__)


def write_movie_nfo(movie: Movie, dir_path: str) -> bool:
    file_path = os.path.join(dir_path, movie.storage_fname + '.nfo')

    # create the file structure
    root = ET.Element('movie')

    ET.SubElement(root, 'title').text = movie.nfo_title

    if movie.studio:
        ET.SubElement(root, 'studio').text = movie.studio
        if movie.studio != movie.raw_studio:
            ET.SubElement(root, 'original_studio').text = movie.raw_studio
        ET.SubElement(root, 'maker').text = movie.studio

    _add_series(movie, root)

    if movie.year:
        ET.SubElement(root, 'year').text = movie.year

    if movie.release:
        ET.SubElement(root, 'release').text = movie.release

    _add_ratings(movie, root)

    if movie.outline:
        ET.SubElement(root, 'outline').text = movie.outline
        ET.SubElement(root, 'plot').text = movie.outline

    if movie.runtime:
        ET.SubElement(root, 'runtime').text = movie.runtime

    if movie.director:
        ET.SubElement(root, 'director').text = movie.director

    _add_actors(movie, root)

    if movie.label:
        ET.SubElement(root, 'label').text = movie.label

    if movie.cover:
        ET.SubElement(root, 'cover').text = movie.cover

    if movie.website:
        ET.SubElement(root, 'website').text = movie.website

    _add_tags(movie, root)

    _add_id(movie, root)

    ET.SubElement(root, 'original_filename').text = movie.original_fname

    if movie.scraper_source:
        ET.SubElement(root, 'avdc_source').text = movie.scraper_source

    tree = ET.ElementTree(element=root)
    ET.indent(tree)
    try:
        tree.write(file_path, encoding='utf-8', xml_declaration=True)
    except:
        logger.error(f'写入nfo文件失败 {file_path}。')
        return False

    logger.info(f'成功写入nfo文件 {file_path}。')
    return True


def _add_series(movie: Movie, root: ET.Element) -> None:
    if not movie.series:
        return

    set_elem = ET.SubElement(root, 'set')
    ET.SubElement(set_elem, 'name').text = movie.series
    ET.SubElement(set_elem, 'overview')


def _add_actors(movie: Movie, root: ET.Element) -> None:
    if not movie.actors:
        return
    actors = movie.actors
    raw_actors = movie.raw_actors

    for actor in actors:
        actor_elem = ET.SubElement(root, 'actor')
        ET.SubElement(actor_elem, 'name').text = actor

    # 如果女优被重命名过的话把原始的记录下来。
    if set(raw_actors) - set(actors):
        for actor in raw_actors:
            ET.SubElement(root, 'original_actor').text = actor


def _add_tags(movie: Movie, root: ET.Element) -> None:
    tags = set(movie.tags)
    raw_tags = set(movie.raw_tags)

    logger.debug(f'原始标签 {raw_tags}')
    logger.debug(f'输出标签 {tags}')

    # 如果tag有变化的话把旧tag记录下来方便日后使用
    if set(raw_tags) - set(tags):
        for t in raw_tags:
            ET.SubElement(root, 'original_tag').text = t

    if movie.series:
        tags.add(f'系列:{movie.series}')

    if movie.studio:
        tags.add(f'片商:{movie.studio}')

    for t in tags:
        ET.SubElement(root, 'tag').text = t
    for t in tags:
        ET.SubElement(root, 'genre').text = t


def _add_id(movie: Movie, root: ET.Element) -> None:
    uniqueid = ET.SubElement(root, 'uniqueid')
    uniqueid.text = movie.movie_id
    uniqueid.set('type', 'av')


def _add_ratings(movie: Movie, root: ET.Element) -> None:
    if not movie.ratings:
        return
    ratings = ET.SubElement(root, 'ratings')
    for i, rt in enumerate(movie.ratings):
        # emby 和 jellyfin还没支持第二种rating标准
        # 先把rating写进user rating里。
        if i == 0:
            user_rating = rt.rating / rt.max_rating * 10
            ET.SubElement(root, 'rating').text = f'{user_rating:0.1f}'

        rating = ET.SubElement(ratings, 'rating')
        if rt.max_rating:
            rating.set('max', f'{rt.max_rating:0.0f}')
        if rt.source:
            rating.set('name', rt.source)
        if i == 0:
            rating.set('default', 'true')

        ET.SubElement(rating, 'value').text = f'{rt.rating:0.1f}'

        if rt.votes:
            ET.SubElement(rating, 'votes').text = f'{rt.votes:d}'
