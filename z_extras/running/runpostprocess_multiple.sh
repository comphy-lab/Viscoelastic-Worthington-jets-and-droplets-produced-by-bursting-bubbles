#!/bin/bash

start=271
end=70

for i in {0..5}; 
do 
cd  $(printf "%03d" $((start+8*i)))
python3 VideoBurstingBubble_facets.py &
cd ../

cd  $(printf "%03d" $((start+8*i+1)))
python3 VideoBurstingBubble_facets.py &
cd ../

cd  $(printf "%03d" $((start+8*i+2)))
python3 VideoBurstingBubble_facets.py &
cd ../

cd  $(printf "%03d" $((start+8*i+3)))
python3 VideoBurstingBubble_facets.py &
cd ../

cd  $(printf "%03d" $((start+8*i+4)))
python3 VideoBurstingBubble_facets.py &
cd ../

cd  $(printf "%03d" $((start+8*i+5)))
python3 VideoBurstingBubble_facets.py &
cd ../

cd  $(printf "%03d" $((start+8*i+6)))
python3 VideoBurstingBubble_facets.py &
cd ../

cd  $(printf "%03d" $((start+8*i+7)))
python3 VideoBurstingBubble_facets.py &
cd ../

wait

cd  $(printf "%03d" $((start+8*i)))
cd Video
ffmpeg -framerate 35 -pattern_type glob -i '*.png' -vf "pad=ceil(iw/2)*2:ceil(ih/2)*2" -c:v libx264 -r 30 -pix_fmt yuv420p $(printf "%03d" $((start+8*i))).mp4
cd ../../

cd  $(printf "%03d" $((start+8*i+1)))
cd Video
ffmpeg -framerate 35 -pattern_type glob -i '*.png' -vf "pad=ceil(iw/2)*2:ceil(ih/2)*2" -c:v libx264 -r 30 -pix_fmt yuv420p $(printf "%03d" $((start+8*i+1))).mp4
cd ../../

cd  $(printf "%03d" $((start+8*i+2)))
cd Video
ffmpeg -framerate 35 -pattern_type glob -i '*.png' -vf "pad=ceil(iw/2)*2:ceil(ih/2)*2" -c:v libx264 -r 30 -pix_fmt yuv420p $(printf "%03d" $((start+8*i+2))).mp4
cd ../../

cd  $(printf "%03d" $((start+8*i+3)))
cd Video
ffmpeg -framerate 35 -pattern_type glob -i '*.png' -vf "pad=ceil(iw/2)*2:ceil(ih/2)*2" -c:v libx264 -r 30 -pix_fmt yuv420p $(printf "%03d" $((start+8*i+3))).mp4
cd ../../

cd  $(printf "%03d" $((start+8*i+4)))
cd Video
ffmpeg -framerate 35 -pattern_type glob -i '*.png' -vf "pad=ceil(iw/2)*2:ceil(ih/2)*2" -c:v libx264 -r 30 -pix_fmt yuv420p $(printf "%03d" $((start+8*i+4))).mp4
cd ../../

cd  $(printf "%03d" $((start+8*i+5)))
cd Video
ffmpeg -framerate 35 -pattern_type glob -i '*.png' -vf "pad=ceil(iw/2)*2:ceil(ih/2)*2" -c:v libx264 -r 30 -pix_fmt yuv420p $(printf "%03d" $((start+8*i+5))).mp4
cd ../../

cd  $(printf "%03d" $((start+8*i+6)))
cd Video
ffmpeg -framerate 35 -pattern_type glob -i '*.png' -vf "pad=ceil(iw/2)*2:ceil(ih/2)*2" -c:v libx264 -r 30 -pix_fmt yuv420p $(printf "%03d" $((start+8*i+6))).mp4
cd ../../

cd  $(printf "%03d" $((start+8*i+7)))
cd Video
ffmpeg -framerate 35 -pattern_type glob -i '*.png' -vf "pad=ceil(iw/2)*2:ceil(ih/2)*2" -c:v libx264 -r 30 -pix_fmt yuv420p $(printf "%03d" $((start+8*i+7))).mp4
cd ../../
done


