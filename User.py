import pandas as pd
import json
import sys


class User:
    def __init__(self, index, username, name, school, star):
        self.index = index
        self.username = username
        self.name = name
        self.school = school
        self.star = star

    def to_dict(self):
        """将User对象转换为字典"""
        return {
            'index': self.index,
            'username': str(self.username),
            'name': self.name,
            'school': self.school,
            'star': self.star
        }


class UserDataProcessor:
    def __init__(self, file_path):
        self.file_path = file_path
        self.users = []

    def check_dependencies(self):
        """检查必要的依赖是否已安装"""
        try:
            pd.read_excel(self.file_path, nrows=1)  # 尝试读取一行来测试
            return True
        except ImportError as e:
            print(f"缺少必要的依赖: {e}")
            print("请安装所需的依赖: pip install openpyxl")
            return False

    def process_data(self):
        """处理Excel数据并转换为User对象列表"""
        # 首先检查依赖
        if not self.check_dependencies():
            return False

        try:
            # 读取Excel文件
            df = pd.read_excel(self.file_path)

            # 确保列名正确
            expected_columns = ['index', 'username', 'name', 'school', 'star']
            if not all(col in df.columns for col in expected_columns):
                print(f"Excel文件缺少必要的列，需要的列: {expected_columns}")
                print(f"实际找到的列: {list(df.columns)}")
                return False

            # 转换为User对象列表
            self.users = []
            for _, row in df.iterrows():
                # 处理可能的NaN值
                user = User(
                    index=row['index'] if pd.notna(row['index']) else None,
                    username=row['username'] if pd.notna(row['username']) else "",
                    name=row['name'] if pd.notna(row['name']) else "",
                    school=row['school'] if pd.notna(row['school']) else "",
                    star=row['star'] if pd.notna(row['star']) else ""
                )
                self.users.append(user)

            print(f"成功处理 {len(self.users)} 条用户数据")
            return True

        except Exception as e:
            print(f"处理数据时出错: {e}")
            return False

    def get_json_data(self):
        """获取JSON格式的数据列表"""
        return [user.to_dict() for user in self.users]

    def save_to_json(self, output_file='users.json'):
        """将JSON数据保存到本地文件"""
        try:
            json_data = self.get_json_data()

            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(json_data, f, ensure_ascii=False, indent=2)

            print(f"数据已保存到 {output_file}")
            return True

        except Exception as e:
            print(f"保存文件时出错: {e}")
            return False


# 使用示例
def process_user_data(file_path):
    """处理用户数据并返回JSON列表"""
    processor = UserDataProcessor(file_path)

    if processor.process_data():
        # 保存到JSON文件
        processor.save_to_json()

        # 返回JSON数据
        return processor.get_json_data()
    else:
        print("数据处理失败")
        return []


# 直接调用获取数据
if __name__ == "__main__":
    # 替换为您的Excel文件路径
    excel_file = "user_info.xlsx"

    # 获取数据
    user_data = process_user_data(excel_file)

    # 打印前几条数据查看结果
    print(user_data)

    print(f"总共获取到 {len(user_data)} 条用户数据")