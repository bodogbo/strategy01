#!/bin/bash

./strategy01 -grid   uniperp-grid.csv 2>output.log &
pid=$!
echo $pid > strategy01.pid

