# NTUEE222-NMLAB HW

## gRPC_part
* server.py
* client.py
* ChangeAlg_pb2.py
* ChangeAlg_pb2_grpc.py
* simRTMP.py
* Alg.txt

## Gstreamer_part
* RTMP_server.py


## How to use
run gRPC server and RTMP server in jetson nano
```sh
python3 server.py
python3 RTMP_server.py
```
run ffplay in laptop
```
ffplay -fflags nobuffer rtmp://192.168.55.1/rtmp/live
```
use client.py to change used vision algorithm
```
python3 client.py --AlgNo AlgorithmNumber
```
