#!/bin/bash

echo "Error catcher initilialized"

echo $number  # Output: 25
pm2 logs --format | grep auto | while read line
do
    id=$(echo "$line" | grep -oP '(?<=id=)\d+')
    echo "$line" | grep "*** API error"
    if [ $? = 0 ]
    then
        echo "Restarting..."
        pm2 restart $id
    fi
done
