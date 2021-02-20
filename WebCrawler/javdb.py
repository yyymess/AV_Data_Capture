import logging
import re
from lxml import etree
import json
from avdc.ADC_function import *
from avdc.model.movie import Movie
# import sys
# import io
# sys.stdout = io.TextIOWrapper(sys.stdout.buffer, errors = 'replace', line_buffering = True)

logger = logging.getLogger(__name__)

def getTitle(a):
    html = etree.fromstring(a, etree.HTMLParser())
    result = html.xpath("/html/body/section/div/h2/strong/text()")[0]
    return result

def getActor(a) -> list[str]:  # //*[@id="center_column"]/div[2]/div[1]/div/table/tbody/tr[1]/td/text()
    html = etree.fromstring(a, etree.HTMLParser())  # //table/tr[1]/td[1]/text()
    result = html.xpath('//strong[contains(text(),"演員")]/../span/text()|'
                        '//strong[contains(text(),"演員")]/../span/a/text()')
    result = [i.strip() for i in result]
    result = [i for i in result if i and i not in [',', 'N/A']]
    return result

def getaphoto(url):
    html_page = get_html(url)
    img_prether = re.compile(r'<span class\=\"avatar\" style\=\"background\-image\: url\((.*?)\)')
    img_url = img_prether.findall(html_page)
    if img_url:
        return img_url[0]
    else:
        return ''

def getActorPhoto(html): #//*[@id="star_qdt"]/li/a/img
    actorall_prether = re.compile(r'<strong>演員\:</strong>\s*?.*?<span class=\"value\">(.*)\s*?</div>')
    actorall = actorall_prether.findall(html)

    if actorall:
        actoralls = actorall[0]
        actor_prether = re.compile(r'<a href\=\"(.*?)\">(.*?)</a>')
        actor = actor_prether.findall(actoralls)
        actor_photo = {}
        for i in actor:
            actor_photo[i[1]] = getaphoto('https://javdb.com'+i[0])

        return actor_photo

    else:
        return {}
    
def getStudio(a):
    # html = etree.fromstring(a, etree.HTMLParser())  # //table/tr[1]/td[1]/text()
    # result1 = str(html.xpath('//strong[contains(text(),"片商")]/../span/text()')).strip(" ['']")
    # result2 = str(html.xpath('//strong[contains(text(),"片商")]/../span/a/text()')).strip(" ['']")
    # return str(result1 + result2).strip('+').replace("', '", '').replace('"', '')
    patherr = re.compile(r'<strong>片商\:</strong>[\s\S]*?<a href=\".*?>(.*?)</a></span>')
    pianshang = patherr.findall(a)
    if pianshang:
        result = pianshang[0]
    else:
        result = ""
    return result
    
def getRuntime(a):
    html = etree.fromstring(a, etree.HTMLParser())  # //table/tr[1]/td[1]/text()
    result1 = str(html.xpath('//strong[contains(text(),"時長")]/../span/text()')).strip(" ['']")
    result2 = str(html.xpath('//strong[contains(text(),"時長")]/../span/a/text()')).strip(" ['']")
    return str(result1 + result2).strip('+').rstrip('mi')
def getLabel(a):
    html = etree.fromstring(a, etree.HTMLParser())  # //table/tr[1]/td[1]/text()
    result1 = str(html.xpath('//strong[contains(text(),"系列")]/../span/text()')).strip(" ['']")
    result2 = str(html.xpath('//strong[contains(text(),"系列")]/../span/a/text()')).strip(" ['']")
    return str(result1 + result2).strip('+').replace("', '", '').replace('"', '')
def getNum(a):
    html = etree.fromstring(a, etree.HTMLParser())
    result1 = str(html.xpath('//strong[contains(text(),"番號")]/../span/text()')).strip(" ['']")
    result2 = str(html.xpath('//strong[contains(text(),"番號")]/../span/a/text()')).strip(" ['']")
    return str(result2 + result1).strip('+')
def getYear(getRelease):
    # try:
    #     result = str(re.search('\d{4}', getRelease).group())
    #     return result
    # except:
    #     return getRelease
    patherr = re.compile(r'<strong>日期\:</strong>\s*?.*?<span class="value">(.*?)\-.*?</span>')
    dates = patherr.findall(getRelease)
    if dates:
        result = dates[0]
    else:
        result = ''
    return result

