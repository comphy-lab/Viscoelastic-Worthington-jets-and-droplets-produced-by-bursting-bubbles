#!/bin/bash

start="219"
end="260"

for i in `seq $start $end`;
do
echo $i
mkdir -p $(printf "%03d" $i)
#scp -r *.c $i/
#scp -r Bo0.0010.dat dump  burstingBubbleVE_ElasticLimit_v3 get* VideoBurstingBubble*  $(printf "%03d" $i) 
#cp -r out_vol_time.py getdropstats* $i
cp out_jheight* getXheight* $i
done
