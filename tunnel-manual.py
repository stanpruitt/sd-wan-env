import argparse
import baseusecase
import vdevs.vgateway
import subprocess

class ThinEdge(baseusecase.BaseUseCase):
    def __init__(self):
        super().__init__()
        self._gw = vdevs.vgateway.vGateway("gw")
        pass

    def start(self):
        self._gw.start()
        pass

    def test(self):
        print("good")
        pass

    def remove(self):
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
        sp = subprocess.run(["ifconfig", "tun13", "up"])
        self._gw.addintf("tun13")
        sp = subprocess.run(["simpletun", "-i", "tun13", "-s", "-p", "5555", "-d"])
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
