from __future__ import annotations  # Type hint for singleton

import os
import configparser
import logging
from pathlib import Path
from avdc.util.logging_config import config_logging

logger = logging.getLogger(__name__)


from typing import Union


class Config:
    _instance: Union[Config, None] = None

    def __init__(self, path: str = "config.ini") -> None:
        if Config._instance is None:
            Config._instance = self

        fname = os.path.basename(path)
        config_paths = [
            os.path.abspath('./' + path),
            os.path.join(os.getcwd(), fname),
            os.path.join(Path(__file__).parent, fname),
        ]

        for p in config_paths:
            if os.path.exists(p):
                logger.info(f'试图载入 {p}')
                parser = configparser.ConfigParser()
                try:
                    parser.read(p, encoding="utf-8-sig")
                    self._conf = parser
                    break
                except:
                    logger.error('配置文件{p}载入失败。')

        if not self._conf:
            logger.error('载入配置文件失败，使用默认配置。')
            self._conf = self._default_config()

        # TODO adding this here for now.
        self.folder_path = os.path.abspath(".")

    @staticmethod
    def get_instance(path: str = 'config.ini') -> Config:
        if Config._instance is None:
            Config._instance = Config(path)
            if Config._instance.debug():
                config_logging('DEBUG')
                logger.debug('Logger设定为DEBUG模式。')

            logger.debug(f'读取config文件 {path}')
        return Config._instance

    def main_mode(self) -> int:
        try:
            return self._conf.getint("common", "main_mode")
        except ValueError:
            self._exit("common:main_mode")

    def failed_folder(self) -> str:
        return self._conf.get("common", "failed_output_folder")

    def success_folder(self) -> str:
        return self._conf.get("common", "success_output_folder")

    def soft_link(self) -> bool:
        return self._conf.getboolean("common", "soft_link")
    def failed_move(self) -> bool:
        return self._conf.getboolean("common", "failed_move")
    def auto_exit(self) -> bool:
        return self._conf.getboolean("common", "auto_exit")
    def transalte_to_sc(self) -> bool:
        return self._conf.getboolean("common", "transalte_to_sc")
    def is_transalte(self) -> bool:
        return self._conf.getboolean("transalte", "switch")

    def translate_to_sc(self) -> bool:
        return self._conf.getboolean("common", "transalte_to_sc")
    def is_translate(self) -> bool:
        return self._conf.getboolean("transalte", "switch")


    def is_trailer(self) -> bool:
        return self._conf.getboolean("trailer", "switch")

    def is_watermark(self) -> bool:
        return self._conf.getboolean("watermark", "switch")

    def is_extrafanart(self) -> bool:
        return self._conf.getboolean("extrafanart", "switch")
    
    def watermark_type(self) -> int:
        return int(self._conf.get("watermark", "water"))

    def get_uncensored(self):
        try:
            sec = "uncensored"
            uncensored_prefix = self._conf.get(sec, "uncensored_prefix")
            # uncensored_poster = self.conf.get(sec, "uncensored_poster")
            return uncensored_prefix

        except ValueError:
            self._exit("uncensored")

    def get_extrafanart(self):
        try:
            extrafanart_download = self._conf.get("extrafanart", "extrafanart_folder")
            return extrafanart_download
        except ValueError:
            self._exit("extrafanart_folder")
    def get_transalte_engine(self) -> str:
        return self._conf.get("transalte","engine")
    # def get_transalte_appId(self) ->str:
    #     return self.conf.get("transalte","appid")
    def get_transalte_key(self) -> str:
        return self._conf.get("transalte","key")
    def get_transalte_delay(self) -> int:
        return self._conf.getint("transalte","delay")
    def transalte_values(self) -> str:
        return self._conf.get("transalte", "values")
    def proxy(self) -> [str, int, int, str]:
        try:
            sec = "proxy"
            switch = self._conf.get(sec, "switch")
            proxy = self._conf.get(sec, "proxy")
            timeout = self._conf.getint(sec, "timeout")
            retry = self._conf.getint(sec, "retry")
            proxytype = self._conf.get(sec, "type")
            return switch, proxy, timeout, retry, proxytype
        except ValueError:
            self._exit("common")

    def cacert_file(self) -> str:
        return self._conf.get('proxy', 'cacert_file')
            
    def media_type(self) -> str:
        return self._conf.get('media', 'media_type')

    def sub_rule(self):
        return self._conf.get('media', 'sub_type').split(',')
            
    def nfo_title_rule(self) -> str:
        return self._conf.get("Name_Rule", "nfo_title_rule")

    def location_rule(self) -> str:
        return self._conf.get("Name_Rule", "location_rule")

    def filename_rule(self) -> str:
        return self._conf.get(
            "Name_Rule", "filename_rule", fallback="number+' '+title")
    
    def max_title_len(self) -> int:
        """
        Maximum title length
        """
        return self._conf.getint("Name_Rule", "max_title_len", fallback=50)


    def update_check(self) -> bool:
        try:
            return self._conf.getboolean("update", "update_check")
        except ValueError:
            self._exit("update:update_check")

    def sources(self) -> str:
        return self._conf.get("priority", "website")

    def escape_literals(self) -> str:
        return self._conf.get("escape", "literals")

    def escape_folder(self) -> str:
        return self._conf.get("escape", "folders")

    def debug(self) -> bool:
        return self._conf.getboolean("debug_mode", "switch", fallback=False)

    @staticmethod
    def _exit(sec: str) -> None:
        print("[-] Read config error! Please check the {} section in config.ini", sec)
        input("[-] Press ENTER key to exit.")
        exit()

    @staticmethod
    def _default_config() -> configparser.ConfigParser:
        conf = configparser.ConfigParser()

        sec1 = "common"
        conf.add_section(sec1)
        conf.set(sec1, "main_mode", "1")
        conf.set(sec1, "failed_output_folder", "failed")
        conf.set(sec1, "success_output_folder", "JAV_output")
        conf.set(sec1, "soft_link", "0")
        conf.set(sec1, "failed_move", "1")
        conf.set(sec1, "auto_exit", "0")
        conf.set(sec1, "transalte_to_sc", "1")

        sec2 = "proxy"
        conf.add_section(sec2)
        conf.set(sec2, "proxy", "")
        conf.set(sec2, "timeout", "5")
        conf.set(sec2, "retry", "3")
        conf.set(sec2, "type", "socks5")
        conf.set(sec2, "cacert_file", "")


        sec3 = "Name_Rule"
        conf.add_section(sec3)
        conf.set(sec3, "location_rule", "actor + '/' + number")
        conf.set(sec3, "nfo_title_rule", "number + '-' + title")
        conf.set(sec3, "filename_rule", "number + ' ' + title")
        conf.set(sec3, "max_title_len", "50")

        sec4 = "update"
        conf.add_section(sec4)
        conf.set(sec4, "update_check", "1")

        sec5 = "priority"
        conf.add_section(sec5)
        conf.set(sec5, "website", "airav,javbus,javdb,fanza,xcity,mgstage,fc2,avsox,jav321,xcity")

        sec6 = "escape"
        conf.add_section(sec6)
        conf.set(sec6, "literals", "\()/")  # noqa
        conf.set(sec6, "folders", "failed, JAV_output")

        sec7 = "debug_mode"
        conf.add_section(sec7)
        conf.set(sec7, "switch", "0")

        sec8 = "transalte"
        conf.add_section(sec8)
        conf.set(sec8, "switch", "0")
        conf.set(sec8, "engine", "google-free")
        # conf.set(sec8, "appid", "")
        conf.set(sec8, "key", "")
        conf.set(sec8, "delay", "1")
        conf.set(sec8, "values", "title,outline")
        
        sec9 = "trailer"
        conf.add_section(sec9)
        conf.set(sec9, "switch", "0")

        sec10 = "uncensored"
        conf.add_section(sec10)
        conf.set(sec10, "uncensored_prefix", "S2M,BT,LAF,SMD")

        sec11 = "media"
        conf.add_section(sec11)
        conf.set(sec11, "media_type", ".mp4,.avi,.rmvb,.wmv,.mov,.mkv,.flv,.ts,.webm,.MP4,.AVI,.RMVB,.WMV,.MOV,.MKV,.FLV,.TS,.WEBM,iso,ISO")
        conf.set(sec11, "sub_type", ".smi,.srt,.idx,.sub,.sup,.psb,.ssa,.ass,.txt,.usf,.xss,.ssf,.rt,.lrc,.sbv,.vtt,.ttml")

        sec12 = "watermark"
        conf.add_section(sec12)
        conf.set(sec12, "switch", 1)
        conf.set(sec12, "water", 2)

        sec13 = "extrafanart"
        conf.add_section(sec13)
        conf.set(sec13, "switch", 1)
        conf.set(sec13, "extrafanart_folder", "extrafanart")

        return conf


if __name__ == "__main__":
    config = Config.get_instance()
    print(config.main_mode())
    print(config.failed_folder())
    print(config.success_folder())
    print(config.soft_link())
    print(config.failed_move())
    print(config.auto_exit())
    print(config.proxy())
    print(config.nfo_title_rule())
    print(config.location_rule())
    print(config.update_check())
    print(config.sources())
    print(config.escape_literals())
    print(config.escape_folder())
    print(config.debug())
    print(config.is_transalte())
    print(config.get_transalte_engine())
    # print(config.get_transalte_appId())
    print(config.get_transalte_key())
    print(config.get_transalte_delay())
    print(config.transalte_values())
