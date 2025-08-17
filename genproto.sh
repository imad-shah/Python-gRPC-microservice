#!/bin/bash

python -m grpc_tools.protoc --proto_path=. --python_out=.proto --pyi_out=.proto --grpc_python_out=.proto library.proto