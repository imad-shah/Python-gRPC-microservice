#!/bin/bash

python -m grpc.tools.protoc --proto_path=. --python_out=. --grpc_python_out=. proto/library.proto