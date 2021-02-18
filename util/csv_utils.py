"""统一csv读取逻辑。"""

from typing import Iterator
import csv

def read_csv(filepath) -> Iterator[list[str]]:
    with open(filepath, 'r', encoding = 'utf-8', newline = '') as f:
        csv_reader = csv.reader(f)
        for row in csv_reader:
            if not row:
                # 空行
                continue

            returnval = [i.strip() for i in row]

            if row[0][0] == '#':
                # 注释
                continue
            yield returnval
