'''
一个为及时获取 osu 的 testflight 资格所写的小型监听器
osu_testflight_listener.py
'''

import json
import os
import re
import smtplib
from email.mime.text import MIMEText
import sys
import time
import requests
from alive_progress import alive_bar

regex = re.compile(r'>https://testflight.apple.com/join/(.*)</a>')
regex_html = re.compile(
    r"<td id=\"content-cell\" align=\"left\">\n([\s\S]*?)\n                </td>"
)
DIR = os.path.dirname(__file__)
PATH = DIR + r'\osu_testflight_listener.txt'
MIN = 60  # 分钟数
TICK = int(MIN * 6000 / 11)  # 所需 tick 数（不严谨计算）


def get_last() -> str:
    '''
    获取上次记录的 `token`
    '''
    with open(PATH, 'r', encoding='utf-8') as file:
        return file.read().strip()


def save_token(new_token: str):
    '''
    保存本次获取的 `token`
    '''
    with open(PATH, 'w', encoding='utf-8') as file:
        file.write(new_token)


class Email():
    '''
    存储获取邮件发送配置信息
    '''
    # 服务器地址
    mail_host: str
    # 用户名
    mail_user: str
    # 密码或授权码
    mail_pass: str
    # 邮件发送方地址
    sender: str
    # 邮件接受方地址, 类型为 list 可以群发
    receivers: list

    def __init__(self, email_json: json) -> None:
        # 将传入的 email_json 分配给类
        self.mail_host = email_json['mail_host']
        self.mail_user = email_json['mail_user']
        self.mail_pass = email_json['mail_pass']
        self.sender = email_json['sender']
        self.receivers = email_json['receivers']


def sent_email(**kwargs):
    '''
    发送邮件
    '''

    for receiver in EMAIL.receivers:
        # 设置 email 信息
        # 邮件内容设置

        raw_html = open(f'{DIR}/email.html', 'r', encoding='utf-8').read()

        custom_html = f'''
            <p>你好 {receiver} ！</p>
            <p>
                Osu 测试通道已更新为
                <a href="https://testflight.apple.com/join/{kwargs['info']}">
                https://testflight.apple.com/join/{kwargs['info']}
                </a>
            </p>
            <p>
                详见
                <a href="https://osu.ppy.sh/home/testflight">
                https://osu.ppy.sh/home/testflight
                </a>
            </p>
            <p>
                如果您未订阅本提醒服务，请与
                <a href="mailto:{EMAIL.sender}">服务订阅者</a>
                联系。
            </p>
            '''
        raw_html = regex_html.sub(
            f"<td id=\"content-cell\" align=\"left\">\n{custom_html}\n                </td>",
            raw_html,
        )

        print(raw_html)

        message = MIMEText(raw_html, 'html', 'utf-8')
        # 邮件主题
        message['Subject'] = 'Osu 测试通道已更新！'
        # 发送方信息
        message['From'] = f'osu_testflight_listener <{EMAIL.sender}>'
        # 接受方信息
        message['To'] = receiver

        # 登录并发送邮件
        try:
            smtp_obj = smtplib.SMTP_SSL(EMAIL.mail_host)
            # 登录到服务器
            smtp_obj.login(EMAIL.mail_user, EMAIL.mail_pass)
            # 发送
            smtp_obj.send_message(message)
            # 退出
            smtp_obj.quit()
            print('success')
        except smtplib.SMTPException as error:
            # 打印错误
            print('error', error)


def wait():
    '''
    等待下次检查
    '''
    with alive_bar(TICK, title='等待下次检查') as process_bar:
        for _ in range(TICK):
            time.sleep(0.1)
            process_bar()
    print()


def diff():
    '''
    获取并比较俩次 `token`
    '''
    res = requests.get(
        'https://osu.ppy.sh/home/testflight',
        timeout=None,
    )
    new = regex.findall(res.text)[0]
    last = get_last()
    if new != last:
        print('检测到链接改变，正在发送邮件')
        sent_email(info=new)
        save_token(new)
    else:
        print(f'链接未改变( https://testflight.apple.com/join/{last} )')


def insert_after(element, new_element):
    '''
    在元素 element 后插入 new_element
    '''
    parent = element.getparent()
    parent.insert(parent.index(element) + 1, new_element)


if __name__ == '__main__':
    os.system('cls')
    EMAIL = Email(
        json.loads(open(
            f'{DIR}/email.json',
            'r',
            encoding='utf-8',
        ).read()))

    while True:
        try:
            diff()
        except Exception as e:
            print(e)
        wait()
