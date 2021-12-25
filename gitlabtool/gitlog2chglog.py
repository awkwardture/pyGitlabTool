import os
import sys
import subprocess


class ChangeLog:
    def __init__(self, arg):
        self.cd2Repo(arg[1])
        if len(arg) > 2:
            self.branch = arg[2]
        else:
            self.branch = None
        if len(arg) > 3:
            self.dist = arg[3]
        else:
            self.dist = None
        if len(arg) > 4:
            self.title = arg[4]
        else:
            self.title = None
        self.curdate = ""
        self.curmsg = ""

    def cd2Repo(self, path):
        # 判断路径是否存在
        if os.path.exists(path):
            os.chdir(path)
        else:
            raise RuntimeError("git库目录不正确")

    def gitlog2chglog(self):
        if self.branch is not None:
            cmd = "git log {} --date=short --format=\"%cd||%d||%s\"".format(self.branch)
        else:
            cmd = "git log --date=short --format=\"%cd||%d||%s\""

        print(cmd)
        with open(self.dist, mode="w+", encoding="utf-8") as f:
            if self.title is not None:
                f.write("#{}\n".format(self.title))
            popen = subprocess.Popen(cmd, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                     stderr=subprocess.PIPE)
            while popen.stdout.readable():
                body = popen.stdout.readline()  # 获取输出结果
                oneline = body.decode("utf-8")

                if len(body) > 0:
                    vals = oneline.split(sep="||")

                    if "tag" in vals[1]:
                        start = vals[1].index("tag") + 4
                        f.write("##{}\n".format(vals[1][start:len(vals[1]) - 1]))
                    # if self.curdate != vals[0]:
                    #     self.curdate = vals[0]
                    #     f.write("{}\n\n".format(self.curdate))
                    if "maven-release-plugin" in vals[2] or vals[2].startswith("Signed-off-by") or vals[2].startswith(
                            "Merge") or vals[2].startswith("Revert"):
                        continue
                    if self.curmsg != vals[2]:
                        self.curmsg = vals[2]
                        f.write("- {}\n".format(vals[2]))


                else:
                    break
            popen.wait()
            popen.stdout.close()


def main(argv=None):
    worker = ChangeLog(argv)
    worker.gitlog2chglog()


if __name__ == '__main__':
    main(sys.argv)
