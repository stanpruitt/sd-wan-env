import vdevs.basevdev
import subprocess
'''
sudo qemu-system-x86_64 -enable-kvm -nographic -m 1024 
-netdev tap,id=net0000 -device e1000,netdev=net0000,mac=52:54:98:76:00:00 
-netdev user,id=net0001,hostfwd=tcp::10022-:22 -device e1000,netdev=net0001,mac=52:54:98:76:00:01 
data/kvm/sd-wan/ubuntu18.04-lts-base.qcow2
"
'''

class VM(vdevs.basevdev.BasevDev):
    def __init__(self, name):
        self._name = name
        self._networks = []
        self._m = 512
        self._image = ""
        self._proc = None

    def config(self, image, m=512):
        self._m = m
        self._image = image

    def addnetwork(self, newnet):
        self._networks.append(newnet)
        pass

    def start(self):
        # try access at first
        pass

    def create(self):
        cmd = []
        cmd.extend(["qemu-system-x86_64", "-enable-kvm", "-nographic"])
        cmd.extend(["-m", str(self._m)])
        for net in self._networks:
            cmd.extend(net)
        cmd.append(self._image)
        print (cmd)
        proc = subprocess.Popen(cmd, stdout=subprocess.DEVNULL)
        self._proc = proc
        pass

    def remove(self):

        pass