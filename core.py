from __future__ import annotations

import json
import os
import pathlib
import re
import shutil
import traceback
from io import BytesIO
from avdc.util.logging_config import get_logger

import requests
from PIL import Image

from avdc.ADC_function import (get_data_state, get_html, get_proxy,
                               is_uncensored)
from avdc.config import Config
from avdc.model.movie import Movie
from avdc.util.file_mgmt import create_folder
from avdc.util.nfo_writer import write_movie_nfo

# =========website========
from avdc.WebCrawler import airav
from avdc.WebCrawler import avsox
from avdc.WebCrawler import fanza
from avdc.WebCrawler import fc2
from avdc.WebCrawler import jav321
from avdc.WebCrawler import javbus
from avdc.WebCrawler import javdb
from avdc.WebCrawler import mgstage
from avdc.WebCrawler import xcity
from avdc.WebCrawler import javlib
from avdc.WebCrawler import dlsite
from avdc.WebCrawler import metajavlib

logger = get_logger('avdc.core')


def escape_path(path, escape_literals: str):  # Remove escape literals
    backslash = '\\'
    for literal in escape_literals:
        path = path.replace(backslash + literal, '')
    return path


def moveFailedFolder(filepath, failed_folder):
    config = Config.get_instance()
    if config.failed_move():
        root_path = str(pathlib.Path(filepath).parent)
        file_name = pathlib.Path(filepath).name
        destination_path = root_path + '/' + failed_folder + '/'
        if config.soft_link():
            print('[-]Create symlink to Failed output folder')
            os.symlink(filepath, destination_path + '/' + file_name)
        else:
            print('[-]Move to Failed output folder')
            shutil.move(filepath, destination_path)
    return


def get_data_from_json(file_number: str, filepath: str) -> Movie:  # 从JSON返回元数据
    """
    iterate through all services and fetch the data 
    """
    conf = Config.get_instance()

    func_mapping = {
        "airav": airav.main,
        "avsox": avsox.main,
        "fc2": fc2.main,
        "fanza": fanza.main,
        "javdb": javdb.main,
        "javbus": javbus.main,
        "mgstage": mgstage.main,
        "jav321": jav321.main,
        "xcity": xcity.main,
        "javlib": javlib.main,
        "dlsite": dlsite.main,
        "metajavlib": metajavlib.main,
    }

    # default fetch order list, from the beginning to the end
    sources = conf.sources().split(',')

    # if the input file name matches certain rules,
    # move some web service to the beginning of the list
    if "avsox" in sources and (re.match(r"^\d{5,}", file_number) or "HEYZO"
                               in file_number or "heyzo" in file_number
                               or "Heyzo" in file_number):
        # if conf.debug() == True:
        #     print('[+]select avsox')
        sources.insert(0, sources.pop(sources.index("avsox")))
    elif "mgstage" in sources and (re.match(r"\d+\D+", file_number) or
                                   "SIRO" in file_number.upper()):
        # if conf.debug() == True:
        # print('[+]select fanza')
        sources.insert(0, sources.pop(sources.index("mgstage")))
    elif "fc2" in sources and ("FC2" in file_number.upper()):
        # if conf.debug() == True:
        #     print('[+]select fc2')
        sources.insert(0, sources.pop(sources.index("fc2")))
    elif "dlsite" in sources and ("RJ" in file_number or "rj" in file_number or
                                  "VJ" in file_number or "vj" in file_number):
        # if conf.debug() == True:
        #     print('[+]select dlsite')
        sources.insert(0, sources.pop(sources.index("dlsite")))

    json_data = {}
    movie = None
    for source in sources:
        try:
            if conf.debug():
                logger.attn(f'select {source}')
            returnval = func_mapping[source](file_number)
            if (isinstance(returnval, Movie)):
                if returnval.is_filled():
                    movie = returnval
                    break
            else:
                json_data = json.loads(returnval)
                # if any service return a valid return, break
                if get_data_state(json_data):
                    break
        except:
            traceback.print_exc()
            break

    # Return if data not found in all sources
    if not json_data and not movie:
        print('[-]Movie Data not found!')
        moveFailedFolder(filepath, conf.failed_folder())
        return Movie()

    # ================================================网站规则添加结束================================================
    if not movie:
        movie = Movie()
        movie.title = json_data.get('title')
        movie.actors = json_data.get('actor')
        movie.release = json_data.get('release')
        movie.cover_small = json_data.get('cover_small')
        movie.cover = json_data.get('cover')
        movie.tags = json_data.get('tag')
        movie.year = json_data.get('year')
        movie.series = json_data.get('series')
        movie.runtime = json_data.get('runtime')
        movie.outline = json_data.get('outline')
        movie.scraper_source = json_data.get('source')
        movie.label = json_data.get('label')
        movie.studio = json_data.get('studio')
        movie.director = json_data.get('director')
        movie.movie_id = json_data.get('number')
        movie.trailer = json_data.get('trailer')
        movie.website = json_data.get('website')
        movie.imagecut = json_data.get('imagecut')
        movie.extra_fanart = json_data.get('extrafanart')

    movie.original_path = filepath

    if not movie.is_filled():
        print('[-]Movie Data not found!')
        moveFailedFolder(filepath, conf.failed_folder())
        return Movie()
    """
    TODO:  翻译以后再说
    if conf.is_transalte():
        translate_values = conf.transalte_values().split(",")
        for translate_value in translate_values:
            if json_data[translate_value] == "":
                continue
            # if conf.get_transalte_engine() == "baidu":
            #     json_data[translate_value] = translate(
            #         json_data[translate_value],
            #         target_language="zh",
            #         engine=conf.get_transalte_engine(),
            #         app_id=conf.get_transalte_appId(),
            #         key=conf.get_transalte_key(),
            #         delay=conf.get_transalte_delay(),
            #     )
            if conf.get_transalte_engine() == "azure":
                json_data[translate_value] = translate(
                    json_data[translate_value],
                    target_language="zh-Hans",
                    engine=conf.get_transalte_engine(),
                    key=conf.get_transalte_key(),
                )
            else:
                json_data[translate_value] = translate(json_data[translate_value])
    """

    logger.debug(movie)
    return movie


