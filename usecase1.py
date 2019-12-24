import baseusecase
import vdevs.vswitch

class UseCase1(baseusecase.BaseUseCase):
    def __init__(self):
        super().__init__()
        self._localswitch = vdevs.vswitch.vSwitch("local")
        pass

    def start(self):
        self._localswitch.start()
        self._localswitch.addintf("tap0")
        self._localswitch.addintf("tap1")
        print (self._localswitch.getintfs())
        pass

    def stop(self):
        self._localswitch.stop()
        pass

    def remove(self):
        self._localswitch.remove()
        pass