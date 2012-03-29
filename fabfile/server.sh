#!/bin/sh

# Starts, stops, and restarts the application.
#
# chkconfig: 35 92 08
# description: Starts and stops the application

# Source function library.
. /etc/rc.d/init.d/functions

# activate the virtualenv
. '%(sandbox)s/bin/activate'

PIDFILE='%(instance_var)s/server.pid'
APP='%(repo)s/manage.py'


start() {
    echo "Starting application"
    $APP runserver &
    PID=$!
    echo -n $PID > $PIDFILE
    RETVAL=$?
    echo
    return $RETVAL
}

stop() {
    echo "Stopping application"
    kill -9 `cat $PIDFILE`
    RETVAL=$?
    echo
    return $RETVAL
}

case $1 in
    start)
        start
        ;;
    stop)
        stop
        ;;
    restart)
        stop
        sleep 1
        start
        ;;
    *)
        echo "Usage: $0 {start|stop|restart}" >&2
        exit 1
        ;;
esac
