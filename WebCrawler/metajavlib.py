"""
主要依靠javlibrary，用jav321补全简介和系列。
缺东西的话再去javdb搜搜。 暂时是野蛮粗暴型，回头用getattr和setattr重写。

TODO: 这货的长期目标应该是一个可以用config自定义的多源刮削器。
"""

from avdc.model.movie import Movie
from avdc.WebCrawler import jav321, javdb, javlib


def main(number: str) -> Movie:
    javlib_scrap = javlib.main(number)
    if not javlib_scrap.is_filled():
        return javlib_scrap

    jav321_scrap = jav321.main(javlib_scrap.movie_id)
    javdb_scrap = javdb.main(javlib_scrap.movie_id)
    if not javlib_scrap.match_movie(jav321_scrap):
        jav321_scrap = Movie()
    if not javlib_scrap.match_movie(javdb_scrap):
        javdb_scrap = Movie()

    javlib_scrap.series = jav321_scrap.series or javdb_scrap.series
    javlib_scrap.outline = jav321_scrap.outline or javdb_scrap.outline
    javlib_scrap.extra_fanart = (jav321_scrap.extra_fanart or javdb_scrap.extra_fanart)
    javlib_scrap.ratings.extend(javdb_scrap.ratings)

    if not javlib_scrap.actors:
        javlib_scrap.actors = javdb_scrap.actors or jav321_scrap.actors

    if not javlib_scrap.director:
        javlib_scrap.director = javdb_scrap.director or jav321_scrap.director

    if not javlib_scrap.studio:
        javlib_scrap.studio = javdb_scrap.studio or jav321_scrap.studio

    if not javlib_scrap.series:
        javlib_scrap.series = javdb_scrap.series or jav321_scrap.series

    javlib_scrap.merge_tags(jav321_scrap)
    javlib_scrap.merge_tags(javdb_scrap)


    return javlib_scrap


if __name__ == "__main__":
    print(main("xrw-565"))
    print(main("jul-404"))
