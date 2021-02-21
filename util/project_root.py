import sys
from pathlib import Path


def get_project_root() -> Path:
    """
    返回项目所在目录。
    pyinstaller环境下返回项目运行临时目录。
    源码环境下返回AV_Data_Capture.py所在目录。
    """
    # 在pyinstaller环境下要返回tmp路径
    if getattr(sys, 'frozen', False):
        return Path(sys._MEIPASS) # type: ignore
    else:
        return Path(__file__).parent.parent


def get_exe_path() -> Path:
    """
    返回执行程序所在目录。
    pyinstaller环境下返回可执行文件目录。
    源码环境下返回AV_Data_Capture.py所在目录。
    """
    if getattr(sys, 'frozen', False):
        return Path(sys.executable).parent
    else:
        return get_project_root()
