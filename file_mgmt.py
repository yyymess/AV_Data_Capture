"""各类文件创立、修改功能"""

import logging
import os

from PIL.Image import DEFAULT_STRATEGY
import config

def get_info(json_data):  # TODO: 优化
    title = json_data.get('title')
    studio = json_data.get('studio')
    year = json_data.get('year')
    outline = json_data.get('outline')
    runtime = json_data.get('runtime')
    director = json_data.get('director')
    actor_photo = json_data.get('actor_photo')
    release = json_data.get('release')
    number = json_data.get('number')
    cover = json_data.get('cover')
    trailer = json_data.get('trailer')
    website = json_data.get('website')
    series = json_data.get('series')
    label = json_data.get('label', "")
    return title, studio, year, outline, runtime, director, actor_photo, release, number, cover, trailer, website, series, label

def create_folder(
        success_folder: str,
        location_rule: str,
        json_data: str,
        conf: config.Config) -> str:
    """为每部影片建立对应的文件夹。"""

    title, studio, year, outline, runtime, director, actor_photo, release, number, cover, trailer, website, series, label = get_info(json_data)

    target_path = os.path.join(conf.folder_path, success_folder, location_rule)
    logging.debug(f"试图创建{target_path}。")

    if not os.path.exists(target_path):
        try:
            os.makedirs(target_path)
        except:
            logging.debug("创建文件夹失败。尝试默认文件夹规则。")
            location_rule = '-'.join([number, title[:10]])
            target_path = os.path.join(
                conf.folder_path, success_folder, location_rule)
            logging.debug(f"试图创建{target_path}。")
            os.makedirs(target_path)
    return target_path


def create_success_failed_folder(conf:config.Config) -> bool:
    """试图创建失败文件夹，返回创建成功与否。"""
    logging.debug("aaaa")
    for d in [conf.failed_folder(), conf.success_folder()]:
        path = os.path.join(conf.folder_path, d)
        if not os.path.isdir(path):
            try:
                logging.debug(f"试图创建{path}。")
                os.makedirs(path)
            except:
                logging.debug("创建失败")
                return False
    return True

def rm_empty_success_failed_folder(conf: config.Config) -> None:
    """当成功、失败文件夹为空的时候删除它们"""
    for d in [conf.failed_folder(), conf.success_folder()]:
        root_path = os.path.join(conf.folder_path, d)
        for dirpath, _, _ in os.walk(root_path, topdown=False):
            if not os.listdir(dirpath):
                try:
                    logging.info(f"试图删除空文件夹{dirpath}。")
                    os.rmdir(dirpath)
                except OSError as ex:
                    logging.debug("删除失败")
