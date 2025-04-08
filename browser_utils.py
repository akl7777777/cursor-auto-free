from DrissionPage import ChromiumOptions, Chromium
import sys
import os
import logging
from dotenv import load_dotenv

load_dotenv()


class BrowserManager:
    def __init__(self):
        self.browser = None

    def init_browser(self, user_agent=None, user_data_dir=None):
        """
        初始化浏览器
        
        Args:
            user_agent: 用户代理字符串
            user_data_dir: 浏览器用户数据目录，用于隔离不同的浏览器实例
            
        Returns:
            Browser: 浏览器实例
        """
        # 使用 ChromiumOptions 来配置浏览器
        co = ChromiumOptions()
        
        # 设置无头模式
        co.headless(True)
        
        # 设置其他选项
        co.set_argument("--ignore-certificate-errors")
        co.set_argument("--no-sandbox")
        co.set_argument("--disable-gpu")
        co.set_argument("--window-size=1920,1080")
        
        # 设置用户代理
        if user_agent:
            co.set_user_agent(user_agent)
        
        # 设置用户数据目录 - 使用正确的参数名
        if user_data_dir:
            co.set_paths(user_data_path=user_data_dir)
        
        # 创建浏览器实例
        browser = Chromium(co)
        self.browser = browser
        return browser

    def _get_browser_options(self, user_agent=None):
        """获取浏览器配置"""
        co = ChromiumOptions()
        try:
            extension_path = self._get_extension_path("turnstilePatch")
            co.add_extension(extension_path)
        except FileNotFoundError as e:
            logging.warning(f"警告: {e}")

        browser_path = os.getenv("BROWSER_PATH")
        if browser_path:
            co.set_paths(browser_path=browser_path)

        co.set_pref("credentials_enable_service", False)
        co.set_argument("--hide-crash-restore-bubble")
        proxy = os.getenv("BROWSER_PROXY")
        if proxy:
            co.set_proxy(proxy)

        co.auto_port()
        if user_agent:
            co.set_user_agent(user_agent)

        co.headless(
            os.getenv("BROWSER_HEADLESS", "True").lower() == "true"
        )  # 生产环境使用无头模式

        # Mac 系统特殊处理
        if sys.platform == "darwin":
            co.set_argument("--no-sandbox")
            co.set_argument("--disable-gpu")

        return co

    def _get_extension_path(self,exname='turnstilePatch'):
        """获取插件路径"""
        root_dir = os.getcwd()
        extension_path = os.path.join(root_dir, exname)

        if hasattr(sys, "_MEIPASS"):
            extension_path = os.path.join(sys._MEIPASS, exname)

        if not os.path.exists(extension_path):
            raise FileNotFoundError(f"插件不存在: {extension_path}")

        return extension_path

    def quit(self):
        """关闭浏览器"""
        if self.browser:
            try:
                self.browser.quit()
            except:
                pass
