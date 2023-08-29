#!/bin/bash

echo "Starting Tests..."
python tests.py
# shellcheck disable=SC2181
if [ $? -eq 0 ]
then
    echo "Tests Complete. Starting Application"
    python main.py
else
    echo "Tests Failed. Exiting Application"
fi
echo "Application Exited"
