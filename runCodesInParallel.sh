#!/bin/bash

# check that CLI inputs are there. 1 is compulsory. if 2 is not there, use 4 (default)
if [ $# -lt 1 ]; then
    echo "Usage: $0 <filename> [number_of_processes]"
    exit 1
fi

file=$1
NP=${2:-4}  # use 4 as default if not provided

mkdir -p $file
CC99='mpicc -std=c99' qcc -Wall -O2 -D_MPI=1 -I$PWD/src-local -I$PWD/../src-local -disable-dimensions $file.c -o $file/$file -lm
chmod +x $file/$file  # Ensure executable has proper permissions
cd $file
mpirun --allow-run-as-root -np $NP ./$file