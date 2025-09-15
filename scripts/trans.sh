#!/usr/bin/env bash

name=$1
toname=$name.mp4

ffmpeg -allowed_extensions ALL -i ${name} -bsf:a aac_adtstoasc -vcodec copy -c copy -crf 50 ${toname}
