from datetime import datetime
import os
import re
import smtplib
from email.mime.text import MIMEText
import sys
from time import sleep
import requests

regex = re.compile(r'>https://testflight.apple.com/join/(.*)</a>')
PATH = os.path.dirname(sys.argv[0])+'\osu_testflight.txt'


def get_last() -> str:
    with open(PATH) as f:
        return f.read().strip()


def save_token(s: str):
    with open(PATH, 'w') as f:
        f.write(s)


def sent_email(info):
    # 邮箱服务器地址
    mail_host = 'smtp.qq.com'
    # 用户名
    mail_user = '2864283875'
    # 密码(部分邮箱为授权码)
    mail_pass = 'urqcczoemnhrdhdi'
    # 邮件发送方邮箱地址
    sender = '2864283875@qq.com'
    # 邮件接受方邮箱地址，注意需要[]包裹，这意味着你可以写多个邮件地址群发
    receivers = ['a2864283875@foxmail.com']

    # 设置email信息
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
        print('error', e)  # 打印错误


def diff():
    res = requests.get('https://osu.ppy.sh/home/testflight')
    new = regex.findall(res.text)[0]
    last = get_last()
    if last != new:
        print(f'{last} changed to {new} at {datetime.now()}!')
        sent_email(
            f'Osu 测试通道已更新为 https://testflight.apple.com/join/{new} ！\n' + '详见 https://osu.ppy.sh/home/testflight')
        save_token(new)
    else:
        print(f'{get_last()} hasn\'t changed!')


if __name__ == '__main__':
    while True:
        try:
            diff()
        except Exception as e:
            print(e)
        for i in range(0, 600):
            print(i/10)
            sleep(0.1)