def small_cover_check(movie: Movie, path, cover_small, conf: Config, filepath,
                      failed_folder):
    fname = movie.storage_fname + '-poster.jpg'
    download_file_with_filename(cover_small, fname, path, conf, filepath,
                                failed_folder)
    logger.debug(f'Image Downloaded! {path}/{fname}')


# =====================资源下载部分===========================


# path = examle:photo , video.in the Project Folder!
def download_file_with_filename(url, filename, path, conf: Config, filepath,
                                failed_folder):
    switch, proxy, timeout, retry_count, proxytype = conf.proxy()

    for i in range(retry_count):
        try:
            if switch == 1 or switch == '1':
                if not os.path.exists(path):
                    os.makedirs(path)
                proxies = get_proxy(proxy, proxytype)
                headers = {
                    'User-Agent':
                    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36'
                }
                r = requests.get(url,
                                 headers=headers,
                                 timeout=timeout,
                                 proxies=proxies)
                if r == '':
                    print('[-]Movie Data not found!')
                    return
                with open(str(path) + "/" + filename, "wb") as code:
                    code.write(r.content)
                return
            else:
                if not os.path.exists(path):
                    os.makedirs(path)
                headers = {
                    'User-Agent':
                    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36'
                }
                r = requests.get(url, timeout=timeout, headers=headers)
                if r == '':
                    print('[-]Movie Data not found!')
                    return
                with open(str(path) + "/" + filename, "wb") as code:
                    code.write(r.content)
                return
        except requests.exceptions.RequestException:
            i += 1
            print('[-]Image Download :  Connect retry ' + str(i) + '/' +
                  str(retry_count))
        except requests.exceptions.ConnectionError:
            i += 1
            print('[-]Image Download :  Connect retry ' + str(i) + '/' +
                  str(retry_count))
        except requests.exceptions.ProxyError:
            i += 1
            print('[-]Image Download :  Connect retry ' + str(i) + '/' +
                  str(retry_count))
        except requests.exceptions.ConnectTimeout:
            i += 1
            print('[-]Image Download :  Connect retry ' + str(i) + '/' +
                  str(retry_count))
    print('[-]Connect Failed! Please check your Proxy or Network!')
    moveFailedFolder(filepath, failed_folder)
    return


