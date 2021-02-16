import sys
sys.path.append('../')
import re
from lxml import etree
import json
from bs4 import BeautifulSoup
from ADC_function import *
# import sys
# import io
# sys.stdout = io.TextIOWrapper(sys.stdout.buffer, errors = 'replace', line_buffering = True)

def getTitle(a):
    try:
        html = etree.fromstring(a, etree.HTMLParser())
        result = str(html.xpath('//*[@id="center_column"]/div[1]/h1/text()')).strip(" ['']")
        return result.replace('/', ',')
    except:
        return ''
def getActor(a): #//*[@id="center_column"]/div[2]/div[1]/div/table/tbody/tr[1]/td/text()
    html = etree.fromstring(a, etree.HTMLParser()) #//table/tr[1]/td[1]/text()
    result = html.xpath('//th[contains(text(),"出演：")]/../td/a/text()')
    result += html.xpath('//th[contains(text(),"出演：")]/../td/text()')
    result = [i.strip() for i in result if i.strip()]

    return result

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
def getLabel(a):
    html = etree.fromstring(a, etree.HTMLParser())  # //table/tr[1]/td[1]/text()
    result1 = str(html.xpath('//th[contains(text(),"シリーズ：")]/../td/a/text()')).strip(" ['']").strip('\\n    ').strip(
        '\\n')
    result2 = str(html.xpath('//th[contains(text(),"シリーズ：")]/../td/text()')).strip(" ['']").strip('\\n    ').strip(
        '\\n')
    return str(result1 + result2).strip('+').replace("', '",'').replace('"','')
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
def getTag(a):
    html = etree.fromstring(a, etree.HTMLParser())  # //table/tr[1]/td[1]/text()
    result1 = str(html.xpath('//th[contains(text(),"ジャンル：")]/../td/a/text()')).strip(" ['']").strip('\\n    ').strip(
        '\\n')
    result2 = str(html.xpath('//th[contains(text(),"ジャンル：")]/../td/text()')).strip(" ['']").strip('\\n    ').strip(
        '\\n')
    result = str(result1 + result2).strip('+').replace("', '\\n",",").replace("', '","").replace('"','').replace(',,','').split(',')
    total = []
    for i in result:
        try:
            total.append(translateTag_to_sc(i))
        except:
            pass
    total.append('日本')
    return total
def getCover(htmlcode):
    html = etree.fromstring(htmlcode, etree.HTMLParser())
    result = str(html.xpath('//*[@id="center_column"]/div[1]/div[1]/div/div/h2/img/@src')).strip(" ['']")
    #                    /html/body/div[2]/article[2]/div[1]/div[1]/div/div/h2/img/@src
    return result
def getDirector(a):
    html = etree.fromstring(a, etree.HTMLParser())  # //table/tr[1]/td[1]/text()
    result1 = str(html.xpath('//th[contains(text(),"シリーズ")]/../td/a/text()')).strip(" ['']").strip('\\n    ').strip(
        '\\n')
    result2 = str(html.xpath('//th[contains(text(),"シリーズ")]/../td/text()')).strip(" ['']").strip('\\n    ').strip(
        '\\n')
    return str(result1 + result2).strip('+').replace("', '",'').replace('"','')
def getOutline(htmlcode):
    html = etree.fromstring(htmlcode, etree.HTMLParser())
    result = str(html.xpath('//p/text()')).strip(" ['']").replace(u'\\n', '').replace("', '', '", '')
    return result
def getSeries(a):
    html = etree.fromstring(a, etree.HTMLParser())  # //table/tr[1]/td[1]/text()
    result1 = str(html.xpath('//th[contains(text(),"シリーズ")]/../td/a/text()')).strip(" ['']").strip('\\n    ').strip(
        '\\n')
    result2 = str(html.xpath('//th[contains(text(),"シリーズ")]/../td/text()')).strip(" ['']").strip('\\n    ').strip(
        '\\n')
    return str(result1 + result2).strip('+').replace("', '", '').replace('"', '')

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

def get_rating(htmlcode):
    html = etree.fromstring(htmlcode, etree.HTMLParser())  # //table/tr[1]/td[1]/text()
    result = html.xpath('//th[contains(text(),"評価")]/../td/text()')
    result = ''.join([i.strip() for i in result])
    return result[:3]

def get_rating_count(htmlcode):
    html = etree.fromstring(htmlcode, etree.HTMLParser())  # //table/tr[1]/td[1]/text()
    result = html.xpath('//th[contains(text(),"評価")]/../td/text()')
    result = ''.join([i.strip() for i in result])
    return result[4:].split(' ')[0]

def main(number2):
    number=number2.upper()
    htmlcode=str(get_html('https://www.mgstage.com/product/product_detail/'+str(number)+'/',cookies={'adc':'1'}))
    soup = BeautifulSoup(htmlcode, 'lxml')
    a = str(soup.find(attrs={'class': 'detail_data'})).replace('\n                                        ','').replace('                                ','').replace('\n                            ','').replace('\n                        ','')
    b = str(soup.find(attrs={'id': 'introduction'})).replace('\n                                        ','').replace('                                ','').replace('\n                            ','').replace('\n                        ','')
    #print(b)
    dic = {
        'title': getTitle(htmlcode).replace("\\n",'').replace('        ',''),
        'studio': getStudio(a),
        'outline': getOutline(b),
        'runtime': getRuntime(a),
        'director': getDirector(a),
        'actor': getActor(a),
        'release': getRelease(a),
        'number': getNum(a),
        'cover': getCover(htmlcode),
        'imagecut': 0,
        'tag': getTag(a),
        'label':getLabel(a),
        'extrafanart': getExtrafanart(htmlcode),
        'year': getYear(getRelease(a)),  # str(re.search('\d{4}',getRelease(a)).group()),
        'actor_photo': '',
        'website':'https://www.mgstage.com/product/product_detail/'+str(number)+'/',
        'source': 'mgstage.py',
        'series': getSeries(a),
        'rating': get_rating(a),
        'rating_count': get_rating_count(a),
        'rating_max': '5',
        'rating_source': 'mgstage'
    }
    js = json.dumps(dic, ensure_ascii=False, sort_keys=True, indent=4, separators=(',', ':'), )  # .encode('UTF-8')
    return js
    #print(htmlcode)

if __name__ == '__main__':
    #020RVG-077 多个可点击演出者
    #200GANA-1283 两个不可点击演出者
    
    print(main('020RVG-077'))
