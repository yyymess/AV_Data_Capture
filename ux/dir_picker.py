"""返回用户选择的文件夹"""
from tkinter import Tk,filedialog

def dir_picker() -> str:
    """返回用户选择的文件夹.
    以后再做点啥。"""
    Tk().withdraw()
    return filedialog.askdirectory()
