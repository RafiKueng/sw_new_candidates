#!/bin/bash



rm times.log

mkdir -p output
cd output


for fullfile in ../cfg/[0-9A-Z]*.cfg; do
    filename=$(basename "$fullfile")
    extension="${filename##*.}"
    mid="${filename%.*}"
    
    echo ${mid}
    
    mkdir -p "../tmp_media/${mid}/"
    
    /usr/bin/time --format='%e' --output="../times/${mid}_time.log" ../../../glass/run_glass -t2 "../cfg/${filename}"
    #break
done

cd ..

for timefile in times/*.log; do
    filename=$(basename "$fullfile")
    extension="${filename##*.}"
    mid="${filename%.*}"
    
    echo ${timefile}
    
    cat ${timefile} >> times.log
    

    #break
done

awk '{s+=$1} END {print "final time: " s}' times.log
