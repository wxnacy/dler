#!/usr/bin/env bash

bname=`git branch | grep '*' | awk '{print $2}'`
bin_name=godler-${bname}

cd godler/cmd/godler && go build -o ${bin_name} && mv ${bin_name} $(go env GOPATH)/bin && cd ../..
