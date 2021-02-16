'''用于存储单个影片，并负责将其存入nfo文件。'''

import os
from avdc.config import Config
from avdc.util.tag_processor import process_tags
from avdc.util.studio_processor import process_studio
from avdc.util.title_processor import process_title
from typing import List

class Movie:
    '''
    用于存储单个影片的各类元数据。
    在写入nfo文件时会根据config决定是否使用各类标签的预处理器。
    如使用预处理器，在nfo文件中同时写入原数据。
    '''
    def __init__(self):
        self._title: str = ''

        self._actors: List[str] = []

        self.release: str = ''

        self.year: str = ''

        self._cover_small: str = ''

        self._tags: List[str] = []

        self._studio: str = ''

        self._director: str = ''

        self._movie_id: str = ''

        self._cover: str = ''

        self._outline: str = ''

        self.runtime: str = ''

        self.series: str = ''

        self.scraper_source: str = ''

        self._label: str = ''

        self._trailer: str = ''

        self.website: str = ''

        self._imagecut: int = 0

        self._extra_fanart: List[str] = []

        self.original_path = ''

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
raw_tags:         {self.raw_tags}
studio:           {self.studio}
raw_studio:       {self.raw_studio}
movie_id:         {self.movie_id}
outline:          {self.outline}
runtime:          {self.runtime}
series:           {self.series}
scraper_source:   {self.scraper_source}
label:            {self.label}
website:          {self.website}
imagecut:         {self.imagecut}
extra_fanart:     {self.extra_fanart}
storage_dir:      {self.storage_dir}
storage_fname:    {self.storage_fname}
original_path:    {self.original_path}
original_fname:   {self.original_fname}
========================================================================
"""
    @property
    def title(self) -> str:
        return process_title(self._title)

    @title.setter
    def title(self, value: str) -> None:
        if value:
            self._title = value

    @property
    def short_title(self) -> str:
        max_len = self._conf.max_title_len()
        return self.title[:max_len]

    @property
    def actors(self) -> List[str]:
        return self._actors

    @actors.setter
    def actors(self, value: List[str]) -> None:
        if value:
            value = [i.strip() for i in value]
            value = [i for i in value if i]
            self._actors = value

    @property
    def first_actor(self) -> str:
        if len(self.actors) > 0:
            return self.actors[0]
        else:
            return ''

    @property
    def cover_small(self) -> str:
        return self._cover_small

    @cover_small.setter
    def cover_small(self, value: str) -> None:
        if value:
            tmp_arr = value.split(',')
            if len(tmp_arr) > 0:
                self._cover_small = tmp_arr[0].strip('\"').strip('\'')
            else:
                self._cover_small = value

    @property
    def tags(self) -> List[str]:
        return process_tags(self._tags)

    @tags.setter
    def tags(self, value: List[str]) -> None:
        if value:
            self._tags = value

    @property
    def raw_tags(self) -> List[str]:
        return self._tags

    @property
    def studio(self) -> str:
        return process_studio(self._studio)

    @studio.setter
    def studio(self, value: str) -> None:
        if value:
            self._studio = value

    @property
    def raw_studio(self) -> str:
        return self._studio

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
    def label(self) -> str:
        return self._label

    @label.setter
    def label(self, value: str) -> None:
        if value:
            self._label = value

    @property
    def trailer(self) -> str:
        if self._conf.is_trailer():
            return self._trailer
        else:
            return ''

    @trailer.setter
    def trailer(self, value: str) -> None:
        if value:
            self._trailer = value

    @property
    def imagecut(self) -> int:
        return self._imagecut

    @imagecut.setter
    def imagecut(self, value: int) -> None:
        if value:
            self._imagecut = value

    @property
    def extra_fanart(self) -> List[str]:
        if self._conf.is_extrafanart():
            return self._extra_fanart
        else:
            return []

    @extra_fanart.setter
    def extra_fanart(self, value: List[str]) -> None:
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

    @property
    def original_fname(self) -> str:
        return os.path.basename(self.original_path)

    def is_filled(self) -> bool:
        """
        Returns true if both title and movie id are filled in this object.
        """
        if not self.title or self.title.lower() == 'null':
            return False

        if not self.movie_id or self.movie_id.lower() == 'null':
            return False

        return True
