#!/bin/bash

for i in *.png
do
echo "Prcoessing image $i ..."
convert -thumbnail 200 $i $i
done
