import json
import traceback
import sys
import subprocess

def loadcfg():
    with open("ns4tunnels.json") as json_file:
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
    run(["ip", "link", "set", veth["veth"], "netns", veth["namespace"]])
    run(["ip", "link", "set", veth["pname"], "netns", veth["pnamespace"]])
    run(["ip", "netns", "exec", veth["namespace"], "ip", "link", "set", veth["veth"], "up"])
    run(["ip", "netns", "exec", veth["namespace"], "ip", "addr", "add", veth["ip"], "dev", veth["veth"]])
    run(["ip", "netns", "exec", veth["pnamespace"], "ip", "link", "set", veth["pname"], "up"])
    run(["ip", "netns", "exec", veth["pnamespace"], "ip", "addr", "add", veth["peerip"], "dev", veth["pname"]])

def create():
    nslist, vethlist = loadcfg()
    for ns in nslist:
        createns(ns)
    for veth in vethlist:
        createveth(veth)
    pass

def destroy():
    run(["ip", "-all", "netns", "delete"])
    sp = subprocess.run(["ip", "link", "show", "type", "veth"], stdout=subprocess.PIPE)
    for l in sp.stdout.decode().splitlines():
        item = l.split()[1]
        peer = item.split("@")[0]
        if "vethp" in peer:
            run(["ip", "link", "delete", peer, "type", "veth"])
    pass

if __name__ == "__main__":
    if sys.argv[1] == "create":
        destroy()
        create()
    elif sys.argv[1] == "destroy":
        destroy()
    else:
        print("Usage: ns4tunnels.py create|destroy")