def trailer_download(movie: Movie, path, filepath, conf: Config,
                     failed_folder):
    fname = movie.storage_fname + '-trailer.mp4'
    if download_file_with_filename(movie.trailer, fname, path, conf, filepath,
                                   failed_folder) == 'failed':
        return
    switch, _proxy, _timeout, retry, _proxytype = conf.proxy()
    for i in range(retry):
        if os.path.getsize(path + '/' + fname) == 0:
            print('[!]Video Download Failed! Trying again. [{}/3]', i + 1)
            download_file_with_filename(movie.trailer, fname, path, conf,
                                        filepath, failed_folder)
            continue
        else:
            break
    if os.path.getsize(path + '/' + fname) == 0:
        return
    print('[+]Video Downloaded!', path + '/' + fname)


# 剧照下载成功，否则移动到failed
def extrafanart_download(data, path, conf: Config, filepath, failed_folder):
    if not conf.is_extrafanart():
        return

    j = 1
    path = path + '/' + conf.get_extrafanart()
    for url in data:
        if download_file_with_filename(url, '/extrafanart-' + str(j) + '.jpg',
                                       path, conf, filepath,
                                       failed_folder) == 'failed':
            moveFailedFolder(filepath, failed_folder)
            return
        switch, _proxy, _timeout, retry, _proxytype = conf.proxy()
        for i in range(retry):
            if os.path.getsize(path + '/extrafanart-' + str(j) + '.jpg') == 0:
                print('[!]Image Download Failed! Trying again. [{}/3]', i + 1)
                download_file_with_filename(url,
                                            '/extrafanart-' + str(j) + '.jpg',
                                            path, conf, filepath,
                                            failed_folder)
                continue
            else:
                break
        if os.path.getsize(path + '/extrafanart-' + str(j) + '.jpg') == 0:
            return
        logger.debug(f'Image Downloaded! {path}/extrafanart-{j}.jpg')
        j += 1


# 封面是否下载成功，否则移动到failed
def image_download(movie: Movie, path, conf: Config, filepath, failed_folder):
    fanart_name = movie.storage_fname + '-fanart.jpg'
    thumb_name = movie.storage_fname + '-thumb.jpg'
    if download_file_with_filename(movie.cover, fanart_name, path, conf,
                                   filepath, failed_folder) == 'failed':
        moveFailedFolder(filepath, failed_folder)
        return

    switch, _proxy, _timeout, retry, _proxytype = conf.proxy()
    for i in range(retry):
        if os.path.getsize(path + '/' + fanart_name) == 0:
            print('[!]Image Download Failed! Trying again. [{}/3]', i + 1)
            download_file_with_filename(movie.cover, fanart_name, path, conf,
                                        filepath, failed_folder)
            continue
        else:
            break
    if os.path.getsize(path + '/' + fanart_name) == 0:
        return
    logger.debug(f'Image Downloaded! {path}/{fanart_name}')
    shutil.copyfile(path + '/' + fanart_name, path + '/' + thumb_name)


def cutImage(movie: Movie, path):
    fanart_fname = movie.storage_fname + '-fanart.jpg'
    poster_fname = movie.storage_fname + '-poster.jpg'

    if movie.imagecut == 1:  # 剪裁大封面
        try:
            img = Image.open(os.path.join(path, fanart_fname))
            imgSize = img.size
            w = img.width
            h = img.height
            img2 = img.crop((w / 1.9, 0, w, h))
            img2.save(os.path.join(path, poster_fname))
            print('[+]Image Cutted!     ' + path + '/' + poster_fname)
        except:
            print('[-]Cover cut failed!')
    elif movie.imagecut == 0:  # 复制封面
        shutil.copyfile(os.path.join(path, fanart_fname),
                        os.path.join(path, poster_fname))
        print('[+]Image Copyed!     ' + path + '/' + poster_fname)


# 此函数从gui版copy过来用用
# 参数说明
# poster_path
# thumb_path
# cn_sub   中文字幕  参数值为 1  0
# leak     流出     参数值为 1   0
# uncensored 无码   参数值为 1   0
# ========================================================================加水印
def add_mark(poster_path, thumb_path, cn_sub, leak, uncensored, conf: Config):
    mark_type = ''
    if cn_sub:
        mark_type += ',字幕'
    if leak:
        mark_type += ',流出'
    if uncensored:
        mark_type += ',无码'
    if mark_type == '':
        return
    add_mark_thread(thumb_path, cn_sub, leak, uncensored, conf)
    print('[+]Thumb Add Mark:   ' + mark_type.strip(','))
    add_mark_thread(poster_path, cn_sub, leak, uncensored, conf)
    print('[+]Poster Add Mark:  ' + mark_type.strip(','))


