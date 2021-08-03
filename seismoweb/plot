#!/bin/bash

while true; do
#  echo 'set yrange [-0.1:0.1]'
  echo "p '-' u 1 w l t 'x', '-' u 2 w l t 'y', '-' u 3 w l t 'z'"
  ./getadc.py $@
  echo -e "e\n"
#  sleep 0.2
done | gnuplot
