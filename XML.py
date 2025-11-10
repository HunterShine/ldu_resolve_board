# import xml.etree.ElementTree as ET
# from xml.dom import minidom
# import json
# from datetime import datetime
# import log_config
# from config import CONTEST_CONFIG, AWARD_CONFIG
#
# log = log_config.get_logger(__name__)
#
#
# class ContestXMLGenerator:
#     def __init__(self, problem_list, user_data, solutions, info, finalized):
#         self.problem_list = problem_list
#         self.user_data = user_data
#         self.solutions = solutions
#         self.info = info
#         self.finalized = finalized
#
#         # 创建映射表
#         self.language_map = self._create_language_map()
#         self.judgement_map = self._create_judgement_map()
#         self.region_map = self._create_region_map()
#
#     def generate_xml(self, output_file='contest.xml'):
#         """生成完整的contest.xml文件"""
#         try:
#             # 创建根元素
#             contest = ET.Element('contest')
#
#             # 添加各个部分
#             self._add_info_section(contest)
#             self._add_regions_section(contest)
#             self._add_judgements_section(contest)
#             self._add_languages_section(contest)
#             self._add_problems_section(contest)
#             self._add_teams_section(contest)
#             self._add_runs_section(contest)
#             self._add_finalized_section(contest)
#
#             # 美化XML并保存
#             xml_str = self._prettify_xml(contest)
#
#             with open(output_file, 'w', encoding='utf-8') as f:
#                 f.write(xml_str)
#
#             log.info(f"XML文件已生成: {output_file}")
#             return True
#
#         except Exception as e:
#             log.error(f"生成XML文件时出错: {e}")
#             return False
#
#     def _add_info_section(self, contest):
#         """添加info部分"""
#         info_elem = ET.SubElement(contest, 'info')
#
#         # 根据示例添加info字段
#         length_elem = ET.SubElement(info_elem, 'length')
#         length_elem.text = self.info.get('length', '4:00:00')
#
#         penalty_elem = ET.SubElement(info_elem, 'penalty')
#         penalty_elem.text = str(self.info.get('penalty', 20))
#
#         started_elem = ET.SubElement(info_elem, 'started')
#         started_elem.text = 'False'
#
#         starttime_elem = ET.SubElement(info_elem, 'starttime')
#         starttime_elem.text = str(self.info.get('starttime', ''))
#
#         title_elem = ET.SubElement(info_elem, 'title')
#         title_elem.text = CONTEST_CONFIG.get('title', CONTEST_CONFIG['name'])
#
#         short_title_elem = ET.SubElement(info_elem, 'short-title')
#         short_title_elem.text = CONTEST_CONFIG.get('short_title', CONTEST_CONFIG['name'])
#
#         freeze_elem = ET.SubElement(info_elem, 'scoreboard-freeze-length')
#         freeze_elem.text = self.info.get('scoreboard-freeze-length', '0:30:00')
#
#         contest_id_elem = ET.SubElement(info_elem, 'contest-id')
#         contest_id_elem.text = CONTEST_CONFIG.get('contest_id', 'default')
#
#     def _add_regions_section(self, contest):
#         """添加region部分"""
#         # 收集所有不同的学校
#         schools = set()
#         for user in self.user_data:
#             if 'school' in user and user['school']:
#                 schools.add(user['school'])
#
#         # 为每个学校创建region元素
#         for i, school in enumerate(schools, 1):
#             region_elem = ET.SubElement(contest, 'region')
#
#             external_id_elem = ET.SubElement(region_elem, 'external-id')
#             external_id_elem.text = str(i)
#
#             name_elem = ET.SubElement(region_elem, 'name')
#             name_elem.text = school
#
#             # 保存映射
#             self.region_map[school] = i
#
#     def _add_judgements_section(self, contest):
#         """添加judgement部分"""
#         # 定义判题结果
#         judgements = [
#             {'id': 1, 'acronym': 'AC', 'name': 'Yes', 'solved': 'true', 'penalty': 'false'},
#             {'id': 2, 'acronym': 'WA', 'name': 'No - Wrong Answer', 'solved': 'false', 'penalty': 'true'},
#             # {'id': 3, 'acronym': 'TLE', 'name': 'No - Time Limit Exceeded', 'solved': 'false', 'penalty': 'true'},
#             # {'id': 4, 'acronym': 'MLE', 'name': 'No - Memory Limit Exceeded', 'solved': 'false', 'penalty': 'true'},
#             # {'id': 5, 'acronym': 'RE', 'name': 'No - Runtime Error', 'solved': 'false', 'penalty': 'true'},
#             # {'id': 6, 'acronym': 'CE', 'name': 'No - Compilation Error', 'solved': 'false', 'penalty': 'false'}
#         ]
#
#         for judgement in judgements:
#             judgement_elem = ET.SubElement(contest, 'judgement')
#
#             id_elem = ET.SubElement(judgement_elem, 'id')
#             id_elem.text = str(judgement['id'])
#
#             acronym_elem = ET.SubElement(judgement_elem, 'acronym')
#             acronym_elem.text = judgement['acronym']
#
#             name_elem = ET.SubElement(judgement_elem, 'name')
#             name_elem.text = judgement['name']
#
#             solved_elem = ET.SubElement(judgement_elem, 'solved')
#             solved_elem.text = judgement['solved']
#
#             penalty_elem = ET.SubElement(judgement_elem, 'penalty')
#             penalty_elem.text = judgement['penalty']
#
#             # 保存映射
#             self.judgement_map[judgement['acronym']] = judgement['id']
#
#     def _add_languages_section(self, contest):
#         """添加language部分"""
#         # 从提交记录中收集所有使用的语言
#         languages_used = set()
#         for solution in self.solutions:
#             if 'language' in solution:
#                 # 将语言转换为小写
#                 lang = solution['language'].lower()
#                 if lang == 'c++':
#                     lang = 'c++'
#                 languages_used.add(lang)
#
#         # 定义语言映射
#         language_definitions = [
#             {'id': 1, 'name': 'c'},
#             {'id': 2, 'name': 'c++'},
#             {'id': 3, 'name': 'java'},
#             {'id': 4, 'name': 'python'},
#             # {'id': 5, 'name': 'go'}
#         ]
#
#         # 只添加实际使用过的语言
#         for lang_def in language_definitions:
#             if lang_def['name'] in languages_used:
#                 language_elem = ET.SubElement(contest, 'language')
#
#                 id_elem = ET.SubElement(language_elem, 'id')
#                 id_elem.text = str(lang_def['id'])
#
#                 name_elem = ET.SubElement(language_elem, 'name')
#                 name_elem.text = lang_def['name']
#
#                 # 保存映射
#                 self.language_map[lang_def['name']] = lang_def['id']
#
#     def _add_problems_section(self, contest):
#         """添加problem部分"""
#         for problem in self.problem_list:
#             problem_elem = ET.SubElement(contest, 'problem')
#
#             id_elem = ET.SubElement(problem_elem, 'id')
#             id_elem.text = str(problem['number_index'])
#
#             letter_elem = ET.SubElement(problem_elem, 'letter')
#             letter_elem.text = problem['letter_index']
#
#             name_elem = ET.SubElement(problem_elem, 'name')
#             name_elem.text = problem['title']
#
#     def _add_teams_section(self, contest):
#         """添加team部分"""
#         for user in self.user_data:
#             team_elem = ET.SubElement(contest, 'team')
#
#             id_elem = ET.SubElement(team_elem, 'id')
#             id_elem.text = str(user['index'])
#
#             external_id_elem = ET.SubElement(team_elem, 'external-id')
#             external_id_elem.text = str(user['index'])
#
#             # 添加区域信息
#             if 'school' in user and user['school']:
#                 region_elem = ET.SubElement(team_elem, 'region')
#                 region_elem.text = user['school']
#
#             name_elem = ET.SubElement(team_elem, 'name')
#             name_elem.text = user['name']
#
#             university_elem = ET.SubElement(team_elem, 'university')
#             university_elem.text = user['school']  # 使用姓名作为大学
#
#     def _add_runs_section(self, contest):
#         """添加run部分"""
#         for solution in self.solutions:
#             team_id = self._find_team_id_by_username(solution['username'])
#             if not team_id:
#                 continue
#             run_elem = ET.SubElement(contest, 'run')
#
#             id_elem = ET.SubElement(run_elem, 'id')
#             id_elem.text = str(solution['id'])
#
#             judged_elem = ET.SubElement(run_elem, 'judged')
#             judged_elem.text = 'True'
#
#             # 语言映射
#             language_key = solution['language'].lower()
#             if language_key == 'c++':
#                 language_key = 'c++'
#
#             if language_key in self.language_map:
#                 language_elem = ET.SubElement(run_elem, 'language')
#                 language_elem.text = language_key
#
#             problem_elem = ET.SubElement(run_elem, 'problem')
#             problem_elem.text = str(solution['problem'])
#
#             status_elem = ET.SubElement(run_elem, 'status')
#             status_elem.text = 'done'
#
#             # 团队映射
#             # team_id = self._find_team_id_by_username(solution['username'])
#             if team_id:
#                 team_elem = ET.SubElement(run_elem, 'team')
#                 team_elem.text = str(team_id)
#
#             time_elem = ET.SubElement(run_elem, 'time')
#             time_elem.text = str(solution['time'])
#
#             timestamp_elem = ET.SubElement(run_elem, 'timestamp')
#             timestamp_elem.text = str(solution['timestamp'])
#
#             solved_elem = ET.SubElement(run_elem, 'solved')
#             solved_elem.text = 'true' if solution['result'] == 'AC' else 'false'
#
#             penalty_elem = ET.SubElement(run_elem, 'penalty')
#             penalty_elem.text = str(solution['penalty']).lower()
#
#             result_elem = ET.SubElement(run_elem, 'result')
#             result_elem.text = solution['result']
#
#     def _add_finalized_section(self, contest):
#         """添加finalized部分"""
#         finalized_elem = ET.SubElement(contest, 'finalized')
#
#         last_gold_elem = ET.SubElement(finalized_elem, 'last_gold')
#         last_gold_elem.text = str(self.finalized.get('last_gold', 1))
#
#         last_silver_elem = ET.SubElement(finalized_elem, 'last_silver')
#         last_silver_elem.text = str(self.finalized.get('last_silver', 4))
#
#         last_bronze_elem = ET.SubElement(finalized_elem, 'last_bronze')
#         last_bronze_elem.text = str(self.finalized.get('last_bronze', 9))
#
#         time_elem = ET.SubElement(finalized_elem, 'time')
#         time_elem.text = str(self.finalized.get('time', 0))
#
#         timestamp_elem = ET.SubElement(finalized_elem, 'timestamp')
#         timestamp_elem.text = str(self.finalized.get('timestamp', ''))
#
#     def _find_team_id_by_username(self, username):
#         """根据用户名找到对应的团队ID"""
#         for user in self.user_data:
#             if user['username'] == username:
#                 return user['index']
#         return None
#
#     def _create_language_map(self):
#         """创建语言映射表"""
#         return {}
#
#     def _create_judgement_map(self):
#         """创建判题结果映射表"""
#         return {}
#
#     def _create_region_map(self):
#         """创建区域映射表"""
#         return {}
#
#     def _prettify_xml(self, elem):
#         """美化XML输出"""
#         rough_string = ET.tostring(elem, encoding='utf-8')
#         reparsed = minidom.parseString(rough_string)
#         return reparsed.toprettyxml(indent="  ", encoding='utf-8').decode('utf-8')
#
#
# def generate_contest_xml(problem_list, user_data, solutions, info, finalized, output_file='contest.xml'):
#     """
#     生成比赛XML文件的主函数
#
#     参数:
#         problem_list: 题目列表
#         user_data: 用户数据
#         solutions: 提交记录
#         info: 基础信息
#         finalized: 奖项信息
#         output_file: 输出文件路径
#
#     返回:
#         bool: 是否成功生成
#     """
#     try:
#         generator = ContestXMLGenerator(problem_list, user_data, solutions, info, finalized)
#         success = generator.generate_xml(output_file)
#
#         if success:
#             log.info(f"成功生成比赛XML文件: {output_file}")
#         else:
#             log.error("生成比赛XML文件失败")
#
#         return success
#
#     except Exception as e:
#         log.error(f"生成比赛XML文件时出现错误: {e}")
#         return False


