#!/bin/bash

function header {
    printf "\nInitializing environment\n"
}

function footer {
    printf "\n---------------------------------\n"
    env | grep -e HOSTNAME -e HOSTIP -e DB
    printf "\n---------------------------------\n"
    printf "Initializing environment done\n"
    printf "\n---------------------------------\n"
    printf "Starting: Server\n\n"
}

function is_db_alive {
  state=0
  printf "checking for database"
  while ! nc -q 1 mongodb_container 27017 </dev/null 1> /dev/null 2> /dev/null; do
    case $state in
      0) printf "\rchecking for database: -";;
      1) printf "\rchecking for database: \\";;
      2) printf "\rchecking for database: |";;
      3) printf "\rchecking for database: /";;
    esac
    [ "${state}" = "3" ] && state=0 || state=$((state+1))
    sleep 0.1
  done
  export DB=mongodb_container
  printf '\rchecking for database -> db alive\n'
}

function SERVER {
  python3 /code/run.py
}

function infinity_loop {
  export PYTHONPATH=/code
  while true; do
    # Touch /flask_app/DEBUG, kill run.py and start run.py manually for debugging... :)
    if [[ ! -f "/code/DEBUG" ]]
    then
	    SERVER;
    fi
    sleep 1
  done
}

header
footer
is_db_alive
infinity_loop
