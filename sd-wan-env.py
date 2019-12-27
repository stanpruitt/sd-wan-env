import argparse
import baseusecase
import usecase1

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("command", help="start stop remove test graph addhost removehost")
    parser.add_argument("nic", nargs="?", help="attach host to a nic interface")
    parser.add_argument("hostname", nargs="?", help="the hostname to be removed from nic")
    args = parser.parse_args()

    usecase = usecase1.UseCase1()
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
    elif args.command == "addhost":
        usecase.addhost(args.nic, args.hostname)
    elif args.command == "removehost":
        usecase.removehost(args.nic, args.hostname)
    else:
        print ("unknown command")