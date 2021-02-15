import requests
import hashlib
import random
import uuid
import json
import time
from lxml import etree
import re
import config

SUPPORT_PROXY_TYPE = ("http", "socks5", "socks5h")

def get_data_state(data: dict) -> bool:  # 元数据获取失败检测
    if "title" not in data or "number" not in data:
        return False

    if data["title"] is None or data["title"] == "" or data["title"] == "null":
        return False

    if data["number"] is None or data["number"] == "" or data["number"] == "null":
        return False

    return True


def getXpathSingle(htmlcode,xpath):
    html = etree.fromstring(htmlcode, etree.HTMLParser())
    result1 = str(html.xpath(xpath)).strip(" ['']")
    return result1


def get_proxy(proxy: str, proxytype: str = None) -> dict:
    ''' 获得代理参数，默认http代理
    '''
    if proxy:
        if proxytype in SUPPORT_PROXY_TYPE:
            proxies = {"http": proxytype + "://" + proxy, "https": proxytype + "://" + proxy}
        else:
            proxies = {"http": "http://" + proxy, "https": "https://" + proxy}
    else:
        proxies = {}

    return proxies


# 网页请求核心
def get_html(url, cookies: dict = None, ua: str = None, return_type: str = None):
    verify=config.Config().cacert_file()
    switch, proxy, timeout, retry_count, proxytype = config.Config().proxy()
    proxies = get_proxy(proxy, proxytype)

    if ua is None:
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3100.0 Safari/537.36"} # noqa
    else:
        headers = {"User-Agent": ua}

    for i in range(retry_count):
        try:
            if switch == '1' or switch == 1:
                result = requests.get(str(url), headers=headers, timeout=timeout, proxies=proxies, verify=verify, cookies=cookies)
            else:
                result = requests.get(str(url), headers=headers, timeout=timeout, cookies=cookies)

            result.encoding = "utf-8"

            if return_type == "object":
                return result
            elif return_type == "content":
                return result.content
            else:
                return result.text
        except requests.exceptions.ProxyError:
            print("[-]Proxy error! Please check your Proxy")
            return
        except Exception as e:
            print("[-]Connect retry {}/{}".format(i + 1, retry_count))
            print("[-]" + str(e))
    print('[-]Connect Failed! Please check your Proxy or Network!')


def post_html(url: str, query: dict, headers: dict = None) -> requests.Response:
    switch, proxy, timeout, retry_count, proxytype = config.Config().proxy()
    proxies = get_proxy(proxy, proxytype)
    headers_ua = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3100.0 Safari/537.36"}
    if headers is None:
        headers = headers_ua
    else:
        headers.update(headers_ua)

    for i in range(retry_count):
        try:
            if switch == 1 or switch == '1':
                result = requests.post(url, data=query, proxies=proxies, headers=headers, timeout=timeout)
            else:
                result = requests.post(url, data=query, headers=headers, timeout=timeout)
            return result
        except requests.exceptions.ProxyError:
            print("[-]Connect retry {}/{}".format(i+1, retry_count))
    print("[-]Connect Failed! Please check your Proxy or Network!")


def get_javlib_cookie() -> [dict, str]:
    import cloudscraper
    switch, proxy, timeout, retry_count, proxytype = config.Config().proxy()
    proxies = get_proxy(proxy, proxytype)

    raw_cookie = {}
    user_agent = ""

    # Get __cfduid/cf_clearance and user-agent
    for i in range(retry_count):
        try:
            if switch == 1 or switch == '1':
                raw_cookie, user_agent = cloudscraper.get_cookie_string(
                    "http://www.m45e.com/",
                    proxies=proxies
                )
            else:
                raw_cookie, user_agent = cloudscraper.get_cookie_string(
                    "http://www.m45e.com/"
                )
        except requests.exceptions.ProxyError:
            print("[-] ProxyError, retry {}/{}".format(i+1, retry_count))
        except cloudscraper.exceptions.CloudflareIUAMError:
            print("[-] IUAMError, retry {}/{}".format(i+1, retry_count))

    return raw_cookie, user_agent

def translateTag_to_sc(tag):
    tranlate_to_sc = config.Config().transalte_to_sc()
    if tranlate_to_sc:
        dict_gen = {
            'パイパン': '白虎'
        }
        if tag in dict_gen:
            return dict_gen[tag]
    else:
        return tag

def translate(
    src: str,
    target_language: str = "zh_cn",
    engine: str = "google-free",
    app_id: str = "",
    key: str = "",
    delay: int = 0,
):
    trans_result = ""
    if engine == "google-free":
        url = (
            "https://translate.google.cn/translate_a/single?client=gtx&dt=t&dj=1&ie=UTF-8&sl=auto&tl="
            + target_language
            + "&q="
            + src
        )
        result = get_html(url=url, return_type="object")

        translate_list = [i["trans"] for i in result.json()["sentences"]]
        trans_result = trans_result.join(translate_list)
    # elif engine == "baidu":
    #     url = "https://fanyi-api.baidu.com/api/trans/vip/translate"
    #     salt = random.randint(1, 1435660288)
    #     sign = app_id + src + str(salt) + key
    #     sign = hashlib.md5(sign.encode()).hexdigest()
    #     url += (
    #         "?appid="
    #         + app_id
    #         + "&q="
    #         + src
    #         + "&from=auto&to="
    #         + target_language
    #         + "&salt="
    #         + str(salt)
    #         + "&sign="
    #         + sign
    #     )
    #     result = get_html(url=url, return_type="object")
    #
    #     translate_list = [i["dst"] for i in result.json()["trans_result"]]
    #     trans_result = trans_result.join(translate_list)
    elif engine == "azure":
        url = "https://api.cognitive.microsofttranslator.com/translate?api-version=3.0&to=" + target_language
        headers = {
                'Ocp-Apim-Subscription-Key': key,
                'Ocp-Apim-Subscription-Region': "global",
                'Content-type': 'application/json',
                'X-ClientTraceId': str(uuid.uuid4())
            }
        body = json.dumps([{'text': src}])
        result = post_html(url=url,query=body,headers=headers)
        translate_list = [i["text"] for i in result.json()[0]["translations"]]
        trans_result = trans_result.join(translate_list)

    else:
        raise ValueError("Non-existent translation engine")
    
    time.sleep(delay)
    return trans_result

# ========================================================================是否为无码
def is_uncensored(number):
    if re.match('^\d{4,}', number) or re.match('n\d{4}', number) or 'HEYZO' in number.upper():
        return True
    configs = config.Config().get_uncensored()
    prefix_list = str(configs).split(',')
    for pre in prefix_list:
        if pre.upper() in number.upper():
            return True
    return False
