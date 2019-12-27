import baseusecase
import vdevs.vswitch
import vdevs.vgateway
import vdevs.vm
import vdevs.vhost

class UseCase1(baseusecase.BaseUseCase):
    def __init__(self):
        super().__init__()
        self._localswitch = vdevs.vswitch.vSwitch("local")
        self._publicgw = vdevs.vgateway.vGateway("public")

        imagebase = "/home/richard/data/kvm/sd-wan/"

        self._vmnat = vdevs.vm.VM("nat")
        self._vmnat.config(imagebase + "nat.qcow2", m=1024)
        self._vmnat.addnetwork(["-netdev", "user,id=net0001,hostfwd=tcp::10001-:22",
                                "-device", "e1000,netdev=net0001,mac=52:54:98:76:00:01"])
        self._vmnat.addnetwork(["-netdev", "tap,id=net0002,ifname=tap0002",
                                "-device", "e1000,netdev=net0002,mac=52:54:98:76:00:02"])
        self._vmnat.addnetwork(["-netdev", "tap,id=net0003,ifname=tap0003",
                                "-device", "e1000,netdev=net0003,mac=52:54:98:76:00:03"])

        self._vmthinedge = vdevs.vm.VM("thinedge")
        self._vmthinedge.config(imagebase + "thinedge.qcow2", m=1024)
        self._vmthinedge.addnetwork(["-netdev", "user,id=net0101,hostfwd=tcp::10101-:22",
                                "-device", "e1000,netdev=net0101,mac=52:54:98:76:01:01"])
        self._vmthinedge.addnetwork(["-netdev", "tap,id=net0102,ifname=tap0102",
                                "-device", "e1000,netdev=net0102,mac=52:54:98:76:01:02"])
        self._vmthinedge.addnetwork(["-netdev", "tap,id=net0103,ifname=tap0103",
                                "-device", "e1000,netdev=net0103,mac=52:54:98:76:01:03"])

        self._vmfatedge = vdevs.vm.VM("fatedge")
        self._vmfatedge.config(imagebase + "fatedge.qcow2", m=1024)
        self._vmfatedge.addnetwork(["-netdev", "user,id=net0201,hostfwd=tcp::10201-:22",
                                "-device", "e1000,netdev=net0201,mac=52:54:98:76:02:01"])
        self._vmfatedge.addnetwork(["-netdev", "tap,id=net0202,ifname=tap0202",
                                "-device", "e1000,netdev=net0202,mac=52:54:98:76:02:02"])
        pass

    def link(self):
        self._localswitch.addintf("tap0003")
        self._publicgw.addintf("tap0002")
        self._localswitch.addintf("tap0103")
        self._publicgw.addintf("tap0202")

        netdata = "/home/richard/PycharmProjects/sd-wan-env/data/dhcpd/data/"
        self._publicgw.set_dhcpserver(netdata)
        gw = self.parsegw(netdata)
        self._publicgw.set_NAT(gw)
        pass

    def test(self):
#        self._publicgw.remove_dhcpserver()
#        self._publicgw.remove_NAT()
        pass

    def start(self):
        self._localswitch.start()
        print (self._localswitch.getintfs())

        self._publicgw.start()

        self._vmnat.start()
        self._vmthinedge.start()
        self._vmfatedge.start()

        pass

    def stop(self):
        self._localswitch.stop()
        self._publicgw.stop()
        self._vmnat.stop()
        self._vmthinedge.stop()
        self._vmfatedge.stop()
        pass

    def remove(self):
        self._publicgw.remove_dhcpserver()
        self._publicgw.remove_NAT()

        self._localswitch.remove()
        self._publicgw.remove()
        self._vmnat.remove()
        self._vmthinedge.remove()
        self._vmfatedge.remove()
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

    def addhost(self, intfname, hostname):
        host = vdevs.vhost.vHost(intfname, hostname)
        host.start()
        pass

    def removehost(self, intfname, hostname):
        host = vdevs.vhost.vHost(intfname, hostname)
        host.remove()
        pass