def getRelease(a):
    # html = etree.fromstring(a, etree.HTMLParser())  # //table/tr[1]/td[1]/text()
    # result1 = str(html.xpath('//strong[contains(text(),"時間")]/../span/text()')).strip(" ['']")
    # result2 = str(html.xpath('//strong[contains(text(),"時間")]/../span/a/text()')).strip(" ['']")
    # return str(result1 + result2).strip('+')
    patherr = re.compile(r'<strong>日期\:</strong>\s*?.*?<span class="value">(.*?)</span>')
    dates = patherr.findall(a)
    if dates:
        result = dates[0]
    else:
        result = ''
    return result
def getTag(a):
    html = etree.fromstring(a, etree.HTMLParser())  # //table/tr[1]/td[1]/text()
    try:
        result = html.xpath('//strong[contains(text(),"類別")]/../span/a/text()')
        total = []
        for i in result:
            try:
                total.append(translateTag_to_sc(i))
            except:
                pass
        return total

    except:
        result = html.xpath('//strong[contains(text(),"類別")]/../span/text()')
        total = []
        for i in result:
            try:
                total.append(translateTag_to_sc(i))
            except:
                pass
        return total

def getCover_small(a, index=0):
    # same issue mentioned below,
    # javdb sometime returns multiple results
    # DO NOT just get the firt one, get the one with correct index number
    html = etree.fromstring(a, etree.HTMLParser())  # //table/tr[1]/td[1]/text()
    try:
        result = html.xpath("//div[@class='item-image fix-scale-cover']/img/@src")[index]
        if not 'https' in result:
            result = 'https:' + result
        return result
    except: # 2020.7.17 Repair Cover Url crawl
        try:
            result = html.xpath("//div[@class='item-image fix-scale-cover']/img/@data-src")[index]
            if not 'https' in result:
                result = 'https:' + result
            return result
        except:
            result = html.xpath("//div[@class='item-image']/img/@data-src")[index]
            if not 'https' in result:
                result = 'https:' + result
            return result


def getTrailer(htmlcode):  # 获取预告片
    video_pather = re.compile(r'<video id\=\".*?>\s*?<source src=\"(.*?)\"')
    video = video_pather.findall(htmlcode)
    if video:
        if not 'https:' in video[0]:
            video_url = 'https:' + video[0]
        else:
            video_url = video[0]
    else:
        video_url = ''
    return video_url

def getExtrafanart(htmlcode):  # 获取剧照
    html_pather = re.compile(r'<div class=\"tile\-images preview\-images\">[\s\S]*?</a>\s+?</div>\s+?</div>')
    html = html_pather.search(htmlcode)
    if html:
        html = html.group()
        extrafanart_pather = re.compile(r'<a class="tile-item" href=\"(.*?)\"')
        extrafanart_imgs = extrafanart_pather.findall(html)
        if extrafanart_imgs:
            return extrafanart_imgs
    return ''

def getCover(htmlcode):
    html = etree.fromstring(htmlcode, etree.HTMLParser())
    try:
        result = html.xpath("//div[contains(@class, 'column-video-cover')]/a/img/@src")[0]
    except: # 2020.7.17 Repair Cover Url crawl
        result = html.xpath("//div[contains(@class, 'column-video-cover')]/img/@src")[0]
    return result
def getDirector(a):
    html = etree.fromstring(a, etree.HTMLParser())  # //table/tr[1]/td[1]/text()
    result1 = str(html.xpath('//strong[contains(text(),"導演")]/../span/text()')).strip(" ['']")
    result2 = str(html.xpath('//strong[contains(text(),"導演")]/../span/a/text()')).strip(" ['']")
    return str(result1 + result2).strip('+').replace("', '", '').replace('"', '')
def getOutline(htmlcode):
    html = etree.fromstring(htmlcode, etree.HTMLParser())
    result = str(html.xpath('//*[@id="introduction"]/dd/p[1]/text()')).strip(" ['']")
    return result

