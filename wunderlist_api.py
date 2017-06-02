# -*- coding: utf-8 -*-

import json, sys
sys.path.append('./requests_oauthlib')
from requests_oauthlib import OAuth2Session
import requests
sys.path.append('../')
import env

CLIENT_ID = env.WUNDERLIST_CLIENT_ID
TOKEN = env.WUNDERLIST_TOKEN


URL = "https://a.wunderlist.com/api/v1/"
params = {}

# wunderlistとのセッションを作る
def create_session():
    wunderlist = OAuth2Session()
    wunderlist.headers['X-Client-ID'] = CLIENT_ID
    wunderlist.headers['X-Access-Token'] = TOKEN
    return wunderlist

# プロジェクトのリストを取得
def get_project_list(sess):
    end_point = URL + 'lists'
    params = {}
    req = sess.get(end_point, params=params)
    res = json.loads(req.text)
    return res

# タスクのリストを取得
def get_task_list(sess, project_id=0):
    end_point = URL + 'tasks'
    params = { 'list_id': project_id }
    req = sess.get(end_point, params=params)
    res = json.loads(req.text)
    return res

# タスクのrevisionの取得
def get_task_revision(sess, task_id):
    end_point = URL + 'tasks/' + str(task_id)
    req = sess.get(end_point, params={})
    return json.loads(req.text)['revision']

# タスクを追加
def add_task(sess, task='', due_date='', project_id=0):
    end_point = URL + 'tasks'
    params = {
        'title': task,
        'list_id': project_id,
        'due_date': due_date
    }
    req = sess.post(end_point, json=params)
    return 0

# タスクを完了にする
def complete_task(sess, task_id, revision):
    end_point = URL + 'tasks/' + str(task_id)
    params = {
        'revision': revision,
        'completed': True
    }
    req = sess.patch(end_point, json=params)
    return "タスクを完了しました"

def get_task_list_payload(sess, project_id=0):
    res = get_task_list(sess, project_id=project_id)
    ret = []

    for i in res:
        text = i['title'] + '  期限: '
        ret.append(
            {
                'fallback': 'wunderlist',
                'text': text + i['due_date'] if 'due_date' in i else text,
                'callback_id': "task",
                'color': '#3000f0',
                'attachment_type': 'default',
                'actions': [
                    {
                        'name': 'complete',
                        'text': '完了',
                        'type': 'button',
                        'value': i['id']
                    }
                ]
            }
        )
    return json.dumps(ret)

# タスクのリストをslackに投稿する
# タスクのリストをslackに送りたいときはこいつを使う
def post_task_list(sess, channel='', project_id=0):
    lis = get_task_list_payload(sess, project_id=project_id)
    payload = {
        'token': env.APP_TOKEN,
        'channel': channel,
        'username': 'wunderlist',
        'attachments': lis
    }
    url = 'https://slack.com/api/chat.postMessage'
    requests.post(url, data=payload)



'''
###############################################
こっからはAPIとやり取りしない処理
###############################################
'''

def get_project_id_by_name(sess, name=''):
    lis = get_project_list(sess)
    for i in lis:
        if i['title'] == name:
            return i['id']

