import json
import os
import time
import re
from datetime import datetime

import log_config
from config import CONTEST_CONFIG
import bs4

log = log_config.get_logger(__name__)


class Solutions:
    def __init__(self, login_session):
        self.session = login_session.get_session()
        self.baseUrl = CONTEST_CONFIG['contest_baseUrl']
        self.contestId = CONTEST_CONFIG['contest_id']
        self.contest_start_time = CONTEST_CONFIG['starttime']
        self.contest_end_time = CONTEST_CONFIG['endtime']

    def get_solution_list(self):
        """获取比赛提交记录列表"""
        try:
            log.info(f'开始获取比赛提交记录: {self.baseUrl}/{self.contestId}/solutions?perPage=10000000')

            # 构建提交记录URL
            solutions_url = f"{self.baseUrl}/{self.contestId}/solutions?perPage=10000000"

            # 发送请求
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36 Edg/141.0.0.0',
                'Referer': f'{self.baseUrl}/{self.contestId}/solutions?perPage=10000000'
            }

            response = self.session.get(solutions_url, headers=headers)
            log.info(f'发送GET请求，获得响应: {response.status_code}')

            if response.status_code != 200:
                log.error(f"获取提交记录失败，状态码: {response.status_code}")
                return None

            # 解析HTML
            soup = bs4.BeautifulSoup(response.text, 'html.parser')

            # 提取提交记录信息
            solution_list = self._parse_solution_list(soup)

            # 过滤提交记录（只保留比赛时间内的记录）
            filtered_solutions = self._filter_solutions_by_time(solution_list)

            # 按运行ID从小到大排序并重新编号
            processed_solutions = self._process_solutions(filtered_solutions)

            # 保存到文件
            self._save_solution_list_to_file(processed_solutions)

            log.info(f"成功获取 {len(processed_solutions)} 条提交记录!")
            return processed_solutions

        except Exception as e:
            log.error(f"获取提交记录时出现错误: {e}")
            return None

    def _parse_solution_list(self, soup):
        """解析提交记录列表"""
        solution_list = []

        # 查找提交记录表格
        table = soup.find('table', class_='table')
        if not table:
            log.error("未找到提交记录表格")
            return solution_list

        # 查找表格主体
        tbody = table.find('tbody')
        if not tbody:
            log.error("未找到表格主体")
            return solution_list

        # 遍历每一行
        for row in tbody.find_all('tr'):
            solution_info = self._parse_solution_row(row)
            if solution_info:
                solution_list.append(solution_info)

        return solution_list

    def _parse_solution_row(self, row):
        """解析单个提交记录的行信息"""
        try:
            cells = row.find_all('td')
            if len(cells) < 8:  # 确保有足够的列
                return None

            # 提取结果信息 (第四个td) - 先检查是否为编译错误
            result_cell = cells[3]
            result_info = self._parse_result_info(result_cell)

            # 如果是编译错误，跳过此条记录
            if result_info['code'] == 11:  # 11 表示编译错误
                log.debug(f"跳过编译错误的提交记录")
                return None

            # 提取运行ID (第一个td)
            run_id_cell = cells[0]
            run_id_link = run_id_cell.find('a')
            run_id = int(run_id_link.text.strip()) if run_id_link else 0

            # 提取问题信息 (第二个td)
            problem_cell = cells[1]
            problem_link = problem_cell.find('a')
            problem_text = problem_link.text.strip() if problem_link else ""
            problem_number = self._parse_problem_number(problem_text)

            # 提取用户名 (第三个td)
            user_cell = cells[2]
            user_link = user_cell.find('a')
            username = user_link.text.strip() if user_link else ""

            # 提取时间信息 (第五个td) - 执行时间
            time_cell = cells[4]
            execution_time = time_cell.text.strip()

            # 提取语言信息 (第七个td)
            language_cell = cells[6]
            language_link = language_cell.find('a')
            language_text = language_link.text.strip() if language_link else ""
            language = self._parse_language(language_text)

            # 提取提交时间 (第八个td)
            submit_time_cell = cells[7]
            submit_time = submit_time_cell.text.strip()
            timestamp = self._datetime_to_timestamp(submit_time)
            time_from_start = self._calculate_time_from_start(submit_time)

            # 构建提交记录信息字典
            solution_info = {
                'run_id': run_id,
                'problem': problem_number,
                'username': username,
                'language': language,
                'execution_time': execution_time,
                'time': round(time_from_start, 6),  # 从比赛开始到提交的秒数
                'timestamp': timestamp,  # 提交时间的时间戳
                'submit_time': submit_time,  # 原始提交时间字符串
                'result': result_info['result'],  # AC 或 WA
                'penalty': result_info['penalty'],  # True 或 False
                'result_detail': result_info['detail'],  # 原始结果详情
                'result_code': result_info['code']  # 结果代码
            }

            return solution_info

        except Exception as e:
            log.error(f"解析提交记录行时出错: {e}")
            return None

    def _parse_problem_number(self, problem_text):
        """解析题目编号"""
        # 格式如: "A (1)", "F (6)" 等
        match = re.search(r'\((\d+)\)', problem_text)
        if match:
            return int(match.group(1))
        else:
            # 如果没有括号数字，尝试提取其他格式的数字
            numbers = re.findall(r'\d+', problem_text)
            return int(numbers[0]) if numbers else 0

    def _parse_language(self, language_text):
        """识别提交语言，只识别C/C++/Java/Python"""
        language_text = language_text.lower()

        if 'c++' in language_text:
            return 'C++'
        elif 'c17' in language_text or 'c ' in language_text:
            return 'C'
        elif 'java' in language_text:
            return 'Java'
        elif 'python' in language_text:
            return 'Python'
        elif 'golang' in language_text:
            return 'Go'
        else:
            return language_text

    def _parse_result_info(self, result_cell):
        """解析结果信息"""
        # 提取隐藏的结果代码
        hidden_spans = result_cell.find_all('span', {'hidden': True})
        result_code = int(hidden_spans[1].text) if len(hidden_spans) > 1 else -1

        # 提取显示的结果文本
        result_span = result_cell.find('span', {'class': 'result_td'})
        result_text = result_span.text.strip() if result_span else ""

        # 根据结果代码判断结果和惩罚
        # 从HTML中可以看到：4表示正确，其他都是错误
        if result_code == 4:
            result = 'AC'
            penalty = False
        else:
            result = 'WA'
            penalty = True

        return {
            'result': result,
            'penalty': penalty,
            'detail': result_text,
            'code': result_code
        }

    def _datetime_to_timestamp(self, datetime_str):
        """将日期时间字符串转换为时间戳"""
        try:
            dt_obj = datetime.strptime(datetime_str, '%Y-%m-%d %H:%M:%S')
            return dt_obj.timestamp()
        except ValueError as e:
            log.error(f"日期格式错误: {e}")
            return None

    def _calculate_time_from_start(self, submit_time_str):
        """计算从比赛开始到提交所经过的秒数"""
        if not self.contest_start_time:
            log.warning("未设置比赛开始时间，无法计算时间差")
            return 0.0

        try:
            start_timestamp = self._datetime_to_timestamp(self.contest_start_time)
            submit_timestamp = self._datetime_to_timestamp(submit_time_str)

            if start_timestamp and submit_timestamp:
                return submit_timestamp - start_timestamp
            else:
                return 0.0
        except Exception as e:
            log.error(f"计算时间差时出错: {e}")
            return 0.0

    def _filter_solutions_by_time(self, solution_list):
        """根据比赛时间过滤提交记录"""
        if not self.contest_start_time or not self.contest_end_time:
            log.warning("未设置比赛开始时间或结束时间，返回所有提交记录")
            return solution_list

        try:
            start_timestamp = self._datetime_to_timestamp(self.contest_start_time)
            end_timestamp = self._datetime_to_timestamp(self.contest_end_time)

            if not start_timestamp or not end_timestamp:
                log.error("无法解析比赛开始时间或结束时间，返回所有提交记录")
                return solution_list

            filtered_solutions = []
            skipped_count = 0

            for solution in solution_list:
                if solution['timestamp'] and start_timestamp <= solution['timestamp'] <= end_timestamp:
                    filtered_solutions.append(solution)
                else:
                    skipped_count += 1

            log.info(f"时间过滤: 保留 {len(filtered_solutions)} 条记录，跳过 {skipped_count} 条记录")
            return filtered_solutions

        except Exception as e:
            log.error(f"过滤提交记录时出错: {e}")
            return solution_list

    def _process_solutions(self, solution_list):
        """处理提交记录：排序并重新编号"""
        # 按运行ID从小到大排序
        sorted_solutions = sorted(solution_list, key=lambda x: x['run_id'])

        # 重新编号（从1开始）
        for index, solution in enumerate(sorted_solutions, 1):
            solution['id'] = index

        return sorted_solutions

    def _save_solution_list_to_file(self, solution_list):
        """保存提交记录列表信息到JSON文件"""
        # 创建目录
        dir_path = f"./solutions/{self.contestId}"
        os.makedirs(dir_path, exist_ok=True)

        # 准备数据
        contest_data = {
            'contest_id': self.contestId,
            'base_url': self.baseUrl,
            'solution_count': len(solution_list),
            'solutions': solution_list,
            'retrieved_time': time.strftime('%Y-%m-%d %H:%M:%S'),
            'contest_start_time': self.contest_start_time,
            'contest_end_time': self.contest_end_time
        }

        # 保存到文件
        file_path = f"{dir_path}/solution_list.json"
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(contest_data, f, ensure_ascii=False, indent=2)

        log.info(f"提交记录已保存到: {file_path}")

    def get_solution_list_data(self):
        """获取提交记录列表数据的接口方法"""
        # 检查是否已有缓存文件
        file_path = f"./solutions/{self.contestId}/solution_list.json"

        if os.path.exists(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                # 检查缓存文件中的时间范围是否与当前设置一致
                cache_start = data.get('contest_start_time')
                cache_end = data.get('contest_end_time')

                if cache_start == self.contest_start_time and cache_end == self.contest_end_time:
                    log.info("从缓存文件加载提交记录数据")
                    return data['solutions']  # 只返回solutions列表
                else:
                    log.info("缓存文件的时间范围与当前设置不一致，重新获取数据")
            except Exception as e:
                log.error(f"读取缓存文件失败: {e}")

        # 如果没有缓存文件或读取失败，重新获取数据
        log.info("重新获取提交记录数据")
        return self.get_solution_list()

    def print_solution_list(self):
        """打印提交记录列表（用于调试）"""
        solutions = self.get_solution_list_data()
        if solutions:
            print(f"比赛ID: {self.contestId}")
            print(f"比赛时间: {self.contest_start_time} 至 {self.contest_end_time}")
            print(f"提交记录数量: {len(solutions)}")
            print("-" * 100)
            for solution in solutions[:5]:  # 只打印前5条
                print(f"ID: {solution['id']}, "
                      f"运行ID: {solution['run_id']}, "
                      f"题目: {solution['problem']}, "
                      f"用户: {solution['username']}, "
                      f"语言: {solution['language']}, "
                      f"结果: {solution['result']}, "
                      f"惩罚: {solution['penalty']}, "
                      f"提交时间: {solution['submit_time']}, "
                      f"时间: {solution['time']}s")
            if len(solutions) > 5:
                print(f"... 还有 {len(solutions) - 5} 条记录")
        else:
            print("无法获取提交记录数据")