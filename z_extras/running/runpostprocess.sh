#!/bin/bash

id="062.mp4"

python3 VideoBurstingBubble_facets.py 
cd Video
ffmpeg -framerate 35 -pattern_type glob -i '*.png' -vf "pad=ceil(iw/2)*2:ceil(ih/2)*2" -c:v libx264 -r 30 -pix_fmt yuv420p $id

