from pathlib import Path
import sys

def get_project_root() -> Path:
    # 在pyinstaller环境下要返回tmp路径
    if getattr(sys, 'frozen', False):
        print(Path(sys._MEIPASS))
        return Path(sys._MEIPASS)
    else:
        return Path(__file__).parent.parent

def get_exe_path() -> Path:
    """
    返回主程序所在目录。
    """
    if getattr(sys, 'frozen', False):
        return Path(sys.executable).parent
    else:
        return get_project_root()
