import sys
import argparse

import grpc
from concurrent import futures
import ChangeAlg_pb2
import ChangeAlg_pb2_grpc


class ChangeAlgServicer(ChangeAlg_pb2_grpc.ChangeAlgServicer):

    def __init__(self):
        pass

    def GetServerResponse(self, request, context):
        N = request.AlgNo
        self.ChangeAlg(N)

        response = ChangeAlg_pb2.Response()
        response.AlgNo = N

        return response

    def ChangeAlg(self, n):
        with open('Alg.txt', 'w') as f:
            f.write(str(n))
        return n

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--ip", default="0.0.0.0", type=str)
    parser.add_argument("--port", default=8000, type=int)
    args = vars(parser.parse_args())

    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    servicer = ChangeAlgServicer()
    ChangeAlg_pb2_grpc.add_ChangeAlgServicer_to_server(servicer, server)

    try:
        server.add_insecure_port(f"{args['ip']}:{args['port']}")
        server.start()
        print(f"Run gRPC Server at {args['ip']}:{args['port']}")
        server.wait_for_termination()
    except KeyboardInterrupt:
        pass
