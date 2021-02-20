"""
主要依靠javlibrary，用jav321补全简介和系列。

TODO: 这货的长期目标应该是一个可以用config自定义的多源刮削器。
"""

from avdc.model.movie import Movie
from avdc.WebCrawler import jav321, javlib


def main(number: str) -> Movie:
    javlib_scrap = javlib.main(number)
    if not javlib_scrap.is_filled():
        return javlib_scrap

    jav321_scrip = jav321.main(javlib_scrap.movie_id)
    if jav321_scrip.movie_id.upper() == javlib_scrap.movie_id.upper():
        javlib_scrap.series = javlib_scrap.series or jav321_scrip.series
        javlib_scrap.outline = javlib_scrap.outline or jav321_scrip.outline
        javlib_scrap.extra_fanart = (javlib_scrap.extra_fanart
                                     or jav321_scrip.extra_fanart)

    return javlib_scrap


if __name__ == "__main__":
    print(main("xrw-565"))
    print(main("jul-404"))
