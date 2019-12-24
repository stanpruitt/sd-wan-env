import baseusecase
import vdevs.vswitch
import vdevs.vgateway
import vdevs.vm

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
        self._vmnat.addnetwork(["-netdev", "tap,id=net0002",
                                "-device", "e1000,netdev=net0002,mac=52:54:98:76:00:02"])
        self._vmnat.addnetwork(["-netdev", "tap,id=net0003",
                                "-device", "e1000,netdev=net0003,mac=52:54:98:76:00:03"])

        pass

    def start(self):
        self._localswitch.start()
        self._localswitch.addintf("tap0")
        self._localswitch.addintf("tap1")
        print (self._localswitch.getintfs())

        self._publicgw.start()

        self._vmnat.start()

        pass

    def stop(self):
        self._localswitch.stop()
        self._publicgw.stop()
        self._vmnat.stop()
        pass

    def remove(self):
        self._localswitch.remove()
        self._publicgw.remove()
        self._vmnat.remove()
        pass