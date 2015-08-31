#!/bin/bash 
#
#   stackone   -  Copyright (c) 2008 stackone Corp.
#   ======
#
# stackone is a Virtualization management tool with a graphical user
# interface that allows for performing the standard set of VM operations
# (start, stop, pause, kill, shutdown, reboot, snapshot, etc...). It
# also attempts to simplify various aspects of VM lifecycle management.
#
#
# This software is subject to the GNU General Public License, Version 2 (GPLv2)
# and for details, please consult it at:
#
#    http://www.gnu.org/licenses/old-licenses/gpl-2.0.txt
# 
#
# author : Jd <jd_jedi@users.sourceforge.net>
#

scriptName="${0##*/}"

declare -i DEFAULT_TIMEOUT=9
declare -i DEFAULT_INTERVAL=1
declare -i DEFAULT_DELAY=1

# Timeout.
declare -i timeout=DEFAULT_TIMEOUT
# Interval between checks if the process is still alive.
declare -i interval=DEFAULT_INTERVAL
# Delay between posting the SIGTERM signal and destroying the process by SIGKILL.
declare -i delay=DEFAULT_DELAY

function printUsage() {
    cat <<EOF

Synopsis
    $scriptName [-t timeout] [-i interval] [-d delay] [ -p pid_file ] command
    Execute a command with a time-out.
    Upon time-out expiration SIGTERM (15) is sent to the process. If SIGTERM
    signal is blocked, then the subsequent SIGKILL (9) terminates it.

    -t timeout
        Number of seconds to wait for command completion.
        Default value: $DEFAULT_TIMEOUT seconds.

    -i interval
        Interval between checks if the process is still alive.
        Positive integer, default value: $DEFAULT_INTERVAL seconds.

    -d delay
        Delay between posting the SIGTERM signal and destroying the
        process by SIGKILL. Default value: $DEFAULT_DELAY seconds.

    -p pid_file
        File to create with pid as content. (can be used for recovery)

As of today, Bash does not support floating point arithmetic (sleep does),
therefore all delay/time values must be integers.
EOF
}

# Options.
while getopts ":t:i:d:p:" option; do
    case "$option" in
        t) timeout=$OPTARG ;;
        i) interval=$OPTARG ;;
        d) delay=$OPTARG ;;
        p) pid_file=$OPTARG ;;
        *) printUsage; exit 1 ;;
    esac
done
shift $((OPTIND - 1))

cleanup()
{
    if [ -e $pid_file ]; then
       rm -f $pid_file
    fi
}

# $# should be at least 1 (the command to execute), however it may be strictly
# greater than 1 if the command itself has options.
if (($# == 0 || interval <= 0)); then
    printUsage
    exit 1
fi

# kill -0 pid   Exit code indicates if a signal may be sent to $pid process.
(
    if [ $pid_file != "" ]; then
       #echo "Adding pid $$ to $pid_file"
       echo $$ > $pid_file
       trap "cleanup" INT TERM ERR EXIT
    fi
    ((t = timeout))

    while ((t > 0)); do
        sleep $interval
        kill -0 $$ || exit 0
        ((t -= interval))
    done
    
    echo "Terminated $0 ($$) after a delay of $timeout sec while executing the command: $@"
    # Be nice, post SIGTERM first.
    # The 'exit 0' below will be executed if any preceeding command fails.
    if [ -e $pid_file ]; then
       rm -f $pid_file
    fi
    pid=`echo $$`
    #kill -s SIGTERM $$ && kill -0 $$ || exit 0
    kill -TERM -$pid
    sleep $delay
    kill -s SIGKILL $$
) 2> /dev/null &

exec "$@"

