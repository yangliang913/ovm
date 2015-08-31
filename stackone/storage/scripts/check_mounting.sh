#!/bin/bash

output=`mount | awk '{print $1"|"$3","}'`
echo "$output"
