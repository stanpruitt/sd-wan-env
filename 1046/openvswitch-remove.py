from pathlib import Path
import subprocess
if __name__ == "__main__":
    with open("openvswitch-filelist") as f:
        for l in f.readlines():
            if "openvswitch" in l or "ovs" in l:
                l = l.strip()
                myfile = Path(l)
                print(l)
                if myfile.exists():
                    cmd = ["rm", "-f", l]
                    print(cmd)
                    sp = subprocess.run(cmd)
                    if sp.returncode != 0:
                        print("delete", l, "failed")
                if "/usr/" in l:
                    l2 = l.replace("/usr/", "/usr/local/", 1)
                    myfile = Path(l2)
                    if myfile.exists():
                        cmd = ["rm", "-f", l2]
                        print(cmd)
                        sp = subprocess.run(cmd)
                        if sp.returncode != 0:
                            print("delete", l2, "failed")
                else:
                    continue
            else:
                pass
    pass