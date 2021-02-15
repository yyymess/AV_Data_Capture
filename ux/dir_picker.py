"""返回用户选择的文件夹"""
from tkinter import filedialog


def dir_picker() -> str:
    """返回用户选择的文件夹.
    以后再做点啥。"""
    return filedialog.askdirectory()
