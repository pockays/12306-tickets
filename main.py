# 导入selenium模块
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec

# 创建浏览器对象
driver = webdriver.Chrome()


class TrainSpider(object):
    # 定义类属性
    login_url = 'https://kyfw.12306.cn/otn/resources/login.html'  # 登录的页面
    profile_url = 'https://kyfw.12306.cn/otn/view/index.html'  # 个人中心的网址

    def __int__(self, from_station, to_station, train_date):
        self.from_station = from_station
        self.to_station = to_station
        self.train_date = train_date

    def login(self):
        # 打开12306的网页
        driver.get(self.login_url)
        # 模拟输入用户名
        username = driver.find_element(By.ID, "J-userName")
        username.send_keys('15137771585')
        # 模拟输入密码
        password = driver.find_element(By.ID, 'J-password')
        password.send_keys('134511130qq')
        # 模拟点击登录按钮
        login_btn = driver.find_element(By.ID, 'J-login')
        login_btn.click()
        WebDriverWait(driver,1000).until(
            ec.url_to_be(self.profile_url)
        )
        print('登录成功')

    def run(self):
        self.login()


def start():
    spider = TrainSpider()
    spider.run()


if __name__ == '__main__':
    start()
    input('输入任意键结束')