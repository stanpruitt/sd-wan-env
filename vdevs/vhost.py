import vdevs.basevdev
import subprocess

class vHost(vdevs.basevdev.BasevDev):
    def __init__(self, nic):
        self._attached_to = nic
        self._name = "host_" + nic
        pass

    def start(self):
        # check if host is running
        pid = self.pid()
        if pid == None:
            # run the docker
            sp = subprocess.run(["docker", "run", "-d", "--rm", "--name", self._name, "sd-wan/ubt_iptools", "sleep", "1d"])
            pid = self.pid()

        if pid == None:
            raise Exception("can not launch docker")

        sp = subprocess.run(["mkdir", "-p", "/var/run/netns"])
        sp = subprocess.run(["ln", "-sf", "/proc/" + pid + "/ns/net", "/var/run/netns/" + self._name])
        sp = subprocess.run(["ip", "link", "add", "v_"+self._name, "type", "veth", "peer", "name", "vp_"+self._name])
        sp = subprocess.run(["ip", "netns", "exec", self._name, "ip", "link", "set", "vp_"+self._name, "up"])
        pass

    def pid(self):
        sp = subprocess.run(["docker", "ps", "-a"], stdout=subprocess.PIPE)
        lines = sp.stdout.splitlines()
        for line in lines:
            if self._name in line.decode():
                items = line.decode().split()
                dockerid = items[0]
                sp = subprocess.run(["docker", "inspect", "-f", "'{{.State.Pid}}'", dockerid], stdout=subprocess.PIPE)
                return sp.stdout.decode().strip()

        return None

