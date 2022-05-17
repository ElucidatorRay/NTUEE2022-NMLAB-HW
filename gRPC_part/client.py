import sys
import argparse

import grpc
import ChangeAlg_pb2
import ChangeAlg_pb2_grpc


def main(args):
    host = f"{args['ip']}:{args['port']}"
    print(host)
    with grpc.insecure_channel(host) as channel:
        stub = ChangeAlg_pb2_grpc.ChangeAlgStub(channel)

        request = ChangeAlg_pb2.Request()
        request.AlgNo = args['AlgNo']

        response = stub.GetServerResponse(request)
        print(response.AlgNo)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--ip", type=str, default="192.168.55.1")
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument("--AlgNo", type=int, default=1)
    args = vars(parser.parse_args())
    main(args)
