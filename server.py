from concurrent import futures
import grpc
import psi_pb2
import psi_pb2_grpc
import time
import threading
import random
import numpy as np
import torch
from torch.utils.data import Dataset
import hashlib
from google.protobuf import empty_pb2

class PSIServicer(psi_pb2_grpc.DataTransferServicer):
    def __init__(self, dataset):
        self.dataset = dataset
        self.domain = {"p": 9223372036854771239, "q": 4611686018427385619}
        self.private_key = random.randint(1, self.domain["q"]-1)
        self.X = None
        self.Y = None
        self.Y_sorted = None

    def _encrypt(self, array):
        result = np.array([pow(int(x), self.private_key, self.domain["p"]) for x in array], dtype=np.uint64)
        return result
    
    def PrepareForPSI(self, request, context):
        index = request.index
        self.X = np.empty(len(self.dataset), dtype=np.uint64)
        for i, sample in enumerate(self.dataset):
            value = sample[index]
            if isinstance(value, torch.Tensor):
                value = str(value.numpy())
            else:
                value = str(value)
            hash_value = int.from_bytes(hashlib.sha1(value.encode("utf-8")).digest(), byteorder="big")
            self.X[i] = hash_value & 0xFFFFFFFFFFFFFFFF
        
        print(f"Hash applied to column {index}.")

        self.Y = self._encrypt(self.X)
        self.Y_sorted = np.sort(self.Y)

        print("Hashes encrypted and sorted!")
        print(f"Encrypted and sorted hashes: {self.Y_sorted}")
        return empty_pb2.Empty()
    
    
def serve(dataset, port):
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    psi_pb2_grpc.add_DataTransferServicer_to_server(PSIServicer(dataset), server)
    server.add_insecure_port(f'[::]:{port}')
    server.start()
    print(f'Server started on port {port}')
    server.wait_for_termination()

class DNIDataset(Dataset):
    def __init__(self, datos_dni, otros_datos, etiquetas):
        self.datos_dni = datos_dni
        self.otros_datos = otros_datos
        self.etiquetas = etiquetas
        
    def __len__(self):
        return len(self.datos_dni)
    
    def __getitem__(self, idx):
        dni = self.datos_dni[idx]
        otro_dato = self.otros_datos[idx]
        etiqueta = self.etiquetas[idx]
        return dni, otro_dato, etiqueta


if __name__ == '__main__':
    # Dataset 1
    datos_dni_1 = ["12345678A", "87654321B", "54321678C", "67891234D"]
    otros_datos_1 = ["datos1", "datos2", "datos3", "datos4"]
    etiquetas_1 = torch.tensor([0, 1, 2, 3])
    dni_dataset_1 = DNIDataset(datos_dni_1, otros_datos_1, etiquetas_1)

    # Dataset 2
    datos_dni_2 = ["67891234D", "22222222Y", "54321678C", "11111111X"]
    otros_datos_2 = ["datos5", "datos6", "datos7", "datos8"]
    etiquetas_2 = torch.tensor([3, 1, 5, 6])
    dni_dataset_2 = DNIDataset(datos_dni_2, otros_datos_2, etiquetas_2)

    # Levantar dos servidores en diferentes puertos
    import multiprocessing
    p1 = multiprocessing.Process(target=serve, args=(dni_dataset_1, 50051))
    p2 = multiprocessing.Process(target=serve, args=(dni_dataset_2, 50052))

    p1.start()
    p2.start()

    p1.join()
    p2.join()