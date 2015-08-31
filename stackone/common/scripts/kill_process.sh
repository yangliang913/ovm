#!/bin/bash

kill_process()
{
  pid=$1
  time_count=$2
  while [ $time_count -ge 0 ]
  do
       if [ -d /proc/$pid ]; then
           kill -9 $1
           sleep 1
       else
           break
       fi
  done
}

kill_process $1 $2
