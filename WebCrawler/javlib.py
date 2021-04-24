import json
import time
from http.cookies import SimpleCookie
from avdc.util.logging_config import config_logging, get_logger

import bs4
from avdc.ADC_function import get_html, get_javlib_cookie
from avdc.model.movie import Movie
from bs4 import BeautifulSoup
from lxml import html

logger = get_logger(__name__)


def main(number: str) -> Movie:
    raw_cookies, user_agent = get_javlib_cookie()

    # Blank cookies mean javlib site return error
    if not raw_cookies:
        return json.dumps({},
                          ensure_ascii=False,
                          sort_keys=True,
                          indent=4,
                          separators=(',', ':'))

    # Manually construct a dictionary
    s_cookie = SimpleCookie()
    s_cookie.load(raw_cookies)
    cookies = {}
    for key, morsel in s_cookie.items():
        cookies[key] = morsel.value

    # Scraping
    result = get_html(
        "http://www.javlibrary.com/cn/vl_searchbyid.php?keyword={}".format(
            number),
        cookies=cookies,
        ua=user_agent,
        return_type="object")
    soup = BeautifulSoup(result.text, "html.parser")
    lx = html.fromstring(str(soup))

    if "/?v=jav" in result.url:
        return extract_movie(lx, soup, result.url)
    else:
        url = _find_best_movie_match(lx, number)
        if url:
            result = get_html(url,
                              cookies=cookies,
                              ua=user_agent,
                              return_type="object")
            soup = BeautifulSoup(result.text, "html.parser")
            lx = html.fromstring(str(soup))
            return extract_movie(lx, soup, result.url)

    return Movie()


def _find_best_movie_match(lx: html.HtmlElement, number: str) -> str:
    number = number.upper()
    vids = lx.xpath('//div[@class="videothumblist"]'
                    '/div[@class="videos"]'
                    '/div[@class="video"]')
    vid_list = []
    for v in vids:
        title = ''.join(v.xpath('.//div[@class="title"]/text()')).strip()
        movie_id = ''.join(
            v.xpath('.//div[@class="id"]/text()')).strip().upper()
        href = ''.join(v.xpath('./a/@href')).strip()[2:]
        url = 'http://www.javlibrary.com/cn/' + href
        vid_list.append((title, movie_id, url))

    # SNIS-459 有蓝光版，选非蓝光版
    # ID-020 有多个同ID片
    matching_list = [i for i in vid_list if i[1] == number]

    if len(matching_list) > 1:
        logger.debug('ID搜索返回多个结果，试图清理蓝光版本。')
        matching_list = [i for i in matching_list if 'ブルーレイ' not in i[0]]

    if not matching_list:
        return ''
    elif len(matching_list) == 1:
        return matching_list[0][2]
    else:
        # TODO  这边的behaviour加个config flag来控制。
        #       默认情况选第一个就好。
        logger.warning(f'多个影片出现重复ID。')
        for i, v in enumerate(matching_list):
            logger.warning(f'{i}: {v[0]}')
            logger.warning(f'     {v[2]}')
        logger.warning(f'{len(matching_list)}: 跳过')
        index = len(matching_list) + 1
        while index > len(matching_list):
            try:
                index = int(input("选择一部影片: "))
            except:
                pass
        if index < len(matching_list):
            return matching_list[index][2]

    return ''


def extract_movie(lx: html.HtmlElement, soup: BeautifulSoup,
                  url: str) -> Movie:
    movie = Movie()
    movie.title = get_title(lx, soup)
    movie.studio = get_table_el_single_anchor(soup, "video_maker")
    movie.director = get_table_el_single_anchor(soup, "video_director")
    movie.cover = get_cover(lx)
    movie.imagecut = 1
    movie.website = url
    movie.scraper_source = 'javlib'
    movie.actors = get_table_el_multi_anchor(soup, "video_cast").split(',')
    movie.label = get_table_el_td(soup, "video_label")
    movie.tags = get_table_el_multi_anchor(soup, "video_genres").split(',')
    movie.movie_id = get_table_el_td(soup, "video_id")
    movie.release = get_table_el_td(soup, "video_date")
    movie.runtime = get_from_xpath(
        lx, '//*[@id="video_length"]/table/tr/td[2]/span/text()')

    _add_rating(movie, lx)
    movie.add_tag('日本')
    movie.add_tag('有码')

    return movie


def _add_rating(movie: Movie, lx: html.HtmlElement) -> None:
    score = lx.xpath('//*[@id="video_review"]//span[@class="score"]/text()')
    if not score:
        return
    try:
        score = float(score[0].strip('( )'))
        movie.add_rating(rating=score, source='javlib', max_rating=10.0)
    except:
        logger.debug('评分刮削失败。')
        pass


def get_from_xpath(lx: html.HtmlElement, xpath: str) -> str:
    return lx.xpath(xpath)[0].strip()


def get_table_el_single_anchor(soup: BeautifulSoup, tag_id: str) -> str:
    tag = soup.find(id=tag_id).find("a")

    if tag is not None:
        return tag.string.strip()
    else:
        return ""


def get_table_el_multi_anchor(soup: BeautifulSoup, tag_id: str) -> str:
    tags = soup.find(id=tag_id).find_all("a")

    return process(tags)


def get_table_el_td(soup: BeautifulSoup, tag_id: str) -> str:
    tags = soup.find(id=tag_id).find_all("td", class_="text")

    return process(tags)


def process(tags: bs4.element.ResultSet) -> str:
    values = []
    for tag in tags:
        value = tag.string
        if value is not None and value != "----":
            values.append(value)

    return ",".join(x for x in values if x)


def get_title(lx: html.HtmlElement, soup: BeautifulSoup) -> str:
    title = get_from_xpath(lx, '//*[@id="video_title"]/h3/a/text()')
    number = get_table_el_td(soup, "video_id")

    return title.replace(number, "").strip()


def get_cover(lx: html.HtmlComment) -> str:
    return "http:{}".format(
        get_from_xpath(lx, '//*[@id="video_jacket_img"]/@src'))


if __name__ == "__main__":
    config_logging('DEBUG', root=True)
    #lists = ["DVMC-003", "GS-0167", "JKREZ-001", "KMHRS-010", "KNSD-023", "ARM-072"]
    lists = ["DASD-802"]
    for num in lists:
        print(main(num))
        time.sleep(3)
