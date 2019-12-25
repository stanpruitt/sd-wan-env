import subprocess
import vdevs.vswitch


class vGateway(vdevs.vswitch.vSwitch):
    def set_dhcpserver(self, cfgdata):
        sp  = subprocess.run(["ps", "-f", "-C", "docker"], stdout=subprocess.PIPE)
        lines = sp.stdout.splitlines()
        for line in lines:
            lstr = line.decode()
            if self._name in lstr and "docker" in lstr and "dhcpd" in lstr:
                print("dhcpserver has already started")
                return
        self._dhcpserverdata = cfgdata
        gw = self.parsegw(self._dhcpserverdata)
        sp = subprocess.run(["ifconfig", self._name, gw+"/24", "up"])
        sp = subprocess.Popen(["docker", "run", "--rm", "--init", "--name", self._name, "--net", "host", "-v", cfgdata+":/data", "networkboot/dhcpd", self._name])
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

    def remove_dhcpserver(self):
        sp  = subprocess.run(["docker", "stop", self._name])
        pass
    #sudo iptables -t nat -A POSTROUTING -s 10.27.1.0/24 ! -o public -j MASQUERADE
    #
    def set_NAT(self, gw):
        sp = subprocess.run(["iptables", "-t", "nat", "-L", "POSTROUTING", "-v", "--line-numbers"], stdout=subprocess.PIPE)
        lines = sp.stdout.splitlines()
        exist = False
        for line in lines:
            lstr = line.decode()
            if self._name in lstr and "MASQUERADE" in lstr:
                exist = True
        if not exist:
            subprocess.run(["iptables", "-t", "nat", "-A", "POSTROUTING", "-s", gw + "/24", "!", "-o", self._name, "-j", "MASQUERADE"])

        exist = False
        sp = subprocess.run(["iptables", "-L", "FORWARD", "-v", "--line-numbers"], stdout=subprocess.PIPE)
        lines = sp.stdout.splitlines()
        for line in reversed(lines):
            lstr = line.decode()
            if self._name in lstr and "ACCEPT" in lstr:
                exist = True
        if not exist:
            subprocess.run(["iptables", "-A", "FORWARD", "-i", self._name, "-j", "ACCEPT"])
            subprocess.run(["iptables", "-A", "FORWARD", "-o", self._name, "-j", "ACCEPT"])
        pass

    def remove_NAT(self):
        sp = subprocess.run(["iptables", "-t", "nat", "-L", "POSTROUTING", "-v", "--line-numbers"], stdout=subprocess.PIPE)
        lines = sp.stdout.splitlines()
        for line in lines:
            lstr = line.decode()
            if self._name in lstr and "MASQUERADE" in lstr:
                num = (lstr.split()[0])
                subprocess.run(["iptables", "-t", "nat", "-D", "POSTROUTING", num])

        sp = subprocess.run(["iptables", "-L", "FORWARD", "-v", "--line-numbers"], stdout=subprocess.PIPE)
        lines = sp.stdout.splitlines()
        for line in reversed(lines):
            lstr = line.decode()
            if self._name in lstr and "ACCEPT" in lstr:
                num = (lstr.split()[0])
                subprocess.run(["iptables", "-D", "FORWARD", num])
        pass
