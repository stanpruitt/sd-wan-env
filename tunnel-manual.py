import argparse
import baseusecase
import vdevs.vgateway
import subprocess

class ThinEdge(baseusecase.BaseUseCase):
    def __init__(self):
        super().__init__()
        self._gw = vdevs.vgateway.vGateway("gw2")
        pass

    def start(self):
        self._gw.start()
        sp = subprocess.run(["ip", "tuntap", "add", "mode", "tun", "tun13"])
        if sp.returncode != 0:
            raise Exception("can not create tuntap")
        sp = subprocess.run(["ip", "addr", "add", "10.10.0.100/24", "dev", "tun13"])
        sp = subprocess.run(["ip", "link", "set", "tun13", "up"])
#        self._gw.addintf("tun13")
        sp = subprocess.run(["/home/richard/work/diyvpn/simpletun", "-i", "tun13", "-c", "10.27.1.101", "-p", "5555", "-d"])
        pass

    def test(self):
        print("good")
        pass

    def remove(self):
        sp = subprocess.run(["ip", "tuntap", "del", "mode", "tun", "tun13"])
        self._gw.remove()
        pass


class FatEdge(baseusecase.BaseUseCase):
    def __init__(self):
        super().__init__()
        self._gw = vdevs.vgateway.vGateway("gw")
        pass

    def start(self):
        self._gw.start()
        sp = subprocess.run(["ip", "tuntap", "add", "mode", "tun", "tun13"])
        if sp.returncode != 0:
            raise Exception("can not create tuntap")
        sp = subprocess.run(["ip", "addr", "add", "10.10.0.1/24", "dev", "tun13"])
#        self._gw.addintf("tun13")
        sp = subprocess.run(["/home/richard/work/diyvpn/simpletun", "-i", "tun13", "-s", "-p", "5555", "-d"])
        pass

    def test(self):
        print("good")
        pass

    def remove(self):
        sp = subprocess.run(["ip", "tuntap", "del", "mode", "tun", "tun13"])
        self._gw.remove()
        pass


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("host", help="thinedge | fatedge")
    parser.add_argument("command", help="start remove test")
    args = parser.parse_args()

    if args.host == "thinedge":
        usecase = ThinEdge()
    else:
        usecase = FatEdge()

    if args.command == "start":
        usecase.start()
    elif args.command == "remove":
        usecase.remove()
    elif args.command == "test":
        usecase.test()
    else:
        print ("unknown command")
