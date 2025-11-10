from datetime import datetime

import log_config
from Login import Login
from Problems import Problems
from Solution import Solutions
from User import process_user_data
from XML import generate_contest_xml
from config import LOGGING_CONFIG, CONTEST_CONFIG, COOKIE, AWARD_CONFIG

log_config.setup_logging(LOGGING_CONFIG)
log = log_config.get_logger(__name__)

excel_file = "user_info.xlsx"


def datetime_to_timestamp(datetime_str):
    """
    将日期时间字符串转换为时间戳

    参数:
        datetime_str: 日期时间字符串，格式如 '2025-10-20 13:00:00'

    返回:
        时间戳（浮点数）
    """
    try:
        # 将字符串转换为datetime对象
        dt_obj = datetime.strptime(datetime_str, '%Y-%m-%d %H:%M:%S')
        # 转换为时间戳
        timestamp = dt_obj.timestamp()
        return timestamp
    except ValueError as e:
        log.error(f"日期格式错误: {e}")
        return None


def _login(cookie):
    login = Login()
    if login.login_with_cookie_string(COOKIE):
        log.info(f'登录验证通过，开始进行题目爬取!')
        return login
    else:
        log.error(f'无法登录，请检查cookie是否正确')
        return 'Error'


def get_info():
    return {
        'length': CONTEST_CONFIG['length'],
        'penalty': CONTEST_CONFIG['penalty'],
        'starttime': datetime_to_timestamp(CONTEST_CONFIG['starttime']),
        'scoreboard-freeze-length': CONTEST_CONFIG['scoreboard-freeze-length']
    }


def get_finalized():
    return {
        'last_gold': AWARD_CONFIG['last_gold'],
        'last_silver': AWARD_CONFIG['last_silver'],
        'last_bronze': AWARD_CONFIG['last_bronze'],
        'timestamp': datetime_to_timestamp(CONTEST_CONFIG['endtime'])
    }


def main():
    log.info(f'开始登录...')
    login = _login(COOKIE)
    if login == 'Error':
        return

    log.info(f'开始获取比赛 {CONTEST_CONFIG["contest_id"]} 的题目列表....')
    problem = Problems(login)
    problem_list = problem.get_problem_list()
    log.info(f'题目列表获取成功: {problem_list}')

    log.info(f'开始获取比赛的所有用户的信息...')
    user_data = process_user_data(excel_file)
    log.info(f'获取用户信息成功，一共 {len(user_data)} 条用户信息')

    log.info(f'开始获取比赛基础信息...')
    info = get_info()
    log.info(f'比赛基础信息如下：{info}')

    log.info(f'开始获取提交记录信息...')
    solution = Solutions(login)
    solutions = solution.get_solution_list_data()
    log.info(f'比赛提交信息获取成功，一共 {len(solutions)} 条数据')

    log.info(f'开始设置奖项信息的获取...')
    finalized = get_finalized()
    log.info(f'奖项信息获取成功：{finalized}')

    log.info(f'开始生成比赛XML文件...')
    success = generate_contest_xml(problem_list, user_data, solutions, info, finalized)

    if success:
        log.info("比赛XML文件生成完成！")
    else:
        log.error("比赛XML文件生成失败！")




if __name__ == '__main__':
    log.info(f'{CONTEST_CONFIG["contest_id"]} 比赛滚榜数据处理开始...')
    main()
