"""用于存储单个影片，并负责将其存入nfo文件。"""
from __future__ import annotations

import os
import re

from avdc.config import Config
from avdc.model.rating import Rating
from avdc.util.actor_processor import process_actors
from avdc.util.studio_processor import process_studio
from avdc.util.tag_processor import process_tags, translate_tag_to_sc
from avdc.util.title_processor import process_title


class Movie:
    """
    用于存储单个影片的各类元数据。
    在写入nfo文件时会根据config决定是否使用各类标签的预处理器。
    如使用预处理器，在nfo文件中同时写入原数据。
    """
    def __init__(self):
        self._title: str = ''

        self._actors: list[str] = []

        self._release: str = ''

        self.year: str = ''

        self._cover_small: str = ''

        self._tags: list[str] = []

        self._studio: str = ''

        self.director: str = ''

        self.movie_id: str = ''

        self.cover: str = ''

        self.outline: str = ''

        self.runtime: str = ''

        self.series: str = ''

        self.scraper_source: str = ''

        self.label: str = ''

        self.trailer: str = ''

        self.website: str = ''

        self.imagecut: int = 0

        self.extra_fanart: list[str] = []

        self.original_path = ''

        self._ratings: list[Rating] = []

        self.fname_postfix = ''

        self._conf: Config = Config.get_instance()

    def __repr__(self):
        return f"""
                              读取影片信息
========================================================================
title:            {self.title}
short_title:      {self.short_title}
director:         {self.director}
actors:           {self.actors}
raw_actors:       {self.raw_actors}
first_actor:      {self.first_actor}
release:          {self.release}
year:             {self.year}
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
ratings:          {self.ratings}
website:          {self.website}
imagecut:         {self.imagecut}
extra_fanart:     {self.extra_fanart}
trailer:          {self.trailer}
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
        if isinstance(value, str):
            self._title = value

    @property
    def short_title(self) -> str:
        max_len = self._conf.max_title_len()
        return self.title[:max_len]

    @property
    def actors(self) -> list[str]:
        return process_actors(self._actors)

    @actors.setter
    def actors(self, value: list[str]) -> None:
        if not isinstance(value, list):
            return
        if len(value) == 0 or isinstance(value[0], str):
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
    def raw_actors(self) -> list[str]:
        return self._actors

    @property
    def cover_small(self) -> str:
        return self._cover_small

    @cover_small.setter
    def cover_small(self, value: str) -> None:
        if isinstance(value, str):
            tmp_arr = value.split(',')
            if len(tmp_arr) > 0:
                self._cover_small = tmp_arr[0].strip('\"').strip('\'')
            else:
                self._cover_small = value

    @property
    def tags(self) -> list[str]:
        return process_tags(self._tags)

    @tags.setter
    def tags(self, value: list[str]) -> None:
        if not isinstance(value, list):
            return
        if len(value) == 0 or isinstance(value[0], str):
            value = [i.strip() for i in value]
            value = [i for i in value if i]
            self._tags = value

    def add_tag(self, val: str) -> None:
        """往标签池内添加新标签。"""

        # 有码无码不能并存,优先后加的。
        if val == '无码' and '有码' in self._tags:
            self._tags.remove('有码')
        elif val == '有码' and '无码' in self._tags:
            self._tags.remove('无码')

        self._tags.append(val)

    @property
    def raw_tags(self) -> list[str]:
        return self._tags

    @property
    def release(self) -> str:
        return self._release

    @release.setter
    def release(self, value: str) -> None:
        if isinstance(value, str):
            self._release = value
            if re.match(r'\d{4}-\d\d?-\d\d?', self._release):
                self.year = value[:4]

    @property
    def studio(self) -> str:
        return process_studio(self._studio)

    @studio.setter
    def studio(self, value: str) -> None:
        if isinstance(value, str):
            self._studio = value

    @property
    def raw_studio(self) -> str:
        return self._studio

    def _eval_name(self, tmpl: str, use_short_title=True) -> str:
        title = self.short_title if use_short_title else self.title
        actor = ','.join(self.actors) or '未知演员'
        first_actor = self.first_actor or '未知演员'
        studio = self.studio or '未知片商'
        director = self.director or '未知导演'
        release = self.release or '1970-01-01'
        year = self.year or '1970'
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
        return self._eval_name(self._conf.filename_rule()) + self.fname_postfix

    @property
    def nfo_title(self) -> str:
        return self._eval_name(self._conf.nfo_title_rule(), False)

    @property
    def original_fname(self) -> str:
        return os.path.basename(self.original_path)

    @property
    def ratings(self) -> list[Rating]:
        # 按照投票人数排序
        # 如果没有人数的话保守按5人算
        self._ratings.sort(key=lambda rt: rt.votes or 5, reverse=True)
        return self._ratings

    def add_rating(self,
                   rating: float = 0.0,
                   max_rating: float = 10,
                   source: str = 'nfo',
                   votes: int = 0):
        new_rating = Rating(rating=rating,
                            max_rating=max_rating,
                            source=source,
                            votes=votes)
        if new_rating.is_valid():
            self._ratings.append(new_rating)

    def add_ratings(self, ratings: list[Rating]):
        existing = set(i.source for i in self._ratings)
        for r in ratings:
            if r.source not in existing:
                self._ratings.append(r)

    def is_filled(self) -> bool:
        """
        Returns true if both title and movie id are filled in this object.
        """
        if not self.title or self.title.lower() == 'null':
            return False

        if not self.movie_id or self.movie_id.lower() == 'null':
            return False

        return True

    def match_movie(self, other: Movie) -> bool:
        """
        检查两部影片是否是同一部。逻辑比较简陋。
        """
        if not self.is_filled():
            return False
        if not other.is_filled():
            return False
        if self.movie_id.upper() != other.movie_id.upper():
            return False
        return True

    def merge_tags(self, other: Movie) -> None:
        """
        将第二部电影的标签加入本电影的标签池中。
        标签会依靠标签翻译库进行简单去重。
        返回本电影。
        """
        # 单独跑，避免受到config的翻译flag影响
        existing_tag = set(process_tags(self._tags))
        for t in other._tags:
            if translate_tag_to_sc(t) not in existing_tag:
                existing_tag.add(translate_tag_to_sc(t))
                self._tags.append(t)
