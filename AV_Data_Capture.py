import argparse
import json
import os
import re
import shutil
import sys
import time
from pathlib import Path
from avdc.util.logging_config import get_logger
from avdc.util.tag_processor import debug_unknown_tags
from avdc.util.logging_config import config_logging

from avdc.ADC_function import get_html
from avdc.config import Config
from avdc.core import core_main
from avdc.number_parser import get_number
from avdc.util.file_mgmt import (create_success_failed_folder, dir_picker,
                            rm_empty_success_failed_folder)

logger = get_logger('avdc.main')


def check_update(local_version):
    try:
        data = json.loads(
            get_html(
                "https://api.github.com/repos/yoshiko2/AV_Data_Capture/releases/latest"
            ))
    except:
        print("[-]Failed to update! Please check new version manually:")
        print("[-] https://github.com/yoshiko2/AV_Data_Capture/releases")
        print("[*]======================================================")
        return

    remote = data["tag_name"].replace(".", "")
    local_version = local_version.replace(".", "")
    if not local_version > remote:
        print("[*]" +
              ("* New update " + str(data["tag_name"]) + " *").center(54))
        print("[*]" + "↓ Download ↓".center(54))
        print("[*]https://github.com/yoshiko2/AV_Data_Capture/releases")
        print("[*]======================================================")


def argparse_function(ver: str) -> [str, str, bool]:
    parser = argparse.ArgumentParser()
    parser.add_argument("file",
                        default='',
                        nargs='?',
                        help="Single Movie file path.")
    parser.add_argument("-p",
                        "--path",
                        default='',
                        nargs='?',
                        help="Analysis folder path.")
    parser.add_argument("-c",
                        "--config",
                        default='config.ini',
                        nargs='?',
                        help="The config file Path.")
    parser.add_argument("-n",
                        "--number",
                        default='',
                        nargs='?',
                        help="Custom file number")
    parser.add_argument("-a",
                        "--auto-exit",
                        dest='autoexit',
                        action="store_true",
                        help="Auto exit after program complete")
    parser.add_argument("-v", "--version", action="version", version=ver)
    args = parser.parse_args()

    return args.file, args.path, args.config, args.number, args.autoexit


def movie_lists(root, escape_folder):
    if os.path.basename(root) in escape_folder:
        return []
    total = []
    file_type = conf.media_type().upper().split(",")
    dirs = os.listdir(root)
    for entry in dirs:
        f = os.path.join(root, entry)
        if os.path.isdir(f):
            total += movie_lists(f, escape_folder)
        elif os.path.splitext(f)[1].upper() in file_type:
            total.append(os.path.abspath(f))
    return total


def rm_empty_folder(path):
    try:
        files = os.listdir(path)  # 获取路径下的子文件(夹)列表
        for file in files:
            os.rmdir(path + '/' + file)  # 删除这个空文件夹
            print('[+]Deleting empty folder', path + '/' + file)
    except:
        pass


def create_data_and_move(file_path: str, c: Config, debug):
    # Normalized number, eg: 111xxx-222.mp4 -> xxx-222.mp4
    n_number = get_number(debug, os.path.basename(file_path))
    file_path = os.path.abspath(file_path)

    if debug == True:
        print("[!]Making Data for [{}], the number is [{}]".format(
            file_path, n_number))
        core_main(file_path, n_number, c)
        print("[*]======================================================")
    else:
        try:
            print("[!]Making Data for [{}], the number is [{}]".format(
                file_path, n_number))
            core_main(file_path, n_number, c)
            print("[*]======================================================")
        except Exception as err:
            print("[-] [{}] ERROR:".format(file_path))
            print('[-]', err)

            # 3.7.2 New: Move or not move to failed folder.
            if c.failed_move() == False:
                if c.soft_link():
                    print("[-]Link {} to failed folder".format(file_path))
                    os.symlink(file_path, conf.failed_folder() + "/")
            elif c.failed_move() == True:
                if c.soft_link():
                    print("[-]Link {} to failed folder".format(file_path))
                    os.symlink(file_path, conf.failed_folder() + "/")
                else:
                    try:
                        print(
                            "[-]Move [{}] to failed folder".format(file_path))
                        shutil.move(file_path, conf.failed_folder() + "/")
                    except Exception as err:
                        print('[!]', err)


def create_data_and_move_with_custom_number(file_path: str,
                                            c: Config,
                                            custom_number=None):
    try:
        print("[!]Making Data for [{}], the number is [{}]".format(
            file_path, custom_number))
        core_main(file_path, custom_number, c)
        print("[*]======================================================")
    except Exception as err:
        print("[-] [{}] ERROR:".format(file_path))
        print('[-]', err)

        if c.soft_link():
            print("[-]Link {} to failed folder".format(file_path))
            os.symlink(file_path, conf.failed_folder() + "/")
        else:
            try:
                print("[-]Move [{}] to failed folder".format(file_path))
                shutil.move(file_path, conf.failed_folder() + "/")
            except Exception as err:
                print('[!]', err)


if __name__ == '__main__':
    version = '4.5.1'

    config_logging()

    # Parse command line args
    single_file_path, folder_path, config_file, custom_number, auto_exit = argparse_function(
        version)

    logger.info(' AV Data Capture '.center(54, '='))
    logger.info(version.center(54))
    logger.info(''.center(54, '='))

    # Read config.ini
    conf = Config.get_instance(path=config_file)

    if conf.update_check():
        check_update(version)

    if conf.soft_link():
        print('[!]Enable soft link')

    if single_file_path:
        conf.folder_path = os.path.basename(single_file_path)
    else:
        if not folder_path:
            folder_path = dir_picker()
        conf.folder_path = folder_path
    if not conf.folder_path:
        logger.critical('无法定位根文件夹。', exc_info=True)
        sys.exit(0)

    if not create_success_failed_folder(conf):
        sys.exit(0)

    if single_file_path:  #Single File
        print('[+]==================== Single File =====================')
        create_data_and_move_with_custom_number(single_file_path, conf,
                                                custom_number)
    else:
        movie_list = movie_lists(folder_path,
                                 re.split("[,，]", conf.escape_folder()))

        count = 0
        count_all = str(len(movie_list))
        logger.attn(f'Find {count_all} movies')
        for movie_path in movie_list:  # 遍历电影列表 交给core处理
            count = count + 1
            percentage = str(count / int(count_all) * 100)[:4] + '%'
            print('[!] - ' + percentage + ' [' + str(count) + '/' + count_all +
                  '] -')
            create_data_and_move(movie_path, conf, conf.debug())
            # 休息几秒，防封
            time.sleep(conf.sleep_between_movie())

    rm_empty_success_failed_folder(conf)
    debug_unknown_tags()
    print("[+]All finished!!!")
    if not (conf.auto_exit() or auto_exit):
        input(
            "Press enter key exit, you can check the error message before you exit..."
        )
    sys.exit(0)
