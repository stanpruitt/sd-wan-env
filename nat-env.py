import argparse
import baseusecase
import vdevs.vgateway

class UseCase(baseusecase.BaseUseCase):
    def __init__(self):
        super().__init__()
        self._publicgw = vdevs.vgateway.vGateway("gw")
        pass

    def link(self):
        self._publicgw.addintf("ens5")

        netdata = "/home/richard/sd-wan/dhcpd/data/"
        self._publicgw.set_dhcpserver(netdata)
        gw = self.parsegw(netdata)
        self._publicgw.set_NAT(gw)
        pass

    def test(self):
        pass

    def start(self):
        self._publicgw.start()
        pass

    def stop(self):
       pass

    def remove(self):
        self._publicgw.remove_dhcpserver()
        self._publicgw.remove_NAT()
        self._publicgw.remove()
        pass

    def parsegw(self, cfgdata):
        cfg = cfgdata + "/dhcpd.conf"
        with open(cfg) as f:
            lines = f.readlines()
            for line in lines:
                if "option" not in line or "routers" not in line:
                    continue
                items = line.split()
                return (items[2].strip(";").strip())
        raise Exception("invalid dhcp server config file")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("command", help="start stop remove test graph")
    args = parser.parse_args()

    usecase = UseCase()
    if args.command == "start":
        usecase.start()
    elif args.command == "stop":
        usecase.stop()
    elif args.command == "remove":
        usecase.remove()
    elif args.command == "test":
        usecase.test()
    elif args.command == "graph":
        usecase.graph()
    elif args.command == "link":
        usecase.link()
    else:
        print ("unknown command")
