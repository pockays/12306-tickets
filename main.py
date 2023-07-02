# 导入selenium模块
import openpyxl
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
    left_ticket = 'https://kyfw.12306.cn/otn/leftTicket/init?linktypeid=dc'  # 余票查询

    def __init__(self, from_station, to_station, train_date):
        self.from_station = from_station
        self.to_station = to_station
        self.train_date = train_date
        self.station_code = self.init_station_code()

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
        # 选择短信验证，并等待能点击时再去点，否则可能会无法与元素交互
        css_selector = '#verification li:nth-child(2) a'
        check = driver.find_element(By.CSS_SELECTOR, css_selector)
        WebDriverWait(driver, 10).until(
            ec.visibility_of(check)
        )
        check.click()
        # 填入身份证后四位
        id_card = driver.find_element(By.ID, "id_card")
        WebDriverWait(driver, 10).until(
            ec.visibility_of_element_located((By.ID, "short_message"))
        )
        id_card.send_keys('0018')
        # 发送验证码
        verification_code = driver.find_element(By.ID, "verification_code")
        verification_code.click()
        WebDriverWait(driver, 1000).until(
            ec.url_to_be(self.profile_url)
        )
        print('登录成功')

    def search_ticket(self):
        driver.get(self.left_ticket)
        from_station_input = driver.find_element(By.ID, 'fromStation')
        to_station_input = driver.find_element(By.ID, 'toStation')
        train_date_input = driver.find_element(By.ID, 'train_date')
        from_station_code = self.station_code[self.from_station]
        to_station_code = self.station_code[self.to_station]
        driver.execute_script('arguments[0].value="%s"' % from_station_code, from_station_input)
        driver.execute_script('arguments[0].value="%s"' % to_station_code, to_station_input)
        driver.execute_script('arguments[0].value="%s"' % self.train_date, train_date_input)

    def run(self):
        # 登录
        self.login()
        # 余票查询
        self.search_ticket()

    def init_station_code(self):
        wb = openpyxl.load_workbook('车站代码.xlsx')
        ws = wb.active
        lst = []
        for row in ws.rows:
            sub_lst = []
            for cell in row:
                sub_lst.append(cell.value)
            lst.append(sub_lst)
        return dict(lst)


def start():
    spider = TrainSpider('北京', '上海', '2023-07-03')
    spider.run()
    spider.search_ticket()


if __name__ == '__main__':
    start()
    input('输入任意键结束')
