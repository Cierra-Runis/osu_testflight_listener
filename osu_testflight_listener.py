'''
一个为及时获取 osu 的 testflight 资格所写的小型监听器
osu_testflight_listener.py
'''

import os
import re
import time
import requests
from alive_progress import alive_bar
from listener_email import ListenerEmail, sent_email

regex = re.compile(r'>https://testflight.apple.com/join/(.*)</a>')

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
        custom_html = f'''
        <p>
            Osu 测试通道已更新为
            <a href="https://testflight.apple.com/join/{new}">
            https://testflight.apple.com/join/{new}
            </a>
        </p>
        <p>
            详见
            <a href="https://osu.ppy.sh/home/testflight">
            https://osu.ppy.sh/home/testflight
            </a>
        </p>
        '''
        sent_email(
            email=ListenerEmail(f'{DIR}/email.json'),
            subject='Osu 测试通道已更新！',
            name='osu_testflight_listener',
            custom_html=custom_html,
            lang='zh-CN',
        )
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

    while True:
        try:
            diff()
        except Exception as e:
            print(e)
        wait()
