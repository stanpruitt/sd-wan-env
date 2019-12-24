import subprocess
import vdevs.basevdev


class vSwitch(vdevs.basevdev.BasevDev):
    def __init__(self, name):
        self._name = name
        self._ifs = set()

    def start(self):
        try:
            self.access(self._name)
        except vdevs.basevdev.ExceptionNotExist:
            self.create(self._name)
        pass

    def remove(self):
        sp = subprocess.run(["ip", "link", "show", self._name, "type", "bridge"])
        if sp.returncode == 0:
            sp = subprocess.run(["ip", "link", "delete", self._name, "type", "bridge"])
        pass

    def addintf(self, intf):
        if len(self._ifs) == 0:
            self.access(self._name)
        if intf in self._ifs:
            return
        sp = subprocess.run(["brctl", "addif", self._name, intf])
        if sp.returncode != 0:
            raise Exception("can not add interface to bridge")
        self._ifs.add(intf)
        pass

    def getintfs(self):
        return self._ifs

# inner
    def create(self, name):
        sp = subprocess.run(["ip", "link", "add", name, "type", "bridge"])
        pass

    def access(self, name):
        sp = subprocess.run(["ip", "link", "show", name, "type", "bridge"])
        if sp.returncode != 0:
            raise vdevs.basevdev.ExceptionNotExist
        sp = subprocess.run(["brctl", "show", name], stdout=subprocess.PIPE)
        lines = sp.stdout.splitlines()
        self._ifs = set()
        for line in lines[1:]:
            items = line.split()
            if len(items) == 4:
                self._ifs.add(items[3].decode())
            elif len(items) == 1:
                self._ifs.add(items[0].decode())
        pass

