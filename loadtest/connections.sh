#!/bin/sh
TOTAL=`netstat --inet -n | grep -v CLOSE | grep -v FIN | grep -v TIME| wc -l`
MAXTALK=`netstat --inet -n | grep -v CLOSE | grep -v FIN | grep -v TIME| grep 6545 |wc -l`
MAX=`netstat --inet -n | grep -v CLOSE | grep -v FIN | grep -v TIME| grep 6543 |wc -l`
MONGO=`netstat --inet -n | grep -v CLOSE | grep -v FIN | grep -v TIME| grep 27017 |wc -l`

echo "TOTAL $TOTAL"
echo "MAXTALK $MAXTALK"
echo "MAX $MAX"
echo "MONGO $MONGO"
