#!/bin/bash

echo "Insert username:"
read input_username
export OCTIV_USERNAME="$input_username"
echo "Insert password:"
read input_password
export OCTIV_PASSWORD="$input_password"
