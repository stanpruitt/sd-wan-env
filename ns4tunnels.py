#usage
# python3 ns4tunnels.py genconfigs ns4virtunnels.json
# python3 ns4tunnels.py create ns4virtunnels.json
# python3 ns4tunnels.py start ns4virtunnels.json
# python3 ns4tunnels.py stop ns4virtunnels.json
# python3 ns4tunnels.py destroy ns4virtunnels.json

import json
import traceback
import sys
import subprocess
import time
import os

def loadcfg(cfg):
    with open(cfg) as json_file:
        data = json.load(json_file)
    nslist = []
    vethlist = []
    for d in data:
        try:
            d["veth"]
            vethlist.append(d)
        except:
            nslist.append(d)
            pass
    return nslist, vethlist

def run(args):
    print(args)
    subprocess.run(args)

def run1(args):
    print(args)


def split(var):
    items = var.split(":")
    name = items[0]
    ip = items[1]
    return name, ip

def createtuntap(ns, tap):
    name, ip = split(tap)
    if "tap" in name:
        mode = "tap"
    elif "tun" in name:
        mode = "tun"
    else:
        raise

    run(["ip", "netns", "exec", ns, "ip", "tuntap", "add", "mode", mode, name])
    run(["ip", "netns", "exec", ns, "ip", "link", "set", name, "up"])
    run(["ip", "netns", "exec", ns, "ip", "addr", "add", ip, "dev", name])

def createns(ns):
    nsname = ns["namespace"]
    run(["ip", "netns", "add", nsname])
    for tap in ns["tap"]:
        createtuntap(nsname, tap)
    for tun in ns["tun"]:
        createtuntap(nsname, tun)

def createveth(veth):
    run(["ip", "link", "add", veth["veth"], "type", "veth", "peer", "name", veth["pname"]])
    if veth["namespace"]:
        run(["ip", "link", "set", veth["veth"], "netns", veth["namespace"]])
    run(["ip", "link", "set", veth["pname"], "netns", veth["pnamespace"]])
    if veth["namespace"]:
        run(["ip", "netns", "exec", veth["namespace"], "ip", "link", "set", veth["veth"], "up"])
        run(["ip", "netns", "exec", veth["namespace"], "ip", "addr", "add", veth["ip"], "dev", veth["veth"]])
    else:
        run(["ip", "link", "set", veth["veth"], "up"])
        run(["ip", "addr", "add", veth["ip"], "dev", veth["veth"]])
    run(["ip", "netns", "exec", veth["pnamespace"], "ip", "link", "set", veth["pname"], "up"])
    run(["ip", "netns", "exec", veth["pnamespace"], "ip", "addr", "add", veth["peerip"], "dev", veth["pname"]])

def create(cfg):
    nslist, vethlist = loadcfg(cfg)
    for ns in nslist:
        createns(ns)
    for veth in vethlist:
        createveth(veth)
    pass

    run(["brctl", "addbr", "br-119"])
    for veth in vethlist:
        if "10.119.0" in veth["peerip"]:
            run(["brctl", "addif", "br-119", veth["veth"]])
    run(["ip", "link", "set", "br-119", "up"])
    run(["ip", "addr", "add", "10.119.0.1/24", "dev", "br-119"])

def destroy():
    run(["ip", "link", "set", "br-119", "down"])
    run(["brctl", "delbr", "br-119"])
    run(["ip", "-all", "netns", "delete"])
    sp = subprocess.run(["ip", "link", "show", "type", "veth"], stdout=subprocess.PIPE)
    for l in sp.stdout.decode().splitlines():
        item = l.split()[1]
        peer = item.split("@")[0]
        if "vethp" in peer:
            run(["ip", "link", "delete", peer, "type", "veth"])
    pass

def genconfigs(configfile):
    cfg = {
      "sn": "00020002",
      "type": "fatedge",
      "name": "sz-fatedge",
      "spec": "baicells-sd-wan-fatedge.hw.v02",
      "sw": "fatedge.v01",
      "sms": "127.0.0.1",
      "smsport": 8080,
      "publicip": "",
      "inputport": 11012,
      "timeout": 6,
      "map": ""
    }

    run(["mkdir", "configs"])
    run(["mkdir", "logs"])
    nslist, vethlist = loadcfg(configfile)
    for n in nslist:
        ns = n["namespace"]
        if ns[0] != "n" or len(ns) != 4:  # just create configs for these
            continue
        cfg["sn"] = "00090" + ns[1:]
        try:
            cfg["name"] = n["ename"] + "-" + ns
        except:
            cfg["name"] = ns
        print(cfg)
        cfg["sms"] = "10.119.0.1"
        md = dict()
        md["eth0"] = "10.119.0." + ns[1:]
        cfg["map"] = md
        with open("configs/" + ns + ".json", 'w') as json_file:
            json.dump(cfg, json_file)

def start(cfgfile):
    nslist, vethlist = loadcfg(cfgfile)
    splist = []
    for n in nslist:
        ns = n["namespace"]
        if ns[0] != "n" or len(ns) != 4: #just create configs for these
            continue
        import pathlib

        print(ns)
        cfg = (str(pathlib.Path(__file__).parent.absolute()) + "/configs/" + ns + ".json")
        log = (str(pathlib.Path(__file__).parent.absolute()) + "/logs/" + ns + ".log")
        '''
        export PYTHONPATH = "$PWD" && ip netns exec ns python3
        edgepoll/__main__.py - -config = configs/config101.json --loglevel=10
        '''
        env = dict()
        cwd = "/home/richard/PycharmProjects/sd-wan-edgev2"
        env["PYTHONPATH"] = cwd
        args = ["ip", "netns", "exec", ns, "python3", "edgepoll/__main__.py", "--config", cfg, "--loglevel=10", "--log", log]
        sp = subprocess.Popen(args, cwd=cwd, env=env)
        splist.append(sp)
    '''
    while True:
        s = input("exit?, Press Y")
        if len(s) < 1:
            continue
        if s[0] == "Y" or s[0] == "y":
            break
    for sp in splist:
        sp.kill()
    pass
    '''

def stop(cfg):
    sp = subprocess.run(["ps", "-ef"], stdout=subprocess.PIPE)
    for l in sp.stdout.decode().splitlines():
        if "edgepoll/__main__.py" in l:
            items = l.split()
            subprocess.run(["kill", "-9", items[1]])

if __name__ == "__main__":
    if sys.argv[1] == "create":
        destroy()
        time.sleep(2)
        create(sys.argv[2])
    elif sys.argv[1] == "destroy":
        destroy()
    elif sys.argv[1] == "genconfigs":
        genconfigs(sys.argv[2])
    elif sys.argv[1] == "start":
        start(sys.argv[2])
    elif sys.argv[1] == "stop":
        stop(sys.argv[2])
    else:
        print("Usage: ns4tunnels.py [create | destroy | stop | genconfigs | start] configfile")



