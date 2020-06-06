import sys
import re
import requests
import configparser
from bs4 import BeautifulSoup
import logging as log
import coloredlogs
from pprint import pprint
import time
coloredlogs.install()

log.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(module)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S %p',
        level=log.NOTSET
)

HOST = "https://carenew.gaodun.com"

session = requests.Session()
parser = configparser.ConfigParser()
try:
    parser.read_file(open('config.ini', encoding='utf-8'))
    USERNAME = parser.get('user', 'username')
    PASSWORD = parser.get('user', 'password')
    q_list_str = parser.get('question', 'q_type')
    TYPE_LIST = [s.strip() for s in re.split(',|，', q_list_str)]
except FileNotFoundError as e:
    log.error('找不到配置文件, 请拷贝配置文件到当前目录')
    sys.exit(0)
except configparser.ParsingError as e:
    log.error('配置文件格式错误')
    sys.exit(0)


def login(username, password):
    login_url = f"{HOST}/Home/Login/login"
    data = {'username': username,'pwd': password}
    session.get(HOST)
    resp = session.post(login_url, data=data)
    if '密码错误' in resp.text:
        log.error('用户名或密码错误')
        sys.exit(1)

def get_question_list():
    task_url = f'{HOST}/Qmanage/myanswer?p=1&ask_type=0&project_id=0&class_id=0&subject_id=0&type_id=0&type=3&datasort=asc&ismyq=2&search_content=&pagesize=15&cfa_type=0&sort_type=time&allcount=0'
    resp = session.get(task_url)
    return resp.json()['data']['html']

def parseData(html):
    question_ids = []
    soup = BeautifulSoup(html, 'html.parser')
    tbody = (soup.table.tbody)

    for tr in tbody.find_all('tr'):
        q_id = parseQuestion(tr)
        if q_id:
            print(q_id)
            log.info("添加任务到待提交列表: " + q_id)
            question_ids.append(q_id)
    return question_ids

def parseQuestion(trSoup):
    tds = trSoup.find_all('td')
    q_id = tds[1].text
    q_type = tds[3].div.text
    if q_type in TYPE_LIST:
        log.info('找到符合的问题来源: ' + q_type)
        return q_id
    return None

def submit(question_ids):
    if not question_ids:
        log.info('待提交列表为空, 5 秒后重新尝试')
        return
    data = {
        'ask_id': question_ids
    }
    submit_url = f'{HOST}/Qmanage/qAccept'

    log.info('提交任务: ' + str(question_ids))
    headers = {
        'Referer': f'{HOST}/Qmanage/myAnswer',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.117 Safari/537.36'
    }
    resp = session.post(submit_url, headers=headers, data=data)
    result = resp.json()
    success = result['data']['accept_success']
    if success:
        num = result['data']['accept_num']
        log.info('成功抢到' + str(num) + '个问题')
    else:
        reason = result['info']
        log.info('抢题失败, 原因: ' + reason)   
    
def main():
    data = get_question_list()
    question_ids = parseData(data)
    submit(question_ids)

if __name__ == '__main__':
    login(USERNAME, PASSWORD)
    while True:
        main()
        time.sleep(5)
    input()