def getSeries(a):
    html = etree.fromstring(a, etree.HTMLParser())  # //table/tr[1]/td[1]/text()
    result = html.xpath('//strong[contains(text(),"系列")]/../span/text()|'
                        '//strong[contains(text(),"系列")]/../span/a/text()')
    result = [i.strip() for i in result]
    result = [i for i in result if i]
    result = result[0] if result else ''
    return result

def set_rating(movie: Movie, a) -> None:
    html = etree.fromstring(a, etree.HTMLParser())  # //table/tr[1]/td[1]/text()
    result = html.xpath('//strong[contains(text(),"評分")]/../span//text()')
    result = [i.strip() for i in result]
    result = [i for i in result if i]
    if not result:
        return

    result = result[0]
    result = re.search(r'^(\d\.\d+).*由(\d+)人評價', result)
    if result:
        rating = float(result.group(1))
        votes = int(result.group(2))
        movie.add_rating(rating = rating,
                         max_rating= 5.0,
                         votes= votes,
                         source='javdb')


def main(number):
    movie = Movie()
    try:
        # if re.search(r'[a-zA-Z]+\.\d{2}\.\d{2}\.\d{2}', number).group():
        #     pass
        # else:
        #     number = number.upper()
        number = number.upper()
        try:
            query_result = get_html('https://javdb.com/search?q=' + number + '&f=all')
        except:
            query_result = get_html('https://javdb4.com/search?q=' + number + '&f=all')
        html = etree.fromstring(query_result, etree.HTMLParser())  # //table/tr[1]/td[1]/text()
        # javdb sometime returns multiple results,
        # and the first elememt maybe not the one we are looking for
        # iterate all candidates and find the match one
        urls = html.xpath('//*[@id="videos"]/div/div/a/@href')
        # 记录一下欧美的ids  ['Blacked','Blacked']
        correct_url = ''
        if re.search(r'[a-zA-Z]+\.\d{2}\.\d{2}\.\d{2}', number):
            correct_url = urls[0]
        else:
            ids =html.xpath('//*[@id="videos"]/div/div/a/div[contains(@class, "uid")]/text()')
            ids = [i.upper() for i in ids]
            if number.upper() in ids:
                correct_url = urls[ids.index(number.upper())]

        if not correct_url:
            return Movie()
        detail_page = get_html('https://javdb.com' + correct_url)

        # no cut image by default
        imagecut = 3
        # If gray image exists ,then replace with normal cover
        if re.search(r'[a-zA-Z]+\.\d{2}\.\d{2}\.\d{2}', number):
            cover_small = getCover_small(query_result)
        else:
            cover_small = getCover_small(query_result, index=ids.index(number))
        if 'placeholder' in cover_small:
            # replace wit normal cover and cut it
            imagecut = 1
            cover_small = getCover(detail_page)

        number = getNum(detail_page)
        title = getTitle(detail_page)
        if title and number:
            # remove duplicate title
            title = title.replace(number, '').strip()

        movie.actors = getActor(detail_page)
        movie.title = title
        movie.studio = getStudio(detail_page)
        movie.outline = getOutline(detail_page)
        movie.runtime = getRuntime(detail_page)
        movie.director = getDirector(detail_page)
        movie.release = getRelease(detail_page)
        movie.movie_id = number
        movie.cover = getCover(detail_page)
        movie.cover_small = cover_small
        movie.trailer = getTrailer(detail_page)
        movie.extra_fanart = getExtrafanart(detail_page)
        movie.imagecut = imagecut
        movie.tags = getTag(detail_page)
        movie.label = getLabel(detail_page)
        # 'actor_photo': getActorPhoto(detail_page),
        movie.website = 'https://javdb.com' + correct_url
        movie.scraper_source = 'javdb'
        movie.series = getSeries(detail_page)
        set_rating(movie, detail_page)

    except Exception as e:
        logger.warning(e, exc_info=True)
        movie = Movie()
    return movie

# main('DV-1562')
# input("[+][+]Press enter key exit, you can check the error messge before you exit.\n[+][+]按回车键结束，你可以在结束之前查看和错误信息。")
if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    # print(main('blacked.20.05.30'))
    # print(main('AGAV-042'))
    # print(main('EIH-059'))
    print(main('IBW-690z'))
