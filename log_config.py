import logging
import logging.handlers
from pathlib import Path
import colorlog

from config import LOGGING_CONFIG


def setup_logging(LOGGING_CONFIG):
    # 创建日志目录（如果不存在）
    log_path = Path(LOGGING_CONFIG['log_dir'])
    log_path.mkdir(parents=True, exist_ok=True)

    # 完整的日志路径
    log_file_path = log_path / LOGGING_CONFIG['log_file']

    # 创建日志记录器
    logger = logging.getLogger()
    logger.setLevel(LOGGING_CONFIG['lowest_level'])  # 设置最低级别，处理器会过滤

    # 避免重复添加处理器（防止多次调用此函数时重复添加）
    if logger.handlers:
        for handler in logger.handlers[:]:
            logger.removeHandler(handler)

    file_formatter = logging.Formatter(
        LOGGING_CONFIG['file_formatter']
    )

    # 1. 创建文件处理器 - 记录所有级别的日志（DEBUG及以上的所有级别）
    file_handler = logging.handlers.RotatingFileHandler(
        log_file_path,
        maxBytes=LOGGING_CONFIG['file_handler']['maxBytes'],  # 10MB
        backupCount=LOGGING_CONFIG['file_handler']['backupCount'],
        encoding=LOGGING_CONFIG['file_handler']['encoding']
    )
    file_handler.setLevel(LOGGING_CONFIG['file_level'])
    file_handler.setFormatter(file_formatter)

    # 2. 创建控制台处理器 - 只记录WARNING及以上的日志
    color_formatter = colorlog.ColoredFormatter(
        LOGGING_CONFIG['color_formatter']['format'],
        datefmt=LOGGING_CONFIG['color_formatter']['datefmt'],
        reset=LOGGING_CONFIG['color_formatter']['reset'],
        log_colors={
            'DEBUG': LOGGING_CONFIG['color_formatter']['log_colors']['DEBUG'],
            'INFO': LOGGING_CONFIG['color_formatter']['log_colors']['INFO'],
            'WARNING': LOGGING_CONFIG['color_formatter']['log_colors']['WARNING'],
            'ERROR': LOGGING_CONFIG['color_formatter']['log_colors']['ERROR'],
            'CRITICAL': LOGGING_CONFIG['color_formatter']['log_colors']['CRITICAL'],
        },
        secondary_log_colors=LOGGING_CONFIG['color_formatter']['secondary_log_colors'],
        style=LOGGING_CONFIG['color_formatter']['style']
    )

    console_handler = colorlog.StreamHandler()
    console_handler.setLevel(LOGGING_CONFIG['console_level'])
    console_handler.setFormatter(color_formatter)

    # 将处理器添加到根日志记录器
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    # 记录初始信息
    logger.info("=" * 50)
    logger.info("日志系统已初始化")
    logger.info(f"控制台级别: {logging.getLevelName(LOGGING_CONFIG['console_level'])}")
    logger.info(f"文件记录级别: {logging.getLevelName(LOGGING_CONFIG['file_level'])}")
    logger.info(f"日志文件保存在: {log_file_path.absolute()}")
    logger.info("=" * 50)


# 创建获取日志记录器的便捷函数
def get_logger(name=None):
    """
    获取配置好的日志记录器

    参数:
        name (str): 日志记录器名称，通常使用__name__

    返回:
        Logger: 配置好的日志记录器
    """
    return logging.getLogger(name)


# 示例：演示不同级别的日志
def demo_log_levels():
    """演示不同级别的日志输出"""
    logger = get_logger(__name__)

    logger.debug("这是一条DEBUG级别的消息 - 通常用于调试信息")
    logger.info("这是一条INFO级别的消息 - 通常用于常规信息")
    logger.warning("这是一条WARNING级别的消息 - 通常用于警告信息")
    logger.error("这是一条ERROR级别的消息 - 通常用于错误信息")
    logger.critical("这是一条CRITICAL级别的消息 - 通常用于严重错误信息")

    # 演示异常记录
    try:
        result = 10 / 0
    except Exception as e:
        logger.exception("发生除零错误: %s", e)


# 如果直接运行此模块，则进行演示
if __name__ == "__main__":
    # 配置日志系统
    setup_logging(LOGGING_CONFIG)

    # 演示不同级别的日志
    demo_log_levels()
