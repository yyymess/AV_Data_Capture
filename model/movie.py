'''用于存储单个影片，并负责将其存入nfo文件。'''

from avdc.config import Config
from avdc.util.tag_processor import process_tags

class Movie:
    '''
    用于存储单个影片的各类元数据。
    在写入nfo文件时会根据config决定是否使用各类标签的预处理器。
    如使用预处理器，在nfo文件中同时写入原数据。
    '''
    def __init__(self):
        self._title: str = ''

        self._actor: [str] = []

        self._release: str = ''

        self._year: str = ''

        self._cover_small: str = ''

        self._tags: [str] = ''

        self._studio: str = ''

        self._director: str = ''

        self._movie_id: str = ''

        self._cover: str = ''

        self._outline: str = ''

        self._runtime: str = ''

        self._series: str = ''

        self._scraper_source: str = ''

        self._label: str = ''

        self._trailer: str = ''

        self._website: str = ''

        self._imagecut: int = 0

        self._extra_fanart: str = ''

        self._conf: Config = Config.get_instance()
    def __repr__(self):
        return f"""
                              读取影片信息
========================================================================
title:            {self.title}
short_title:      {self.short_title}
director:         {self.director}
actors:           {self.actors}
first_actor:      {self.first_actor}
release:          {self.release}
cover:            {self.cover}
cover_small:      {self.cover_small}
tags:             {self.tags}
processed_tags:   {self.processed_tags}
studio:           {self.studio}
movie_id:         {self.movie_id}
outline:          {self.outline}
runtime:          {self.runtime}
series:           {self.series}
scraper_source:   {self.scraper_source}
label:            {self.label}
imagecut:         {self.imagecut}
extra_fanart:     {self.extra_fanart}
storage_dir:      {self.storage_dir}
storage_fname:    {self.storage_fname}
========================================================================
"""

    @property
    def title(self) -> str:
        return self._title

    @title.setter
    def title(self, value: str) -> None:
        if value:
            self._title = value

    @property
    def short_title(self) -> str:
        max_len = self._conf.max_title_len()
        return self._title[:max_len]

    @property
    def actors(self) -> [str]:
        return self._actor

    @actors.setter
    def actors(self, value: [str]) -> None:
        if value:
            self._actor = value

    @property
    def first_actor(self) -> str:
        if len(self.actors) > 0:
            return self.actors[0]
        else:
            return ''

    @property
    def release(self) -> str:
        return self._release

    @release.setter
    def release(self, value: str) -> None:
        if value:
            self._release = value

    @property
    def cover_small(self) -> str:
        return self._cover_small

    @cover_small.setter
    def cover_small(self, value: str) -> None:
        if value:
            self._cover_small = value

    @property
    def tags(self) -> [str]:
        return self._tags

    @tags.setter
    def tags(self, value: [str]) -> None:
        if value:
            self._tags = value

    @property
    def processed_tags(self) -> [str]:
        return process_tags(self.tags)

    @property
    def studio(self) -> str:
        return self._studio

    @studio.setter
    def studio(self, value: str) -> None:
        if value:
            self._studio = value

    @property
    def director(self) -> str:
        return self._director

    @director.setter
    def director(self, value: str) -> None:
        if value:
            self._director = value

    @property
    def movie_id(self) -> str:
        return self._movie_id

    @movie_id.setter
    def movie_id(self, value: str) -> None:
        if value:
            self._movie_id = value

    @property
    def cover(self) -> str:
        return self._cover

    @cover.setter
    def cover(self, value: str) -> None:
        if value:
            self._cover = value

    @property
    def outline(self) -> str:
        return self._outline

    @outline.setter
    def outline(self, value: str) -> None:
        if value:
            self._outline = value

    @property
    def runtime(self) -> str:
        return self._runtime

    @runtime.setter
    def runtime(self, value: str) -> None:
        if value:
            self._runtime = value

    @property
    def series(self) -> str:
        return self._series

    @series.setter
    def series(self, value: str) -> None:
        if value:
            self._series = value

    @property
    def scraper_source(self) -> str:
        return self._scraper_source

    @scraper_source.setter
    def scraper_source(self, value: str) -> None:
        if value:
            self._scraper_source = value

    @property
    def label(self) -> str:
        return self._label

    @label.setter
    def label(self, value: str) -> None:
        if value:
            self._label = value

    @property
    def trailer(self) -> str:
        return self._trailer

    @trailer.setter
    def trailer(self, value: str) -> None:
        if value:
            self._trailer = value

    @property
    def website(self) -> str:
        return self._website

    @website.setter
    def website(self, value: str) -> None:
        if value:
            self._website = value

    @property
    def imagecut(self) -> int:
        return self._imagecut

    @imagecut.setter
    def imagecut(self, value: int) -> None:
        if value:
            self._imagecut = value

    @property
    def extra_fanart(self) -> str:
        return self._extra_fanart

    @extra_fanart.setter
    def extra_fanart(self, value: str) -> None:
        if value:
            self._extra_fanart = value

    def _eval_name(self, tmpl: str) -> str:
        title = self.short_title
        actor = ','.join(self.actors)
        first_actor = self.first_actor
        studio = self.studio
        director = self.director
        release = self.release
        year = self.year
        number = self.movie_id
        cover = self.cover
        tag = ','.join(self.tags)
        outline = self.outline
        runtime = self.runtime
        series = self.series

        if len(actor) > 100:
            actor = '多人作品'
        return eval(tmpl)

    @property
    def storage_dir(self) -> str:
        return self._eval_name(self._conf.location_rule())

    @property
    def storage_fname(self) -> str:
        return self._eval_name(self._conf.naming_rule())
