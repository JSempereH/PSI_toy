import grpc
import asyncio
import psi_pb2
import psi_pb2_grpc
from google.protobuf import empty_pb2
from threading import RLock

lock = asyncio.Lock()

async def prepare_for_psi(stub, column_index):
    async with lock:
        request = psi_pb2.PrepareForPSIRequest(index = column_index)
        await stub.PrepareForPSI(request) # The response is Empty
        


async def main():
    server_1_address = 'localhost:50051'
    server_2_address = 'localhost:50052'

    column_index = 0

    async with grpc.aio.insecure_channel(server_1_address) as channel1, \
               grpc.aio.insecure_channel(server_2_address) as channel2:
        stub1 = psi_pb2_grpc.DataTransferStub(channel1)
        stub2 = psi_pb2_grpc.DataTransferStub(channel2)

        # Prepara PSI: each server hashes, encrypts and sorts its data
        await asyncio.gather(
            prepare_for_psi(stub1, column_index),
            prepare_for_psi(stub2, column_index)
        )

if __name__ == '__main__':
    asyncio.run(main())