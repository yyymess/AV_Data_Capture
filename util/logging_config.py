"""配置logging系统。"""
import logging

def config_logging(level = logging.INFO):
    fmt = '%(name)s %(levelname)s %(message)s'
    avdc_logger = logging.getLogger('avdc')
    logging.basicConfig(format = fmt)
    avdc_logger.setLevel(level)
