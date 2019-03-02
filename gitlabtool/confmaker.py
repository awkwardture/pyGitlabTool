import platform
from jinja2 import Environment, FileSystemLoader
from flask import *
import os
import sys
import shutil  # 内置文件操作
import requests  # requests框架，一个httpclient
import subprocess

from tornado.wsgi import WSGIContainer
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop

# 实例化Flask类，flask框架的web服务器
app = Flask(__name__)
confmakers = {}
SLASH = "/"
if platform.system() == "Windows":
    SLASH = "\\"


class ConfMaker:
    def __init__(self, center, host, token, new_gitgroup_url, new_repo_url):
        self.center = center
        self.host = host
        self.token = token
        self.new_gitgroup_url = new_gitgroup_url
        self.new_repo_url = new_repo_url

    def prepareSrc(self, src, dist, **kvargs):
        # 判断路径是否存在
        if os.path.exists(dist):
            # 判断操作系统
            if platform.system() == "Windows":
                os.system("rd /s/q  {}".format(dist))
            else:
                os.system("rm -rf  {}".format(dist))
            # rd(dist)
        shutil.copytree(src, dist, ignore=shutil.ignore_patterns('.git'))
        self.__render_to_file(dist, **kvargs)

    # __ 双下划线开头的方法是私有方法，只有类内访问
    # _ 单下划线，可以子类访问
    # 用jinja渲染模板生成最终配置文件的主函数
    def __render_to_file(self, tamplate_dir, **kvargs):
        env = Environment(loader=FileSystemLoader(tamplate_dir))
        tpl_list = os.listdir(tamplate_dir)
        # 渲染tpl目录下的所有模板
        for t in tpl_list:
            if t != 'apiGateway':
                tpl = env.get_template(t)
                output = tpl.render(kvargs)
                with open(tamplate_dir + SLASH + t, 'w') as out:
                    out.write(output)

    def createGitRepo(self, grp=None, subgrp=None, description=None, subdescription=None, repo=None):
        parent_id = 0
        if grp is not None and subgrp is None:
            # 构建query参数
            payload = {'name': grp, 'path': grp, 'description': description, 'parent_id': None,
                       'private_token': self.token}
            # 调用,拼接参数
            r = requests.post(self.new_gitgroup_url, params=payload)
            print(r.url)
            resp = r.json()
            print(json.dumps(resp))
            parent_id = resp["id"]
        elif grp is not None and subgrp is not None:
            parent_id = findGrpId(grp, self.token, self.new_gitgroup_url)
            if parent_id == 0:
                # 如果没找到，创建父群组
                payload = {'name': grp, 'path': grp, 'description': description, 'parent_id': None,
                           'private_token': self.token}
                r = requests.post(self.new_gitgroup_url, params=payload)
                print(r.url)
                resp = r.json()
                print(json.dumps(resp))
                parent_id = resp["id"]
            payload = {'name': subgrp, 'path': subgrp, 'description': subdescription, 'parent_id': parent_id,
                       'private_token': self.token}
            r = requests.post(self.new_gitgroup_url, params=payload)
            print(r.url)
            resp = r.json()
            print(json.dumps(resp))
            parent_id = resp["id"]
        else:
            raise NotImplementedError

        payload = {'name': repo, 'namespace_id': parent_id, 'private_token': self.token}
        r = requests.post(self.new_repo_url, params=payload)
        print(r.url)
        return json.dumps(r.json())

    def pushGitRepo(self, dist, grp, subgrp, repo):
        remote = ""
        if grp is not None and subgrp is None:
            remote = self.host + "/" + grp + "/" + repo + ".git"
        elif grp is not None and subgrp is not None:
            remote = self.host + "/" + grp + "/" + subgrp + "/" + repo + ".git"
        else:
            raise NotImplementedError
        # 字符串前加r, 代表原始字符串
        os.chdir(dist)
        # cmd = r'git init'
        # print(cmd)
        # os.system(cmd)
        # cmd = r'git remote add origin {}'
        # cmd = cmd.format(remote)
        # print(cmd)
        # os.system(cmd)
        # cmd = r'git add .'
        # print(cmd)
        # os.system(cmd)
        # cmd = r'git commit -m "Initial commit"'
        # print(cmd)
        # os.system(cmd)
        # cmd = r'git push -u origin master'
        # print(cmd)
        # os.system(cmd)
        cmd = "git init && git remote add origin {} && git add . && git commit -m \"Initial commit\" && git push -u origin master".format(
            remote)
        print(cmd)
        subprocess.run(cmd, shell=True)
        os.chdir("..")