def add_mark_thread(pic_path, cn_sub, leak, uncensored, conf):
    size = 14
    img_pic = Image.open(pic_path)
    # 获取自定义位置，取余配合pos达到顺时针添加的效果
    # 左上 0, 右上 1, 右下 2， 左下 3
    count = conf.watermark_type()
    if cn_sub == 1 or cn_sub == '1':
        add_to_pic(pic_path, img_pic, size, count, 1)  # 添加
        count = (count + 1) % 4
    if leak == 1 or leak == '1':
        add_to_pic(pic_path, img_pic, size, count, 2)
        count = (count + 1) % 4
    if uncensored == 1 or uncensored == '1':
        add_to_pic(pic_path, img_pic, size, count, 3)
    img_pic.close()


def add_to_pic(pic_path, img_pic, size, count, mode):
    mark_pic_path = ''
    if mode == 1:
        mark_pic_path = BytesIO(
            get_html(
                'https://raw.githubusercontent.com/yoshiko2'
                '/AV_Data_Capture/master/Img/SUB.png',
                return_type="content"))
    elif mode == 2:
        mark_pic_path = BytesIO(
            get_html(
                'https://raw.githubusercontent.com/yoshiko2'
                '/AV_Data_Capture/master/Img/LEAK.png',
                return_type="content"))
    elif mode == 3:
        mark_pic_path = BytesIO(
            get_html(
                'https://raw.githubusercontent.com/yoshiko2'
                '/AV_Data_Capture/master/Img/UNCENSORED.png',
                return_type="content"))
    img_subt = Image.open(mark_pic_path)
    scroll_high = int(img_pic.height / size)
    scroll_wide = int(scroll_high * img_subt.width / img_subt.height)
    img_subt = img_subt.resize((scroll_wide, scroll_high), Image.ANTIALIAS)
    r, g, b, a = img_subt.split()  # 获取颜色通道，保持png的透明性
    # 封面四个角的位置
    pos = [
        {
            'x': 0,
            'y': 0
        },
        {
            'x': img_pic.width - scroll_wide,
            'y': 0
        },
        {
            'x': img_pic.width - scroll_wide,
            'y': img_pic.height - scroll_high
        },
        {
            'x': 0,
            'y': img_pic.height - scroll_high
        },
    ]
    img_pic.paste(img_subt, (pos[count]['x'], pos[count]['y']), mask=a)
    img_pic.save(pic_path, quality=95)


# ========================结束=================================


def paste_file_to_folder(movie: Movie, filepath, path,
                         conf: Config):  # 文件路径，番号，后缀，要移动至的位置
    houzhui = os.path.splitext(filepath)[1].replace(",", "")
    file_parent_origin_path = str(pathlib.Path(filepath).parent)
    try:
        targetpath = os.path.join(path, movie.storage_fname + houzhui)
        # 如果soft_link=1 使用软链接
        if conf.soft_link():
            os.symlink(filepath, targetpath)
            # 采用相对路径，以便网络访问时能正确打开视频
            filerelpath = os.path.relpath(filepath, path)
            os.symlink(filerelpath, targetpath)
        else:
            os.rename(filepath, targetpath)
            # 移走文件后，在原来位置增加一个可追溯的软链接，指向文件新位置
            # 以便追查文件从原先位置被移动到哪里了，避免因为得到错误番号后改名移动导致的文件失踪
            # 便于手工找回文件。并将软连接文件名后缀修改，以避免再次被搜刮。
            # windows 会爆炸
#            targetabspath = os.path.abspath(targetpath)
#            if targetabspath != os.path.abspath(filepath):
#                targetrelpath = os.path.relpath(targetabspath, file_parent_origin_path)
#                os.symlink(targetrelpath, filepath + '#sym')
        sub_res = conf.sub_rule()

        for subname in sub_res:
            if os.path.exists(movie.storage_fname + subname):  # 字幕移动
                os.rename(movie.storage_fname + subname,
                          path + '/' + movie.storage_fname + subname)
                print('[+]Sub moved!')
                return True

    except FileExistsError:
        print('[-]File Exists! Please check your movie!')
        print('[-]move to the root folder of the program.')
        return
    except PermissionError:
        logger.error('Please run as administrator!', exc_info=True)
        return


