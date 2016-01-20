#!/bin/bash

# Runs the bot

reset_db=$1

source ./set_env.sh

executable="python"
has_python3=`which python3`

if [[ ! -z $has_python3 ]]; then
  executable="python3"
fi

$executable src/main.py $reset_db
