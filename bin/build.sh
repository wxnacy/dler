#!/usr/bin/env bash

bname=`git branch | grep '*' | awk '{print $2}'`
bin_name=dler
if [[ $bname != 'master' ]]
then
    bin_name=dler-${bname}
fi

cd cmd/dler && go build && mv dler $(go env GOPATH)/bin/$bin_name && cd --
