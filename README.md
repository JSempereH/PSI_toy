

```
python -m venv psi_toy
source psi_toy/bin/activate
```

```
pip install -r requirements.txt
```

In two different terminals:

```
python server.py
```

```
python client.py
```

If there are changes in psi.proto, it needs to be compiled:

```
python -m grpc_tools.protoc -I protos --python_out=. --grpc_python_out=. ./protos/psi.proto
```