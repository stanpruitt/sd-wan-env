import argparse
import baseusecase
import usecase1

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("command", help="start stop remove test graph")
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
    else:
        print ("unknown command")