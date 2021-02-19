import json
import logging
import re
import sys

from avdc.ADC_function import get_html
from avdc.model.movie import Movie
from lxml import etree  # need install

logger = logging.getLogger(__name__)


def getTitle_fc2com(htmlcode):  #获取厂商
    html = etree.fromstring(htmlcode, etree.HTMLParser())
    result = html.xpath('/html/head/title/text()')[0]
    return result


def getStudio_fc2com(htmlcode):  #获取厂商
    try:
        html = etree.fromstring(htmlcode, etree.HTMLParser())
        result = str(
            html.xpath(
                '//*[@id="top"]/div[1]/section[1]/div/section/div[2]/ul/li[3]/a/text()'
            )).strip(" ['']")
        return result
    except:
        return ''


def getNum_fc2com(htmlcode):  #获取番号
    html = etree.fromstring(htmlcode, etree.HTMLParser())
    result = str(
        html.xpath('/html/body/div[5]/div[1]/div[2]/p[1]/span[2]/text()')
    ).strip(" ['']")
    return result


def getRelease_fc2com(htmlcode2):  #
    html = etree.fromstring(htmlcode2, etree.HTMLParser())
    result = str(
        html.xpath(
            '//*[@id="top"]/div[1]/section[1]/div/section/div[2]/div[2]/p/text()'
        )).strip(" ['販売日 : ']").replace('/', '-')
    return result


def getCover_fc2com(htmlcode2):  #获取厂商 #
    html = etree.fromstring(htmlcode2, etree.HTMLParser())
    result = str(
        html.xpath(
            '//*[@id="top"]/div[1]/section[1]/div/section/div[1]/span/img/@src'
        )).strip(" ['']")
    return 'http:' + result


# def getOutline_fc2com(htmlcode2):     #获取番号 #
#     xpath_html = etree.fromstring(htmlcode2, etree.HTMLParser())
#     path = str(xpath_html.xpath('//*[@id="top"]/div[1]/section[4]/iframe/@src')).strip(" ['']")
#     html = etree.fromstring(get_html('https://adult.contents.fc2.com/'+path), etree.HTMLParser())
#     print('https://adult.contents.fc2.com'+path)
#     print(get_html('https://adult.contents.fc2.com'+path,cookies={'wei6H':'1'}))
#     result = str(html.xpath('/html/body/div/text()')).strip(" ['']").replace("\\n",'',10000).replace("'",'',10000).replace(', ,','').strip('  ').replace('。,',',')
#     return result

def getTag_fc2com(number):  #获取番号
    htmlcode = str(
        bytes(
            get_html(
                'http://adult.contents.fc2.com/api/v4/article/' + number +
                '/tag?'), 'utf-8').decode('unicode-escape'))
    result = re.findall('"tag":"(.*?)"', htmlcode)
    return result


def getExtrafanart(htmlcode):  # 获取剧照
    html_pather = re.compile(
        r'<ul class=\"items_article_SampleImagesArea\"[\s\S]*?</ul>')
    html = html_pather.search(htmlcode)
    if html:
        html = html.group()
        extrafanart_pather = re.compile(r'<a href=\"(.*?)\"')
        extrafanart_imgs = extrafanart_pather.findall(html)
        if extrafanart_imgs:
            return extrafanart_imgs
    return ''


def getTrailer(htmlcode):
    video_pather = re.compile(r'\'[a-zA-Z0-9]{32}\'')
    video = video_pather.findall(htmlcode)
    if video:
        video_url = video[0].replace('\'', '')
        video_url = 'https://adult.contents.fc2.com/api/v2/videos/1603395/sample?key=' + video_url
        url_json = eval(get_html(video_url))['path'].replace(
            '\\', '')
    else:
        video_url = ''

    return url_json

def set_rating(movie: Movie, htmlcode) -> None:
    html = etree.fromstring(htmlcode, etree.HTMLParser())
    try:
        rating_div = html.xpath('//a[@class="items_article_Stars"]')[0]
        stars = rating_div.xpath('.//span')
        rating = float(stars[0].attrib['class'][-1])
        votes = int(stars[1].text)
        movie.add_rating(
            rating = rating, max_rating= 5.0, source = 'fc2', votes = votes)
    except:
        logger.debug('评分刮削失败')



def main(number):
    movie = Movie()
    try:
        number = number.replace('FC2-', '').replace('fc2-', '')
        htmlcode = get_html(
            'https://adult.contents.fc2.com/article/' + number + '/')
        movie.title = getTitle_fc2com(htmlcode)
        movie.release = getRelease_fc2com(htmlcode)
        movie.movie_id = f'FC2-{number}'
        # 因为FC2，用上传者代表演员
        movie.actors = [getStudio_fc2com(htmlcode)]
        movie.studio = getStudio_fc2com(htmlcode)
        movie.director = getStudio_fc2com(htmlcode)
        movie.cover = getCover_fc2com(htmlcode)
        movie.imagecut = 0
        movie.extra_fanart =  getExtrafanart(htmlcode)
        movie.trailer = getTrailer(htmlcode)
        movie.tags = getTag_fc2com(number)
        movie.website = f'https://adult.contents.fc2.com/article/{number}/'
        movie.scraper_source = 'fc2'
        set_rating(movie, htmlcode)
    except Exception as e:
        logger.error('fc2刮削失败。')
        logger.debug('', exc_info = True)
        movie = Movie()
    return movie


if __name__ == '__main__':
    print(main('FC2-1603395'))
