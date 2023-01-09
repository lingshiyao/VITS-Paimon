import time
from concurrent.futures import ThreadPoolExecutor
from os.path import exists

from flask import Flask, request, send_file, Response
import os

from api.app_constance import AppConstance
from api.paimon import Paimon
from api.net.req_params_getter import ReqParamsGetter
from api.block_runner.runner import Runner
from api.task import Task
from api.block_runner.task_queue import TaskQueue
from zfoutils import ZfoUtils

taskQuene = TaskQueue()
runner = Runner([Paimon()])
def loop():
    while True:
        time.sleep(0.02)
        task = taskQuene.get_not_running_head()
        if task is not None and not task.running:
            task.running = True
            print("here")
            result = runner.run("gen", task.text, task.token, task.need_cache)
            if result is None:
                task.running = False
            else:
                taskQuene.remove_task_by_token(task.token)
pool = ThreadPoolExecutor(max_workers=runner.get_runner_count())
for i in range(runner.get_runner_count()):
    pool.submit(loop)

app = Flask(__name__)

@app.route('/')
def hello_world():  # put application's code here
    return 'Hello paimon!'

# 创建一个map，key是token，value是task
taskMap = {}

# 0 running
# 1 add task success
@app.route('/tryToAddPaimonTask', methods=['POST'])
def try_to_add_paimon_audio_task():
    token = request.headers.get('Authorization')
    if token is None:
        return "no token", 500
    text = ReqParamsGetter.get_params('text', default='您没有输入文本')
    need_refresh_cache = ReqParamsGetter.get_params('need_refresh_cache')
    if need_refresh_cache is not None:
        if need_refresh_cache == "1":
            need_refresh_cache = True
        else:
            need_refresh_cache = False
    else:
        need_refresh_cache = False

    need_cache = ReqParamsGetter.get_params('need_cache')
    if need_cache is not None:
        if need_cache == "1":
            need_cache = True
        else:
            need_cache = False
    else:
        need_cache = False

    task = Task(token=token, text=text, need_cache=need_cache, need_refresh_cache=need_refresh_cache)
    taskMap[token] = task
    if need_cache and not need_refresh_cache:
        if exists(AppConstance.OUT_PUT_PATH + ZfoUtils.md5(text) + '.wav'):
            return str(1)

    result = taskQuene.add_task(task)
    if not result:
        return str(0)
    return str(1)


# -1 not found
# 0 running
# >0 排队中
@app.route('/getPaimonTaskLeft', methods=['POST'])
def get_paimon_task_left():
    token = request.headers.get('Authorization')
    if token is None:
        return "no token", 500
    return str(taskQuene.get_index_not_running(token))

@app.route('/getPaimonTaskLeftSee', methods=['POST'])
def get_paimon_task_left_see():
    token = request.headers.get('Authorization')
    if token is None:
        return "no token", 500
    return Response(event_stream_paimon(token), mimetype='text/event-stream')

def event_stream_paimon(token):
    while True:
        data = taskQuene.get_index_not_running(token) # 获取下一条数据
        print("data:", data)
        yield 'data: %s\n\n' % str(data) # 发送 SSE 消息
        if data == -1:
            break
        time.sleep(1)  # 延迟 1 秒

# -1 not found
@app.route('/getPaimonVoiceFile', methods=['POST'])
def get_paimon_voice_file():
    print("getPaimonVoiceFile")
    token = request.headers.get('Authorization')
    if token is None:
        return "no token", 500
    voice_path = AppConstance.OUT_PUT_PATH + token + ".wav"
    task = taskMap.get(token)
    print(task)
    if task.need_cache:
        voice_path = AppConstance.OUT_PUT_PATH + ZfoUtils.md5(task.text) + ".wav"
    print(voice_path)
    if not exists(voice_path):
        return "no file", 500
    return send_file(voice_path, mimetype='audio/wav')


# 1000 no token
# 1001 file not found
if __name__ == '__main__':
    from waitress import serve

    # serve(app, host="0.0.0.0", port=5004)
    serve(app,
          host=os.getenv('HOST', '0.0.0.0'),
          port=int(os.getenv('PORT', '5004')),
          # 是否在出现异常时，将异常的跟踪信息暴露到客户端。默认为True。
          expose_tracebacks=True,
          # Waitress 服务器的连接数上限。默认为 "1000"。
          connection_limit=os.getenv('CONNECTION_LIMIT', '2000'),
          # 服务器使用的线程数。默认为 "50"。
          threads=os.getenv('THREADS', '100'),
          # Waitress 服务器使用的通道超时时间。默认为 "10" 秒。
          channel_timeout=os.getenv('CHANNEL_TIMEOUT', '20'),
          # Waitress 服务器进行清理的间隔时间。默认为 "30" 秒。
          cleanup_interval=os.getenv('CLEANUP_INTERVAL', '30'),
          # 服务器的连接队列长度。默认为"2048"。
          backlog=os.getenv('BACKLOG', '2048'))
