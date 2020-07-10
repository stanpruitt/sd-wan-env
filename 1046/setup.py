# How to setup 5G router from initial system
# Connect the second eth port near sim card, get ip from the router, and ssh to device
# 1. apt-get install ntpdate
# 2. ntpdate -s cn.pool.ntp.org
# 3. git clone https://github.com/vewe-richard/sd-wan-env.git
# 4. python3 1046/setup.py
#
# about:
# 1. 1046 kernel build and replace, detail reference youdaoyun
#   a. vm location: E:\vmware\Ubuntu1804_64bit_LSDK1903_ARM64, user ubuntu, pwd ubuntu
#   b. scp ubuntu@172.16.1.168:/home/forlinx/work/OK10xx-linux-fs/flexbuild/build/linux/linux/arm64/Image /var/run/media/mmcblk0p2/boot/
#
#
import subprocess
import os
import random
import json
class Setup5GRouter:
    def __init__(self):
        self._cwd = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
        assert self.runningUnderGitProjectRootDirectory(self._cwd)
        os.chdir(self._cwd)

        sp = subprocess.run(["dpkg", "--print-architecture"], stdout=subprocess.PIPE)
        out = sp.stdout.decode().strip()
        if "amd64" in out:
            self._root = "/tmp/root/"
        else:
            self._root = "/"

        vpaths = ["/", "/etc/systemd/network/", "/var/run/media/mmcblk0p2/boot/", "/root/.sdwan/edgepoll/", "/etc/sdwan/edge/"]
        for p in vpaths:
            sp = subprocess.run(["mkdir", "-p", self._root + p])
        pass

    def runningUnderGitProjectRootDirectory(self, cwd):
        return os.path.isfile(os.path.join(cwd, "LICENSE"))

    def wan(self):
        sp = subprocess.run(["rm", "-f", self._root + "/etc/systemd/network/fm1-mac6.network"])
        sp = subprocess.run(["rm", "-f", self._root + "/etc/systemd/network/fm1-mac9.network"])
        sp = subprocess.run(["cp", "./1046/fm1-mac9.network", self._root + "/etc/systemd/network/"])
        sp = subprocess.run(["cp", "./1046/fm1-usb0.network", self._root + "/etc/systemd/network/"])
        pass

    def git(self):
        os.chdir(self._root + "/root")
        if not os.path.isdir("sd-wan-edgev2"):
            sp = subprocess.run(["git", "clone", "https://github.com/vewe-richard/sd-wan-edgev2.git"])
        os.chdir(self._cwd)
        pass

    def pypackage(self):
        if os.path.isdir("/tmp/python-pytuntap-1.0.5"):
            return
        os.chdir("/tmp")
        sp = subprocess.run(["unzip", self._cwd + "/1046/setuptools-49.1.0.zip"])
        os.chdir("setuptools-49.1.0")
        sp = subprocess.run(["python3", "setup.py", "install"])

        os.chdir("/tmp")
        sp = subprocess.run(["tar", "xf", self._cwd + "/1046/python-pytuntap-1.0.5.tar.gz"])
        os.chdir("python-pytuntap-1.0.5")
        sp = subprocess.run(["python3", "setup.py", "install"])

        os.chdir("/tmp")
        sp = subprocess.run(["tar", "xf", self._cwd + "/1046/pyserial-3.4.tar.gz"])
        os.chdir("pyserial-3.4")
        sp = subprocess.run(["python3", "setup.py", "install"])

        os.chdir(self._cwd)
        pass

    def kernel(self):
        sp = subprocess.run(["unzip", "-o", "./1046/Image.zip", "-d", self._root + "/var/run/media/mmcblk0p2/boot/"])
        pass


    def edgepoll(self):
        cfgs = ["network.json", "5g.json"]
        for cfg in cfgs:
            sp = subprocess.run(["cp", "./1046/" + cfg, self._root + "/root/.sdwan/edgepoll/"])
        config = {
            "sn": str(random.randint(11100000, 11109999)),
            "type": "thinedge-5g",
            "name": "5g",
            "spec": "baicells-sd-wan-thinedge-5g.hw.v01",
            "sw": "thinedge-5g.v01",
            "sms": "58.251.8.132",
            "smsport": 8081,
            "publicip": "",
            "inputport": 11112,
            "timeout": 6
        }
        if not os.path.isfile(self._root + "/etc/sdwan/edge/config.json"):
            with open(self._root + "/etc/sdwan/edge/config.json", 'w') as json_file:
                json.dump(config, json_file)
        pass


if __name__ == "__main__":
    setup = Setup5GRouter()
    setup.wan()
    setup.git()
    setup.pypackage()
    setup.kernel()
    setup.edgepoll()
    print("cd to", setup._root, "/root/sd-wan-edgev2", ",run python3 install.py")
    pass

