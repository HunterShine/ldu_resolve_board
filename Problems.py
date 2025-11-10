import json
import os
import random
import time
import re

import log_config
from config import CONTEST_CONFIG
import bs4

log = log_config.get_logger(__name__)


class Problems:
    def __init__(self, login_session):
        self.session = login_session.get_session()
        self.baseUrl = CONTEST_CONFIG['contest_baseUrl']
        self.contestId = CONTEST_CONFIG['contest_id']
        # self.problemNum = CONTEST_CONFIG['problemNum']

    def get_problem_list(self):
        """获取比赛题目列表信息"""
        try:
            log.info(f'开始获取比赛题目列表: {self.baseUrl}/{self.contestId}')
            # 构建比赛URL
            contest_url = f"{self.baseUrl}/{self.contestId}"

            # 发送请求
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36 Edg/141.0.0.0',
                'Referer': f'{self.baseUrl}'
            }

            response = self.session.get(contest_url, headers=headers)
            log.info(f'发送GET请求，获得响应: {response.status_code}')

            if response.status_code != 200:
                log.error(f"获取比赛题目列表失败，状态码: {response.status_code}")
                return None

            # 解析HTML
            soup = bs4.BeautifulSoup(response.text, 'html.parser')

            # 提取题目列表信息
            problem_list = self._parse_problem_list(soup)

            # 按数字序号排序
            problem_list.sort(key=lambda x: x['number_index'])

            # 保存到文件
            self._save_problem_list_to_file(problem_list)

            log.info(f"成功获取 {len(problem_list)} 个题目的列表信息!")
            return problem_list

        except Exception as e:
            log.error(f"获取比赛题目列表时出现错误: {e}")
            return None

    def _parse_problem_list(self, soup):
        """解析题目列表信息"""
        problem_list = []

        # 查找题目表格
        table = soup.find('table', class_='table')
        if not table:
            log.error("未找到题目表格")
            return problem_list

        # 查找表格主体
        tbody = table.find('tbody')
        if not tbody:
            log.error("未找到表格主体")
            return problem_list

        # 遍历每一行
        for row in tbody.find_all('tr'):
            problem_info = self._parse_problem_row(row)
            if problem_info:
                problem_list.append(problem_info)

        return problem_list

    def _parse_problem_row(self, row):
        """解析单个题目的行信息"""
        try:
            cells = row.find_all('td')
            if len(cells) < 6:  # 确保有足够的列
                return None

            # 提取序号信息 (第二个td)
            index_cell = cells[1]
            index_text = index_cell.get_text(strip=True)

            # 解析字母序号和数字序号
            letter_index, number_index = self._parse_index(index_text)

            # 提取标题 (第三个td)
            title_cell = cells[2]
            title_link = title_cell.find('a')
            if title_link:
                problem_title = title_link.get_text(strip=True)
            else:
                problem_title = title_cell.get_text(strip=True)

            # 提取来源题目序号 (第六个td)
            source_cell = cells[6]
            source_problem_id = self._parse_source_problem_id(source_cell)

            # 构建题目信息字典
            problem_info = {
                'number_index': int(number_index),  # 数字序号，用于排序
                'letter_index': letter_index,  # 字母序号
                'title': problem_title,  # 题目标题
                'source_problem_id': source_problem_id  # 来源题目序号
            }

            return problem_info

        except Exception as e:
            log.error(f"解析题目行时出错: {e}")
            return None

    def _parse_index(self, index_text):
        """解析序号，提取字母和数字部分"""
        # 格式如: "A (1)", "B (2)" 等
        # 使用正则表达式匹配字母和数字
        match = re.match(r'([A-Z])\s*\((\d+)\)', index_text)
        if match:
            letter_index = match.group(1)  # 字母部分
            number_index = match.group(2)  # 数字部分
            return letter_index, number_index
        else:
            # 如果格式不匹配，尝试其他解析方式
            log.warning(f"无法解析序号格式: {index_text}")
            # 简单分割处理
            parts = index_text.split()
            if len(parts) >= 2:
                letter_index = parts[0]
                # 从括号中提取数字
                number_match = re.search(r'\((\d+)\)', index_text)
                number_index = number_match.group(1) if number_match else '0'
            else:
                letter_index = index_text
                number_index = '0'
            return letter_index, number_index

    def _parse_source_problem_id(self, source_cell):
        """解析来源题目序号"""
        try:
            # 查找所有链接
            links = source_cell.find_all('a')
            for link in links:
                link_text = link.get_text(strip=True)
                log.debug(f"找到链接文本: {link_text}")

                # 检查链接文本是否包含"问题"字样
                if '问题' in link_text:
                    # 提取数字部分
                    match = re.search(r'\d+', link_text)
                    if match:
                        log.debug(f"从链接文本中提取到数字: {match.group()}")
                        return match.group()

            # 如果没有找到包含"问题"的链接，尝试从href属性中提取
            for link in links:
                href = link.get('href', '')
                log.debug(f"找到链接href: {href}")

                # 从URL中提取问题ID
                # 例如: https://icpc.ldu.edu.cn/problems/5089
                match = re.search(r'/problems/(\d+)', href)
                if match:
                    log.debug(f"从href中提取到数字: {match.group(1)}")
                    return match.group(1)

            # 最后尝试从单元格文本中提取任何数字
            cell_text = source_cell.get_text(strip=True)
            log.debug(f"单元格文本: {cell_text}")

            # 查找类似"问题5089"的文本
            match = re.search(r'问题\s*(\d+)', cell_text)
            if match:
                log.debug(f"从单元格文本中提取到数字: {match.group(1)}")
                return match.group(1)

            # 最后尝试提取任何数字
            match = re.search(r'\b\d+\b', cell_text)
            if match:
                log.debug(f"从单元格文本中提取到数字（备用）: {match.group()}")
                return match.group()

            log.warning(f"无法从来源单元格中提取问题ID: {cell_text}")
            return None

        except Exception as e:
            log.error(f"解析来源题目序号时出错: {e}")
            return None

    def _save_problem_list_to_file(self, problem_list):
        """保存题目列表信息到JSON文件"""
        # 创建目录
        dir_path = f"./problems/{self.contestId}"
        os.makedirs(dir_path, exist_ok=True)

        # 准备数据
        contest_data = {
            'contest_id': self.contestId,
            'base_url': self.baseUrl,
            'problem_count': len(problem_list),
            'problems': problem_list,
            'retrieved_time': time.strftime('%Y-%m-%d %H:%M:%S')
        }

        # 保存到文件
        file_path = f"{dir_path}/problem_list.json"
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(contest_data, f, ensure_ascii=False, indent=2)

        log.info(f"题目列表已保存到: {file_path}")

    def get_problem_list_data(self):
        """获取题目列表数据的接口方法"""
        # 检查是否已有缓存文件
        file_path = f"./problems/{self.contestId}/problem_list.json"

        if os.path.exists(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                log.info("从缓存文件加载题目列表数据")
                return data
            except Exception as e:
                log.error(f"读取缓存文件失败: {e}")

        # 如果没有缓存文件或读取失败，重新获取数据
        log.info("重新获取题目列表数据")
        return self.get_problem_list()

    def print_problem_list(self):
        """打印题目列表（用于调试）"""
        data = self.get_problem_list_data()
        if data and 'problems' in data:
            print(f"比赛ID: {data['contest_id']}")
            print(f"题目数量: {data['problem_count']}")
            print("-" * 50)
            for problem in data['problems']:
                print(f"数字序号: {problem['number_index']}, "
                      f"字母序号: {problem['letter_index']}, "
                      f"标题: {problem['title']}, "
                      f"来源ID: {problem['source_problem_id']}")
        else:
            print("无法获取题目列表数据")