import requests
import log_config
from config import CONTEST_CONFIG

log = log_config.get_logger(__name__)
class Login:
    def __init__(self):
        self.session = requests.Session()
        self.logged_in = False

    def login_with_cookie_string(self, cookie_string):
        """使用cookie字符串进行登录"""
        try:
            # 解析cookie字符串
            cookies_dict = self._parse_cookie_string(cookie_string)

            # 设置cookies
            for key, value in cookies_dict.items():
                self.session.cookies.set(key, value)

            # 设置请求头，模拟浏览器
            self.session.headers.update({
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36 Edg/141.0.0.0',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
                'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6,fr-FR;q=0.5,fr;q=0.4',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1'
            })

            # 验证登录状态
            test_url = f"{CONTEST_CONFIG['contest_baseUrl']}"
            response = self.session.get(test_url)

            return True

            # if response.status_code == 200 and 'computer2106' in response.text:
            #     self.logged_in = True
            #     print("登录成功!")
            #     return True
            # else:
            #     print("登录失败! 请检查cookie是否有效")
            #     return False

        except Exception as e:
            log.error(f"登录过程中出现错误: {e}")
            return False

    def _parse_cookie_string(self, cookie_string):
        """解析cookie字符串为字典"""
        cookies_dict = {}
        # 按分号分割
        cookies = cookie_string.split(';')

        for cookie in cookies:
            cookie = cookie.strip()
            if '=' in cookie:
                key, value = cookie.split('=', 1)
                cookies_dict[key.strip()] = value.strip()

        return cookies_dict

    def get_session(self):
        """获取会话对象"""
        return self.session
