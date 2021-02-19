"""
用于生成女优姓名对照表。 没事手动执行一下既可。
暂行方案：
- 使用github.com/xinxin8816/gfriends的json文件获取一对一参照
- 使用1:1 map生成每个名字被映射次数的列表
- 使用每个名称出现的频率来判断哪个名字为主要名，假设高频用名同时代表更多对应的图像文件
- 输出csv，模式为
  主要名，别名，别名，别名。。。。

这货实际上可以在使用时动态调用gfriends的数据库，不过本地化CSV能减少一个point of failure.
"""

import csv
import json
import os
import sys
from collections import Counter, defaultdict
from collections.abc import Iterable
from traceback import format_exc

import requests
from avdc.util.project_root import get_project_root


def gen_file() -> None:
    dupe_list = reduce_gfriends_map()
    print(f'√ 共检测到{len(dupe_list):,}位重名女友。')

    output_filepath = os.path.join(get_project_root(), 'data',
                                   'actor_dupe_map.csv')
    with open(output_filepath, 'wt', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        csvfile.write('# 女优名, 别名, 别名, …………')
        # 用csv来换行保证换行符一致性。
        writer.writerow([])
        writer.writerows(dupe_list)


def reduce_gfriends_map() -> list[str]:
    """
    将1:1的map按女优做成group。
    返回 list[别名列表] 方便后续输出。
    """
    gf_map = get_gfriends_map()
    name_to_counter: dict[str, Counter[str]] = defaultdict(hashableCounter)

    # 用counter数每个名字被映射的次数
    # 每次出现映射关系的时候合并两边的counter计数
    # 得到的结果就是每个counter内包含同一个女优的不同别名
    for source, target in gf_map:
        target_counter = name_to_counter[target]
        target_counter[target] += 1
        target_counter[source] += 0

        if source not in name_to_counter:
            name_to_counter[source] = target_counter
        elif name_to_counter[source] != target_counter:
            # 两个名字都各自被map过，合并。
            target_counter.update(name_to_counter[source])
            name_to_counter[source] = target_counter

    all_actors_dicts = set(name_to_counter.values())
    result_list = []
    for d in all_actors_dicts:
        actors = [key for key, _ in d.most_common()]
        if len(actors) == 1:
            # 没有重名的女优，可以无视了
            continue
        result_list.append(actors)

    # 按名字排序下，稳定git更新
    result_list.sort()
    return result_list


def get_gfriends_map() -> Iterable[tuple[str, str]]:
    """
    从gfriends挖过来改了改。
    返回一个(别名，实用名)列表。
    """
    print('>> 连接 Gfriends 女友头像仓库...')
    filetree_url = ('https://raw.githubusercontent.com/'
                    'xinxin8816/gfriends/master/Filetree.json')
    try:
        response = requests.get(filetree_url)
        response.encoding = 'utf-8'
    except:
        print(format_exc())
        print('× 网络连接异')
        sys.exit()
    if response.status_code != 200:
        print('× 女友仓库返回了一个错误：' + str(response.status_code))
        sys.exit()

    # 只管名字，所以把aifix都去掉。
    map_json = json.loads(response.text.replace('AI-Fix-', ''))
    output = {}

    first_lvls = map_json.keys()
    for first in first_lvls:
        second_lvls = map_json[first].keys()
        for second in second_lvls:
            for k, v in map_json[first][second].items():
                # 处理据库内个别错误信息
                if '???' not in k + v:
                    output[os.path.splitext(k)[0]] = os.path.splitext(v)[0]
    print('√ 连接 Gfriends 女友头像仓库成功')
    return output.items()


class hashableCounter(Counter):
    """ 方便用set暴力去重的Counter。 """
    def __hash__(self):
        return hash(id(self))

    def __eq__(self, x):
        return x is self

    def __ne__(self, x):
        return x is not self


if __name__ == '__main__':
    gen_file()