def paste_file_to_folder_mode2(movie: Movie, filepath, path,
                               conf):  # 文件路径，番号，后缀，要移动至的位置
    houzhui = os.path.splitext(filepath)[1].replace(",", "")
    file_parent_origin_path = str(pathlib.Path(filepath).parent)
    try:
        if conf.soft_link():
            os.symlink(filepath, path + '/' + movie.storage_fname + houzhui)
        else:
            os.rename(filepath, path + '/' + movie.storage_fname + houzhui)

        sub_res = conf.sub_rule()
        for subname in sub_res:
            if os.path.exists(os.getcwd() + '/' + movie.storage_fname +
                              subname):  # 字幕移动
                os.rename(os.getcwd() + '/' + movie.storage_fname + subname,
                          path + '/' + movie.storage_fname + subname)
                print('[+]Sub moved!')
                print('[!]Success')
                return True
    except FileExistsError:
        print('[-]File Exists! Please check your movie!')
        print('[-]move to the root folder of the program.')
        return
    except PermissionError:
        print('[-]Error! Please run as administrator!')
        return


def get_part(filepath, failed_folder) -> str:
    try:
        if re.search('-CD\d+', filepath):
            return re.findall('-CD\d+', filepath)[0]
        if re.search('-cd\d+', filepath):
            return re.findall('-cd\d+', filepath)[0]
    except:
        print("[-]failed!Please rename the filename again!")
        moveFailedFolder(filepath, failed_folder)
        return ''


def core_main(files:list[str], movie_id: str, conf: Config):
    # =======================================================================初始化所需变量
    part = ''
    leak_word = ''
    c_word = ''
    cn_sub = ''

    filepath = files[0]  # 影片的路径 绝对路径

    movie = get_data_from_json(movie_id, files[0])  # 定义番号

    # Return if blank dict returned (data not found)
    if not movie.is_filled():
        return

    imagecut = movie.imagecut
    # =======================================================================判断-C,-CD后缀
    if '-c.' in filepath or '-C.' in filepath or '中文' in filepath or '字幕' in filepath:
        cn_sub = '1'
        c_word = '-C'  # 中文字幕影片后缀
        movie.add_tag('中文字幕')
    if '-CD' in filepath or '-cd' in filepath:
        part = get_part(filepath, conf.failed_folder())

    # 判断是否无码
    if '无码' in filepath or is_uncensored(movie.movie_id):
        uncensored = 1
        movie.add_tag("无码")
    else:
        uncensored = 0

    if '流出' in filepath or 'uncensored' in filepath:
        movie.add_tag("流出")
        leak = 1
        leak_word = '-流出' # 流出影片后缀
    else:
        leak = 0

    movie.fname_postfix = leak_word + c_word + part

    # main_mode
    #  1: 刮削模式 / Scraping mode
    #  2: 整理模式 / Organizing mode
    #  3：不改变路径刮削
    if conf.main_mode() == 1:
        # 创建文件夹
        path = create_folder(movie, conf)

        # 检查小封面, 如果image cut为3，则下载小封面
        if imagecut == 3:
            small_cover_check(movie, path, movie.cover_small, conf,
                              filepath, conf.failed_folder())

        # creatFolder会返回番号路径
        image_download(movie, path, conf, filepath, conf.failed_folder())
        try:
            # 下载预告片
            if movie.trailer and conf.is_trailer():
                trailer_download(movie, path, filepath, conf,
                                 conf.failed_folder())
        except:
            pass

        try:
            # 下载剧照 data, path, conf: Config, filepath, failed_folder
            if movie.extra_fanart:
                extrafanart_download(movie.extra_fanart, path, conf,
                                     filepath, conf.failed_folder())
        except:
            pass
        # 裁剪图
        cutImage(movie, path)
        # 打印NFO文件
        write_movie_nfo(movie, path)

        # 移动文件
        paste_file_to_folder(movie, filepath, path, conf)

        poster_path = path + '/' + movie.storage_fname + '-poster.jpg'
        thumb_path = path + '/' + movie.storage_fname + '-thumb.jpg'
        if conf.is_watermark():
            add_mark(poster_path, thumb_path, cn_sub, leak, uncensored, conf)

        for f in files[1:]:
            #暴力。。先解决了再说
            logger.debug(f'Moving extra part {f}')
            new_part = get_part(f, conf.failed_folder())
            movie.fname_postfix = leak_word + c_word + new_part
            paste_file_to_folder(movie, f, path, conf)

    else:
        logger.critical('Unimplemented mode')
