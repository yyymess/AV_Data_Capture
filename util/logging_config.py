"""配置logging系统。"""
import logging

root_logger = logging.getLogger('root')
avdc_logger = logging.getLogger('avdc')
console_handler = logging.StreamHandler()
root_logger.addHandler(console_handler)


def config_logging(level: str = 'INFO', root=False):
    logger = avdc_logger
    if root:
        logger = logging.getLogger('root')
    if level == 'DEBUG':
        logger.setLevel(logging.DEBUG)
        formatter = _DebugFormatter()
    else:
        logger.setLevel(logging.INFO)
        formatter = _InfoFormatter()
    console_handler.setFormatter(formatter)

class _CustomLogger(logging.Logger):
    is_initialized = False
    # 增加一个attn级别的logging
    def attn(self, msg, *args, **kwargs):
        super().log(25, msg, *args, **kwargs)

def get_logger(name:str) -> _CustomLogger:
    if not _CustomLogger.is_initialized:
        logging.setLoggerClass(_CustomLogger)
        logging.addLevelName(25, 'ATTN')
        _CustomLogger.is_initialized = True
    return logging.getLogger(name)

_WHITE = '\u001b[38;5;15m'
_GREY = '\u001b[38;5;8m'
_YELLOW = '\u001b[38;5;11m'
_RED = '\u001b[38;5;9m'
_BOLD_RED = '\u001b[38;5;1m\033[1m'
_RESET = "\u001B[0m"


class _InfoFormatter(logging.Formatter):
    """
    简化Info模式下logging的level输出。
    """
    def __init__(self, fmt='%(msg)s'):
        super().__init__(fmt)

    def _format_msg(self, record, msg) -> str:
        level = record.levelname
        if level == 'ATTN':
            return f'[-]{_WHITE}{msg}{_RESET}'
        if level == 'WARNING':
            return f'[+]{_YELLOW}{msg}{_RESET}'
        elif level == 'ERROR':
            return f'[!]{_RED}{msg}{_RESET}'
        elif level == 'CRITICAL':
            return f'[!]{_BOLD_RED}{msg}{_RESET}'
        else:
            return f'[*]{_WHITE}{msg}{_RESET}'

    def format(self, record):
        result = super().format(record)
        return self._format_msg(record, result)


class _DebugFormatter(_InfoFormatter):
    """
    简化Info模式下logging的level输出。
    """
    def __init__(
            self,
            fmt='%(name)s %(filename)s:%(lineno)s %(levelname)s %(message)s'):
        super().__init__(fmt)

    def _format_msg(self, record, msg) -> str:
        level = record.levelname
        if level in ('INFO', 'ATTN'):
            return f'{_WHITE}{msg}{_RESET}'
        elif level == 'WARNING':
            return f'{_YELLOW}{msg}{_RESET}'
        elif level == 'ERROR':
            return f'{_RED}{msg}{_RESET}'
        elif level == 'CRITICAL':
            return f'{_BOLD_RED}{msg}{_RESET}'
        else:
            return f'{_GREY}{msg}{_RESET}'


if __name__ == '__main__':
    print('''
------------------
info logging test.
------------------
''')

    logger = get_logger('avdc.logging')
    config_logging('INFO')
    logger.debug('This is DEBUG')
    logger.info('This is INFO')
    logger.attn('This is ATTN')
    logger.warning('This is WARNING')
    logger.error('This is ERROR')
    logger.critical('This is CRITICAL')

    print('''
------------------
debug logging test.
------------------
''')
    config_logging('DEBUG')
    logger.debug('This is DEBUG')
    logger.info('This is INFO')
    logger.attn('This is INFO')
    logger.warning('This is WARNING')
    logger.error('This is ERROR')
    logger.critical('This is CRITICAL')
