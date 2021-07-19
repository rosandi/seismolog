#!/bin/bash

while true; do
  #echo 'set yrange [-0.5:0.5]'
  echo "p '-' u 1 w l t 'x', '-' u 2 w l t 'y', '-' u 3 w l t 'z'"
  ./getadc.py n=100 g=6
  echo -e "e\n"
  sleep 0.2
done | gnuplot
