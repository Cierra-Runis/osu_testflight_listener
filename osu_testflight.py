import os
import re
import smtplib
from email.mime.text import MIMEText
import sys
import requests
from alive_progress import alive_bar
import time

regex = re.compile(r'>https://testflight.apple.com/join/(.*)</a>')
PATH = os.path.dirname(sys.argv[0]) + '\osu_testflight.txt'


def get_last() -> str:
    with open(PATH) as f:
        return f.read().strip()


def save_token(s: str):
    with open(PATH, 'w') as f:
        f.write(s)


def sent_email(info):
    # 服务器地址
    mail_host = 'smtp.qq.com'
    # 用户名
    mail_user = '2864283875'
    # 密码或授权码
    mail_pass = 'urqcczoemnhrdhdi'
    # 邮件发送方地址
    sender = '2864283875@qq.com'
    # 邮件接受方地址，注意需 [] 包裹，这意味着可以群发
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
        smtpObj = smtplib.SMTP_SSL(mail_host)
        # 登录到服务器
        smtpObj.login(mail_user, mail_pass)
        # 发送
        smtpObj.sendmail(
            sender, receivers, message.as_string())
        # 退出
        smtpObj.quit()
        print('success')
    except smtplib.SMTPException as e:
        # 打印错误
        print('error', e)


def wait():
    with alive_bar(5000, title='等待下次检查') as bar:
        for item in range(5000):
            time.sleep(0.1)
            bar()
    print()


def diff():
    res = requests.get('https://osu.ppy.sh/home/testflight')
    new = regex.findall(res.text)[0]
    last = get_last()
    if last != new:
        print('检测到链接改变，正在发送邮件')
        sent_email(
            f'Osu 测试通道已更新为 https://testflight.apple.com/join/{new} ！\n' + '详见 https://osu.ppy.sh/home/testflight')
        save_token(new)
    else:
        print('链接未改变')


if __name__ == '__main__':
    while True:
        try:
            diff()
        except Exception as e:
            print(e)
        wait()
