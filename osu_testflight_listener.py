'''
一个为及时获取 osu 的 testflight 资格所写的小型监听器
osu_testflight_listener.py
'''

import os
import re
import smtplib
from email.mime.text import MIMEText
import sys
import time
import requests
from alive_progress import alive_bar

regex = re.compile(r'>https://testflight.apple.com/join/(.*)</a>')
PATH = os.path.dirname(sys.argv[0]) + r'\osu_testflight_listener.txt'
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


def sent_email(info):
    '''
    发送邮件
    '''
    # 服务器地址
    mail_host = 'smtp.qq.com'
    # 用户名
    mail_user = '2864283875'
    # 密码或授权码
    mail_pass = 'urqcczoemnhrdhdi'
    # 邮件发送方地址
    sender = '2864283875@qq.com'
    # 邮件接受方地址, 注意需 [] 包裹, 可以群发
    receivers = ['a2864283875@foxmail.com']

    # 设置 email 信息
    # 邮件内容设置
    message = MIMEText(info, 'plain', 'utf-8')
    # 邮件主题
    message['Subject'] = 'Osu 测试通道已更新！'
    # 发送方信息
    message['From'] = sender
    # 接受方信息
    message['To'] = receivers[0]

    # 登录并发送邮件
    try:
        smtp_obj = smtplib.SMTP_SSL(mail_host)
        # 登录到服务器
        smtp_obj.login(mail_user, mail_pass)
        # 发送
        smtp_obj.sendmail(sender, receivers, message.as_string())
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
    if last != new:
        print('检测到链接改变，正在发送邮件')
        sent_email(
            f'Osu 测试通道已更新为 https://testflight.apple.com/join/{new} ！\n' +
            '详见 https://osu.ppy.sh/home/testflight')
        save_token(new)
    else:
        print(f'链接未改变( https://testflight.apple.com/join/{last} )')


if __name__ == '__main__':
    while True:
        try:
            diff()
        except Exception as e:
            print(e)
        wait()
