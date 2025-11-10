import logging
from datetime import datetime

LOGGING_CONFIG = {
    'lowest_level': logging.DEBUG,
    'console_level': logging.INFO,
    'file_level': logging.DEBUG,
    'log_dir': f'./log/{datetime.now().strftime("%Y%m%d-%H")}',
    'log_file': f'{datetime.now().strftime("%Y%m%d-%H'%M")}.log',
    'file_formatter': '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s',
    'color_formatter': {
        'format': '%(log_color)s%(asctime)s - %(name)s - %(''levelname)s - %(filename)s:%(lineno)d - ''%(message)s',
        'datefmt': None,
        'reset': True,
        'log_colors': {'DEBUG': 'cyan', 'INFO': 'green', 'WARNING': 'yellow', 'ERROR': 'red',
                       'CRITICAL': 'red,bg_yellow'},
        'secondary_log_colors': {},
        'style': '%',
    },
    'file_handler': {
        'maxBytes': 10 * 1024 * 1024,
        'backupCount': 5,
        'encoding': 'utf-8',
    }
}

CONTEST_CONFIG = {
    'length': '5:00:00',  # 比赛时长
    'penalty': '20',  # 罚时
    'starttime': '2025-10-26 13:00:00',  # 比赛开始时间
    'endtime': '2025-10-26 18:00:00',  # 比赛结束时间
    'scoreboard-freeze-length': '1:00:00',  # 封榜时长，最后30分钟封榜
    'contest_baseUrl': 'https://icpc.ldu.edu.cn/contests',
    'contest_id': '4105',
    'name': '测试滚榜活动1'
}

AWARD_CONFIG = {
    'last_gold': 2,  # 金牌最后一名
    'last_silver': 5,  # 银牌最后一名
    'last_bronze': 10,  # 铜牌最后一名
}

COOKIE = 'unencrypted_contests_default_cate=16; unencrypted_solutions_default_perpage=10; remember_web_59ba36addc2b2f9401580f014c7f58ea4e30989d=eyJpdiI6Ilc5aFM3UkFTVjN0ZUdhbGNlTm92aVE9PSIsInZhbHVlIjoiMGtHSXc3MTJTM2hnTE1YK1dZMFRRRDJ5UVFoY0pUalBEdkViUDNzdFc2ckl4Y1NzZnd2V25DdS9EWUtmSkQ3bys3Wm8zcEVOSGRvSlJPRXRuMldNQ1VGK2Q1QjlhV2c4VGVSNStmYk1KUjlUQWJ5TEx1bTVnQjByOWFPa0s5b3Q4Y29PM1phUzNqaTMwV1B4V2FKdFFJUVhDWmVyK2tpYjBoaHBFTEhzZGkwZ0dHQ2swSncvVjlXb2Y1TUtwOC9sWjg4TFczQURGMC9OZy94V05SV0IxUDVlOEdrNGhwYkpZTmgrck5mQUhncz0iLCJtYWMiOiIyMDZmMzk2N2EzODI1YThlNzZjMjJjMDI2MDc2MTcwNzNkZDE2MzhjOGRlNmFkYzQxMmNiYzQxNTVmYjc2MDNiIiwidGFnIjoiIn0%3D; onlinejudge_session=eyJpdiI6ImJTZEc1QU4wWjUrZVZrQVhmeW0rWkE9PSIsInZhbHVlIjoicmNJSWluV3VIR1dpZ2NkNHRCSFc0NTk4UFZXeFptdjQ0QUVsQTdHcmhnZjB5aW4xU2dMazQ0VzBlb0pHUFZRbHdzNEVGZUQvaHZMLzd0QVJPbXFnVlJhREhUUlZCU3hmVmRvVmloSk1Cc0NkbGpzN0xWUFJRUnJ1d1diMm5kQWwiLCJtYWMiOiJlMzE1NTFiNTE0NmY5MTM3NTlkNmViZGI4MDc3NzZiYWQxYWVlYzQzYzJmN2IwMGVlMDE0M2JhMTczNmQ4M2MzIiwidGFnIjoiIn0%3D'
