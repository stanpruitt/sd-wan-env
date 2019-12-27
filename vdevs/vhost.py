import vdevs.basevdev
import vdevs.vswitch
import subprocess

class vHost(vdevs.basevdev.BasevDev):
    def __init__(self, nic, hostname):
        self._attached_to = nic
        self._hostname = hostname
        self._name = hostname + "_" + nic
        self._switch = vdevs.vswitch.vSwitch(self._name)
        self._vethhost = "v_"+self._name
        self._vethpeer = "vp_"+self._name
        pass

    def start(self):
        self._switch.start()
        # check if host is running
        pid = self.pid()
        if pid == None:
            # run the docker
            sp = subprocess.run(["docker", "run", "-d", "--net", "none", "--rm", "--name", self._name, "sd-wan/ubt_iptools", "sleep", "1d"])
            pid = self.pid()

        if pid == None:
            raise Exception("can not launch docker")

        sp = subprocess.run(["mkdir", "-p", "/var/run/netns"])
        sp = subprocess.run(["ln", "-sf", "/proc/" + pid + "/ns/net", "/var/run/netns/" + self._name])
        sp = subprocess.run(["ip", "link", "add", self._vethhost, "type", "veth", "peer", "name", self._vethpeer])
        sp = subprocess.run(["ip", "link", "set", self._vethpeer, "netns", self._name])
        sp = subprocess.run(["ip", "netns", "exec", self._name, "ip", "link", "set", self._vethpeer, "up"])
        self._switch.addintf(self._attached_to)
        self._switch.addintf(self._vethhost)
        print("run dhcpclient to descover ip address")
        sp = subprocess.run(["ip", "netns", "exec", self._name, "dhclient", self._vethpeer])

        pass

    def remove(self):
        self._switch.remove()
        sp = subprocess.run(["ip", "link", "delete", self._vethhost, "type", "veth"])
        #remove namespace link
        sp = subprocess.run(["unlink", "/var/run/netns/" + self._name])
        sp = subprocess.run(["docker", "ps"], stdout=subprocess.PIPE)
        lines = sp.stdout.splitlines()
        for line in lines:
            if self._name in line.decode():
                cid = line.decode().split()[0]
                sp = subprocess.run(["docker", "stop", cid])
        pass

    def pid(self):
        sp = subprocess.run(["docker", "ps", "-a"], stdout=subprocess.PIPE)
        lines = sp.stdout.splitlines()
        for line in lines:
            if self._name in line.decode():
                items = line.decode().split()
                dockerid = items[0]
                sp = subprocess.run(["docker", "inspect", "-f", "'{{.State.Pid}}'", dockerid], stdout=subprocess.PIPE)
                return sp.stdout.decode().strip().strip("'")

        return None

