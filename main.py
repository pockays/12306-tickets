# 导入selenium模块
import openpyxl
from selenium import webdriver
from selenium.common import NoSuchElementException, ElementNotVisibleException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
import datetime
import time

# 目前需要修改的点   1：实时更新车票更新并进行重复抢票
# 2：去掉各种确认窗口
# 创建浏览器对象
driver = webdriver.Chrome()


class TrainSpider(object):
    # 定义类属性
    login_url = 'https://kyfw.12306.cn/otn/resources/login.html'  # 登录的页面
    profile_url = 'https://kyfw.12306.cn/otn/view/index.html'  # 个人中心的网址
    left_ticket = 'https://kyfw.12306.cn/otn/leftTicket/init?linktypeid=dc'  # 余票查询
    confirm_url = 'https://kyfw.12306.cn/otn/confirmPassenger/initDc'  # 确认界面

    def __init__(self, from_station, to_station, train_date, trains, passengers, ticket_type, target_datetime):
        self.selected_no = None
        self.from_station = from_station
        self.to_station = to_station
        self.train_date = train_date
        self.station_code = self.init_station_code()
        self.trains = trains
        self.passengers = passengers
        self.ticket_type = ticket_type
        self.seat_type = None
        self.target_datetime = target_datetime

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
        # 获取元素
        from_station_input = driver.find_element(By.ID, 'fromStation')
        to_station_input = driver.find_element(By.ID, 'toStation')
        train_date_input = driver.find_element(By.ID, 'train_date')
        # 通过目的地/出发地找到相应代号
        from_station_code = self.station_code[self.from_station]
        to_station_code = self.station_code[self.to_station]
        # 填入代号
        driver.execute_script('arguments[0].value="%s"' % from_station_code, from_station_input)
        driver.execute_script('arguments[0].value="%s"' % to_station_code, to_station_input)
        driver.execute_script('arguments[0].value="%s"' % self.train_date, train_date_input)
        # 查询
        query_ticker_tag = driver.find_element(By.ID, 'query_ticket')
        is_flag = False
        while True:  # 重复查询刷新抢票
            current_datetime = datetime.datetime.now()
            if current_datetime >= self.target_datetime:
                while True:
                    query_ticker_tag.click()
                    # 解析车次
                    WebDriverWait(driver, 1000).until(
                        ec.presence_of_element_located((By.XPATH, '//tbody[@id = "queryLeftTable"]/tr'))
                    )
                    trains = driver.find_elements(By.XPATH, '//tbody[@id = "queryLeftTable"]/tr[not(@datatran)]')
                    for train in trains:
                        infos = train.text.replace('\n', ' ').split(' ')
                        train_no = infos[0]  # 显示车次
                        if train_no in self.trains:  # 是否存在需求车次
                            seat_types = self.trains[train_no]
                            for seat_type in seat_types:  # 查找是否有位置
                                if seat_type == 'O':  # 如果是二等座
                                    count = infos[9]
                                    if count.isdigit() or count == '有':
                                        is_flag = True
                                        break  # 退出席位循环
                                elif seat_type == 'M':
                                    count = infos[8]
                                    if count.isdigit() or count == '有':
                                        is_flag = True
                                        break
                            # 是否有余票
                            if is_flag:
                                order_btn = train.find_element(By.XPATH,
                                                               './/a[@class="btn72"]')  # 注意是.// 表示当前路径，否则是在全局选择，而不是当前行
                                order_btn.click()
                                self.selected_no = train_no
                                return  # 退出该函数
            time.sleep(1)  # 每过一秒进行检查当前时间

    def confirm(self):
        WebDriverWait(driver, 1000).until(
            ec.url_to_be(self.confirm_url)
        )
        WebDriverWait(driver, 1000).until(
            ec.presence_of_element_located((By.XPATH, '//ul[@id = "normal_passenger_id"]/li/label'))
        )
        passengers = driver.find_elements(By.XPATH, '//ul[@id = "normal_passenger_id"]/li/label')
        for passenger in passengers:
            passenger_name = passenger.text.replace('(学生)', '')  # 学生认证后会有（学生）
            if passenger_name in self.passengers:
                passenger.click()
                # 选学生票会有弹窗
                if ec.visibility_of_element_located((By.ID, 'dialog_xsertcj_msg')):
                    student_ticket_ok = driver.find_element(By.ID, 'dialog_xsertcj_ok')
                    WebDriverWait(driver, 1000).until(
                        ec.element_to_be_clickable((By.ID, 'dialog_xsertcj_ok'))
                    )
                    student_ticket_ok.click()

        # 选择票类
        ticket_select = Select(driver.find_element(By.ID, 'ticketType_1'))
        ticket_select.select_by_value(self.ticket_type)
        # 选择席位
        seat_select = Select(driver.find_element(By.ID, 'seatType_1'))
        seat_types = self.trains[self.selected_no]
        for seat_type in seat_types:
            try:
                seat_select.select_by_value(seat_type)
                self.seat_type = seat_type
            except NoSuchElementException:
                continue
            else:
                break
        # 提交订单
        WebDriverWait(driver, 1000).until(
            ec.element_to_be_clickable((By.ID, 'submitOrder_id'))
        )
        submit_btn = driver.find_element(By.ID, 'submitOrder_id')
        submit_btn.click()

        WebDriverWait(driver, 1000).until(
            ec.presence_of_element_located((By.CLASS_NAME, 'dhtmlx_window_active'))
        )
        WebDriverWait(driver, 1000).until(
            ec.element_to_be_clickable((By.ID, 'qr_submit_id'))
        )
        submit_btn = driver.find_element(By.ID, 'qr_submit_id')
        while submit_btn:
            try:
                submit_btn.click()
                submit_btn = driver.find_element(By.ID, 'qr_submit_id')
            except ElementNotVisibleException:
                break
        print(f'恭喜{self.selected_no}的{self.seat_type}抢票成功！')

    def run(self):
        # 登录
        self.login()
        # 余票查询
        self.search_ticket()
        # 确认订单
        self.confirm()

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


def start():  # o为二等座，m为一等座，9为商务座         票类别分为 成人票为1 儿童票为2 学生票为3 残军票为4    year,month, day,hour, minute,second,microsecond
    spider = TrainSpider('葫芦岛', '大连', '2023-07-13', {'G1253': ['O', 'M']}, ['郭政熠'], '1',
                         datetime.datetime(2023, 7, 6, 10, 43))
    spider.run()


if __name__ == '__main__':
    start()
    input('输入任意键结束')
    driver.quit()
