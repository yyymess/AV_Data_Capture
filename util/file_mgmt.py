"""各类文件创立、修改功能"""

import os

from tkinter import Tk, filedialog
import os
from avdc.util.logging_config import get_logger
from avdc import config
from avdc.model.movie import Movie

logger = get_logger(__name__)

def dir_picker() -> str:
    """询问用户并返回一个文件夹"""
    root = Tk()
    root.withdraw()
    return filedialog.askdirectory()

def create_folder(
        movie: Movie,
        conf: config.Config) -> str:
    """为每部影片建立对应的文件夹。"""

    target_path = os.path.join(conf.folder_path, conf.success_folder(), movie.storage_dir)
    logger.debug(f"试图创建{target_path}。")

    if not os.path.exists(target_path):
        try:
            os.makedirs(target_path)
        except:
            logger.debug("创建文件夹失败。尝试默认文件夹规则。")
            location_rule = '-'.join([movie.movie_id, movie.title[:10]])
            target_path = os.path.join(
                conf.folder_path, conf.success_folder(), location_rule)
            logger.debug(f"试图创建{target_path}。")
            os.makedirs(target_path)
    return target_path


def create_success_failed_folder(conf: config.Config) -> bool:
    """试图创建失败文件夹，返回创建成功与否。"""
    for d in [conf.failed_folder(), conf.success_folder()]:
        path = os.path.join(conf.folder_path, d)
        if not os.path.isdir(path):
            try:
                logger.debug(f"试图创建{path}。")
                os.makedirs(path)
            except:
                logger.debug("创建失败")
                return False
    return True

def rm_empty_success_failed_folder(conf: config.Config) -> None:
    """当成功、失败文件夹为空的时候删除它们"""
    for d in [conf.failed_folder(), conf.success_folder()]:
        root_path = os.path.join(conf.folder_path, d)
        for dirpath, _, _ in os.walk(root_path, topdown=False):
            if not os.listdir(dirpath):
                try:
                    logger.info(f"试图删除空文件夹{dirpath}。")
                    os.rmdir(dirpath)
                except OSError as ex:
                    logger.debug("删除失败")
