import logging
import re
from lxml import etree
from bs4 import BeautifulSoup
from avdc.ADC_function import *
from avdc.model.movie import Movie

logger = logging.getLogger(__name__)
def getTitle(a):
    try:
        html = etree.fromstring(a, etree.HTMLParser())
        result = str(html.xpath('//*[@id="center_column"]/div[1]/h1/text()')).strip(" ['']")
        return result.replace('/', ',')
    except:
        return ''
def _set_actors(movie: Movie, a): #//*[@id="center_column"]/div[2]/div[1]/div/table/tbody/tr[1]/td/text()
    html = etree.fromstring(a, etree.HTMLParser()) #//table/tr[1]/td[1]/text()
    result = html.xpath('//th[contains(text(),"出演：")]/../td/a/text()|'
                        '//th[contains(text(),"出演：")]/../td/text()')
    result = [i.strip() for i in result if i.strip()]
    movie.actors = result

def getStudio(a):
    html = etree.fromstring(a, etree.HTMLParser()) #//table/tr[1]/td[1]/text()
    result1=str(html.xpath('//th[contains(text(),"メーカー：")]/../td/a/text()')).strip(" ['']").strip('\\n    ').strip('\\n')
    result2=str(html.xpath('//th[contains(text(),"メーカー：")]/../td/text()')).strip(" ['']").strip('\\n    ').strip('\\n')
    return str(result1+result2).strip('+').replace("', '",'').replace('"','')
def getRuntime(a):
    html = etree.fromstring(a, etree.HTMLParser())  # //table/tr[1]/td[1]/text()
    result1 = str(html.xpath('//th[contains(text(),"収録時間：")]/../td/a/text()')).strip(" ['']").strip('\\n    ').strip('\\n')
    result2 = str(html.xpath('//th[contains(text(),"収録時間：")]/../td/text()')).strip(" ['']").strip('\\n    ').strip('\\n')
    return str(result1 + result2).strip('+').rstrip('mi')

def getNum(a):
    html = etree.fromstring(a, etree.HTMLParser())  # //table/tr[1]/td[1]/text()
    result1 = str(html.xpath('//th[contains(text(),"品番：")]/../td/a/text()')).strip(" ['']").strip('\\n    ').strip(
        '\\n')
    result2 = str(html.xpath('//th[contains(text(),"品番：")]/../td/text()')).strip(" ['']").strip('\\n    ').strip(
        '\\n')
    return str(result1 + result2).strip('+')
def getYear(getRelease):
    try:
        result = str(re.search('\d{4}',getRelease).group())
        return result
    except:
        return getRelease
def getRelease(a):
    html = etree.fromstring(a, etree.HTMLParser())  # //table/tr[1]/td[1]/text()
    result1 = str(html.xpath('//th[contains(text(),"配信開始日：")]/../td/a/text()')).strip(" ['']").strip('\\n    ').strip(
        '\\n')
    result2 = str(html.xpath('//th[contains(text(),"配信開始日：")]/../td/text()')).strip(" ['']").strip('\\n    ').strip(
        '\\n')
    return str(result1 + result2).strip('+').replace('/','-')

def _set_tags(movie: Movie, a) -> None:
    html = etree.fromstring(a, etree.HTMLParser())  # //table/tr[1]/td[1]/text()
    result = html.xpath('//th[contains(text(),"ジャンル：")]/../td/a/text()|'
                         '//th[contains(text(),"ジャンル：")]/../td/text()')
    result = set([i.strip() for i in result if i.strip()])
    result.add('日本')
    result.add('有码')
    movie.tags = list(result)

def getCover(htmlcode):
    html = etree.fromstring(htmlcode, etree.HTMLParser())
    result = str(html.xpath('//*[@id="center_column"]/div[1]/div[1]/div/div/h2/img/@src')).strip(" ['']")
    #                    /html/body/div[2]/article[2]/div[1]/div[1]/div/div/h2/img/@src
    return result

def getOutline(htmlcode):
    html = etree.fromstring(htmlcode, etree.HTMLParser())
    result = str(html.xpath('//p/text()')).strip(" ['']").replace(u'\\n', '').replace("', '', '", '')
    return result

def getSeries(a):
    html = etree.fromstring(a, etree.HTMLParser())  # //table/tr[1]/td[1]/text()
    result = html.xpath('//th[contains(text(),"シリーズ：")]/../td/a/text()|'
                         '//th[contains(text(),"シリーズ：")]/../td/text()')
    result = ' '.join([i.strip() for i in result if i.strip()])
    return result

def getExtrafanart(htmlcode):  # 获取剧照
    html_pather = re.compile(r'<dd>\s*?<ul>[\s\S]*?</ul>\s*?</dd>')
    html = html_pather.search(htmlcode)
    if html:
        html = html.group()
        extrafanart_pather = re.compile(r'<a class=\"sample_image\" href=\"(.*?)\"')
        extrafanart_imgs = extrafanart_pather.findall(html)
        if extrafanart_imgs:
            return extrafanart_imgs
    return ''

def _set_rating(movie: Movie, htmlcode) -> None:
    html = etree.fromstring(htmlcode, etree.HTMLParser())  # //table/tr[1]/td[1]/text()
    result = html.xpath('//th[contains(text(),"評価")]/../td/text()')
    result = ''.join([i.strip() for i in result])

    try:
        movie.add_rating(rating = float(result[:3]),
                         votes = int(result[4:].split(' ')[0]),
                         source = 'mgstage',
                         max_rating = 5.0)
    except:
        logger.warn('获取评分失败。')

def main(number2) -> Movie:
    number=number2.upper()
    htmlcode=str(get_html('https://www.mgstage.com/product/product_detail/'+str(number)+'/',cookies={'adc':'1'}))
    soup = BeautifulSoup(htmlcode, 'lxml')
    a = str(soup.find(attrs={'class': 'detail_data'})).replace('\n                                        ','').replace('                                ','').replace('\n                            ','').replace('\n                        ','')
    b = str(soup.find(attrs={'id': 'introduction'})).replace('\n                                        ','').replace('                                ','').replace('\n                            ','').replace('\n                        ','')

    movie = Movie()
    movie.title = getTitle(htmlcode).replace("\\n",'').replace('        ','')
    movie.studio = getStudio(a)
    movie.outline = getOutline(b)
    movie.runtime = getRuntime(a)
    _set_actors(movie, a)
    movie.release = getRelease(a)
    movie.movie_id = getNum(a)
    movie.cover = getCover(htmlcode)
    movie.imagecut = 0
    _set_tags(movie, a)
    movie.extra_fanart = getExtrafanart(htmlcode)
    movie.website = f'https://www.mgstage.com/product/product_detail/{number}/'
    movie.scraper_source = 'mgstage'
    movie.series = getSeries(a)
    _set_rating(movie, a)

    return movie
    #print(htmlcode)

if __name__ == '__main__':
    #020RVG-077 多个可点击演出者
    #200GANA-1283 两个不可点击演出者
    #488MCV-008 0评分
    #SIRO-4427 有评分
    print(main('200GANA-1283'))