def main(argv=None):
    # server = ThreadingHTTPServer(('0.0.0.0', 7777), WebRequestHandler)
    # ip, port = server.server_address
    # # Start a thread with the server -- that thread will then start one
    # # more thread for each request
    # server_thread = threading.Thread(target=server.serve_forever)
    # # Exit the server thread when the main thread terminates
    # server_thread.setDaemon(True)
    # server_thread.start()
    # print
    # "Server loop running in thread:", server_thread.getName()
    # while True:
    #     pass
    # app.run('127.0.0.1','7777')
    # useDebug=str_to_bool(argv)
    # app.run(host='0.0.0.0', port='7777', debug=useDebug)
    http_server = HTTPServer(WSGIContainer(app))
    http_server.listen(7777)
    IOLoop.instance().start()


def str_to_bool(args):
    if len(args) < 2:
        return False
    elif args is None:
        return False
    elif args[1].lower() == 'true':
        return True
    return False


# flash路由，python装饰器其实是一个包装函数的函数,@是执行这个包装函数
@app.route('/pyGitlabTool')
def pyGitlabTool():
    result = "ok"
    # flask框架的request.args是query参数
    center = request.args.get("center")
    grp = request.args.get("group")
    subgrp = request.args.get("subgroup")
    desc = request.args.get("desc")
    subdesc = request.args.get("subdesc")
    repo = request.args.get("repo")
    rmqhost = request.args.get("rmqhost")
    host = request.args.get("host")
    token = request.args.get("token")
    srcpath = request.args.get("srcpath")
    if platform.system() == "Windows":
        srcpath = "d:" + srcpath
        srcpath = srcpath.replace("/", "\\")
        print(srcpath)
    baserepo = request.args.get("baserepo")
    if center is None or repo is None or host is None or token is None or srcpath is None or baserepo is None:
        return "缺少参数"
    src, dist, new_gitgroup_url, new_repo_url = getReqInfo(host, token, srcpath, baserepo, repo)
    makerKey = host + center + repo
    # python字典，可以用in判断key是否存在
    if makerKey in confmakers:
        maker = confmakers[makerKey]
    else:
        # 实例化类对象
        maker = ConfMaker(center, host, token, new_gitgroup_url, new_repo_url)
        # 字典赋值，就是map.put
        confmakers[makerKey] = maker
    kvargs = {'center': center, 'rmqhost': rmqhost}
    maker.prepareSrc(src, dist, **kvargs)
    result = maker.createGitRepo(grp, subgrp, desc, subdesc, repo)
    maker.pushGitRepo(dist, grp, subgrp, repo)
    return result


@app.route('/pyGitlabTool/reset')
def toolReset():
    grp = request.args.get("group")
    host = request.args.get("host")
    token = request.args.get("token")
    if grp is None or host is None or token is None:
        return "缺少参数group"
    new_gitgroup_url = getReqInfo(host, token)
    grpid = findGrpId(grp, token, new_gitgroup_url)
    delGrpUrl = new_gitgroup_url + "/" + str(grpid)
    payload = {'private_token': token}
    r = requests.delete(delGrpUrl, params=payload)
    print(r.url)
    return r.text


def getReqInfo(host, token, srcpath=None, baserepo=None, repo=None):
    if host is None or token is None:
        raise RuntimeError("host和token不能为空")
    gitlab_api_url = host + "/api/v4"
    if srcpath is None:
        return gitlab_api_url + "/groups"
    else:
        srctp = srcpath + SLASH + "{}"
        src = srctp.format(baserepo)
        dist = srctp.format(repo)
        new_gitgroup_url = gitlab_api_url + "/groups"
        new_repo_url = gitlab_api_url + "/projects"
        return src, dist, new_gitgroup_url, new_repo_url


def findGrpId(grp, token, new_gitgroup_url):
    parent_id = 0
    payload = {'search': grp, 'private_token': token}
    r = requests.get(new_gitgroup_url, params=payload)
    print(r.url)
    jsonbody = r.json()
    for pGrp in jsonbody:
        if pGrp["name"] == grp:
            parent_id = pGrp["id"]
            break
    return parent_id


def rd(dist):
    filelist = os.listdir(dist)  # 列出该目录下的所有文件名
    for f in filelist:
        filepath = os.path.join(dist, f)  # 将文件名映射成绝对路劲
        if os.path.isfile(filepath):  # 判断该文件是否为文件或者文件夹
            os.remove(filepath)  # 若为文件，则直接删除
            print(str(filepath) + " removed!")
        elif os.path.isdir(filepath):
            rd(filepath)
    shutil.rmtree(dist, False)  # 最后删除文件夹
    print("删除成功")


if __name__ == '__main__':
    main(sys.argv)