import xml.etree.ElementTree as ET
from xml.dom import minidom
import json
from datetime import datetime
import log_config
from config import CONTEST_CONFIG, AWARD_CONFIG

log = log_config.get_logger(__name__)


class ContestXMLGenerator:
    def __init__(self, problem_list, user_data, solutions, info, finalized):
        self.problem_list = problem_list
        self.user_data = user_data
        self.solutions = solutions
        self.info = info
        self.finalized = finalized

        # 创建映射表
        self.language_map = self._create_language_map()
        self.judgement_map = self._create_judgement_map()
        self.region_map = self._create_region_map()
        self.problem_letter_to_id = {p['letter_index']: p['number_index'] for p in problem_list}

    def generate_xml(self, output_file='contest.xml'):
        """生成完整的contest.xml文件"""
        try:
            # 创建根元素
            contest = ET.Element('contest')

            # 添加各个部分
            self._add_info_section(contest)
            self._add_regions_section(contest)
            self._add_judgements_section(contest)
            self._add_languages_section(contest)
            self._add_problems_section(contest)
            self._add_teams_section(contest)
            self._add_runs_section(contest)
            self._add_finalized_section(contest)

            # 美化XML并保存
            xml_str = self._prettify_xml(contest)

            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(xml_str)

            log.info(f"XML文件已生成: {output_file}")
            return True

        except Exception as e:
            log.error(f"生成XML文件时出错: {e}")
            return False

    def _add_info_section(self, contest):
        """添加info部分"""
        info_elem = ET.SubElement(contest, 'info')

        # 根据示例添加info字段
        length_elem = ET.SubElement(info_elem, 'length')
        length_elem.text = self.info.get('length', '4:00:00')

        penalty_elem = ET.SubElement(info_elem, 'penalty')
        penalty_elem.text = str(self.info.get('penalty', 20))

        started_elem = ET.SubElement(info_elem, 'started')
        started_elem.text = 'False'

        starttime_elem = ET.SubElement(info_elem, 'starttime')
        starttime_elem.text = str(self.info.get('starttime', ''))

        title_elem = ET.SubElement(info_elem, 'title')
        title_elem.text = CONTEST_CONFIG.get('title', CONTEST_CONFIG['name'])

        short_title_elem = ET.SubElement(info_elem, 'short-title')
        short_title_elem.text = CONTEST_CONFIG.get('short_title', CONTEST_CONFIG['name'])

        freeze_elem = ET.SubElement(info_elem, 'scoreboard-freeze-length')
        freeze_elem.text = self.info.get('scoreboard-freeze-length', '0:30:00')

        contest_id_elem = ET.SubElement(info_elem, 'contest-id')
        contest_id_elem.text = CONTEST_CONFIG.get('contest_id', 'default')

    def _add_regions_section(self, contest):
        """添加region部分"""
        # 收集所有不同的学校
        schools = set()
        for user in self.user_data:
            if 'school' in user and user['school']:
                schools.add(user['school'])

        # 为每个学校创建region元素
        for i, school in enumerate(schools, 1):
            region_elem = ET.SubElement(contest, 'region')

            external_id_elem = ET.SubElement(region_elem, 'external-id')
            external_id_elem.text = str(i)

            name_elem = ET.SubElement(region_elem, 'name')
            name_elem.text = school

            # 保存映射
            self.region_map[school] = i

    def _add_judgements_section(self, contest):
        """添加judgement部分"""
        # 定义判题结果
        judgements = [
            {'id': 1, 'acronym': 'AC', 'name': 'Yes', 'solved': 'true', 'penalty': 'false'},
            {'id': 2, 'acronym': 'WA', 'name': 'No - Wrong Answer', 'solved': 'false', 'penalty': 'true'},
            # {'id': 3, 'acronym': 'TLE', 'name': 'No - Time Limit Exceeded', 'solved': 'false', 'penalty': 'true'},
            # {'id': 4, 'acronym': 'MLE', 'name': 'No - Memory Limit Exceeded', 'solved': 'false', 'penalty': 'true'},
            # {'id': 5, 'acronym': 'RE', 'name': 'No - Runtime Error', 'solved': 'false', 'penalty': 'true'},
            # {'id': 6, 'acronym': 'CE', 'name': 'No - Compilation Error', 'solved': 'false', 'penalty': 'false'}
        ]

        for judgement in judgements:
            judgement_elem = ET.SubElement(contest, 'judgement')

            id_elem = ET.SubElement(judgement_elem, 'id')
            id_elem.text = str(judgement['id'])

            acronym_elem = ET.SubElement(judgement_elem, 'acronym')
            acronym_elem.text = judgement['acronym']

            name_elem = ET.SubElement(judgement_elem, 'name')
            name_elem.text = judgement['name']

            solved_elem = ET.SubElement(judgement_elem, 'solved')
            solved_elem.text = judgement['solved']

            penalty_elem = ET.SubElement(judgement_elem, 'penalty')
            penalty_elem.text = judgement['penalty']

            # 保存映射
            self.judgement_map[judgement['acronym']] = judgement['id']

    def _add_languages_section(self, contest):
        """添加language部分"""
        # 从提交记录中收集所有使用的语言
        languages_used = set()
        for solution in self.solutions:
            if 'language' in solution:
                # 将语言转换为小写
                lang = solution['language'].lower()
                if lang == 'c++':
                    lang = 'c++'
                languages_used.add(lang)

        # 定义语言映射
        language_definitions = [
            {'id': 1, 'name': 'c'},
            {'id': 2, 'name': 'c++'},
            {'id': 3, 'name': 'java'},
            {'id': 4, 'name': 'python'},
            # {'id': 5, 'name': 'go'}
        ]

        # 只添加实际使用过的语言
        for lang_def in language_definitions:
            if lang_def['name'] in languages_used:
                language_elem = ET.SubElement(contest, 'language')

                id_elem = ET.SubElement(language_elem, 'id')
                id_elem.text = str(lang_def['id'])

                name_elem = ET.SubElement(language_elem, 'name')
                name_elem.text = lang_def['name']

                # 保存映射
                self.language_map[lang_def['name']] = lang_def['id']

    def _add_problems_section(self, contest):
        """添加problem部分"""
        for problem in self.problem_list:
            problem_elem = ET.SubElement(contest, 'problem')

            id_elem = ET.SubElement(problem_elem, 'id')
            id_elem.text = str(problem['number_index'])

            letter_elem = ET.SubElement(problem_elem, 'letter')
            letter_elem.text = problem['letter_index']

            name_elem = ET.SubElement(problem_elem, 'name')
            name_elem.text = problem['title']

    def _add_teams_section(self, contest):
        """添加team部分"""
        for user in self.user_data:
            team_elem = ET.SubElement(contest, 'team')

            id_elem = ET.SubElement(team_elem, 'id')
            id_elem.text = str(user['index'])

            external_id_elem = ET.SubElement(team_elem, 'external-id')
            external_id_elem.text = str(user['index'])

            # 添加区域信息
            if 'school' in user and user['school']:
                region_elem = ET.SubElement(team_elem, 'region')
                region_elem.text = user['school']

            name_elem = ET.SubElement(team_elem, 'name')
            name_elem.text = user['name']

            university_elem = ET.SubElement(team_elem, 'university')
            university_elem.text = user['school']  # 使用姓名作为大学

    def _add_runs_section(self, contest):
        """添加run部分"""
        log.info(f"开始处理提交记录，共 {len(self.solutions)} 条")

        # 按时间排序提交记录
        sorted_solutions = sorted(self.solutions, key=lambda x: x['timestamp'])
        log.info(f"排序后提交记录数量: {len(sorted_solutions)}")

        # 记录每个用户每个题目的通过状态
        user_problem_accepted = {}

        # 用于生成连续 run id 的计数器
        run_id_counter = 1
        processed_count = 0
        skipped_count = 0

        for solution in sorted_solutions:
            team_id = self._find_team_id_by_username(solution['username'])
            if team_id is None:
                log.info(f"跳过提交 {solution['id']}: 未找到用户 {solution['username']} 对应的团队ID")
                skipped_count += 1
                continue

            # 将数字题目编号转换为字母（1->A, 2->B, 3->C, ...）
            problem_number = solution['problem']
            problem_letter = chr(ord('A') + problem_number - 1)  # 1->A, 2->B, 3->C, 等等

            # 获取题目ID
            problem_id = None

            # 查找对应的题目ID
            for problem in self.problem_list:
                if problem['letter_index'] == problem_letter:
                    problem_id = problem['number_index']
                    break

            log.info(f"题目编号: {problem_number}, 题目字母: {problem_letter}, 题目ID: {problem_id}")
            if problem_id is None:
                log.warning(f"警告: 无法找到题目 '{problem_letter}' 对应的ID")
                skipped_count += 1
                continue

            # 初始化用户记录
            if solution['username'] not in user_problem_accepted:
                user_problem_accepted[solution['username']] = {}

            # 如果这个题目已经通过了，跳过后续所有提交
            if user_problem_accepted[solution['username']].get(problem_letter):
                log.info(f"跳过用户 {solution['username']} 题目 {problem_letter} 的提交，因为已经通过")
                skipped_count += 1
                continue

            # 处理当前提交
            run_elem = ET.SubElement(contest, 'run')

            # 使用连续的 run id
            id_elem = ET.SubElement(run_elem, 'id')
            id_elem.text = str(run_id_counter)
            run_id_counter += 1  # 递增计数器

            judged_elem = ET.SubElement(run_elem, 'judged')
            judged_elem.text = 'True'

            # 语言映射
            language_key = solution['language'].lower()
            if language_key == 'c++':
                language_key = 'c++'

            if language_key in self.language_map:
                language_elem = ET.SubElement(run_elem, 'language')
                language_elem.text = language_key

            problem_elem = ET.SubElement(run_elem, 'problem')
            problem_elem.text = str(problem_id)

            status_elem = ET.SubElement(run_elem, 'status')
            status_elem.text = 'done'

            team_elem = ET.SubElement(run_elem, 'team')
            team_elem.text = str(team_id)

            time_elem = ET.SubElement(run_elem, 'time')
            time_elem.text = str(solution['time'])

            timestamp_elem = ET.SubElement(run_elem, 'timestamp')
            timestamp_elem.text = str(solution['timestamp'])

            solved_elem = ET.SubElement(run_elem, 'solved')
            solved_elem.text = 'true' if solution['result'] == 'AC' else 'false'

            penalty_elem = ET.SubElement(run_elem, 'penalty')
            penalty_elem.text = str(solution['penalty']).lower()

            result_elem = ET.SubElement(run_elem, 'result')
            result_elem.text = solution['result']

            # 如果当前提交是AC，标记该用户该题目已通过
            if solution['result'] == 'AC':
                user_problem_accepted[solution['username']][problem_letter] = True
                log.info(f"用户 {solution['username']} 题目 {problem_letter} 已通过")

            processed_count += 1

        log.info(f"处理完成: 共处理 {processed_count} 条提交，跳过 {skipped_count} 条提交")
        log.info(f"生成的 run 元素数量: {run_id_counter - 1}")

    def _add_finalized_section(self, contest):
        """添加finalized部分"""
        finalized_elem = ET.SubElement(contest, 'finalized')

        last_gold_elem = ET.SubElement(finalized_elem, 'last_gold')
        last_gold_elem.text = str(self.finalized.get('last_gold', 1))

        last_silver_elem = ET.SubElement(finalized_elem, 'last_silver')
        last_silver_elem.text = str(self.finalized.get('last_silver', 4))

        last_bronze_elem = ET.SubElement(finalized_elem, 'last_bronze')
        last_bronze_elem.text = str(self.finalized.get('last_bronze', 9))

        time_elem = ET.SubElement(finalized_elem, 'time')
        time_elem.text = str(self.finalized.get('time', 0))

        timestamp_elem = ET.SubElement(finalized_elem, 'timestamp')
        timestamp_elem.text = str(self.finalized.get('timestamp', ''))

    def _find_team_id_by_username(self, username):
        """根据用户名找到对应的团队ID"""
        for user in self.user_data:
            if user['username'] == username:
                return user['index']
        return None

    def _create_language_map(self):
        """创建语言映射表"""
        return {}

    def _create_judgement_map(self):
        """创建判题结果映射表"""
        return {}

    def _create_region_map(self):
        """创建区域映射表"""
        return {}

    def _prettify_xml(self, elem):
        """美化XML输出"""
        rough_string = ET.tostring(elem, encoding='utf-8')
        reparsed = minidom.parseString(rough_string)
        return reparsed.toprettyxml(indent="  ", encoding='utf-8').decode('utf-8')


def generate_contest_xml(problem_list, user_data, solutions, info, finalized, output_file='contest.xml'):
    """
    生成比赛XML文件的主函数

    参数:
        problem_list: 题目列表
        user_data: 用户数据
        solutions: 提交记录
        info: 基础信息
        finalized: 奖项信息
        output_file: 输出文件路径

    返回:
        bool: 是否成功生成
    """
    try:
        generator = ContestXMLGenerator(problem_list, user_data, solutions, info, finalized)
        success = generator.generate_xml(output_file)

        if success:
            log.info(f"成功生成比赛XML文件: {output_file}")
        else:
            log.error("生成比赛XML文件失败")

        return success

    except Exception as e:
        log.error(f"生成比赛XML文件时出现错误: {e}")
        return False