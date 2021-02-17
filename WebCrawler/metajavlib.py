"""主要依靠javlibrary，用jav321补全简介和系列。"""
from avdc.WebCrawler import javlib
from avdc.WebCrawler import jav321

from avdc.model.movie import Movie

def main(number: str) -> Movie:
    javlib_scrap = javlib.main(number)
    if not javlib_scrap.is_filled():
        return javlib_scrap

    if not javlib_scrap.outline or not javlib_scrap.series:
        jav321_scrip = jav321.main(javlib_scrap.movie_id)
        if jav321_scrip.movie_id.upper() == javlib_scrap.movie_id.upper():
            javlib_scrap.series = jav321_scrip.series
            javlib_scrap.outline = jav321_scrip.outline

    return javlib_scrap

if __name__ == "__main__":
    print(main("xrw-565"))
    print(main("jul-404"))
