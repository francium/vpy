#!/bin/bash


DEFAULT_VENV_PATH="venv"
PROJECT_FILE="requirements.txt"
ACTIVATE_PATH="bin/activate"


function _validate_requirements {
    which python3 > /dev/null
    if (( $? != 0 )); then
        echo "Python3 not found in PATH"
        exit 1
    fi

    which virtualenv3 > /dev/null
    if (( $? != 0 )); then
        echo "Virtualenv3 not found in PATH"
        exit 1
    fi
}
_validate_requirements


function _find_project_root {
    pushd . > /dev/null
    while true; do
        if [[ -f $PROJECT_FILE ]]; then
            local dir=$(pwd)
            popd > /dev/null

            echo $dir
            return
        fi
        cd ..
    done
}


function _create_venv {
    local VENV_PATH=$1

    echo "Creating virtual environment $VENV_PATH"
    virtualenv $DEFAULT_VENV_PATH
}


function _activate_venv {
    local PROJECT_ROOT=$(_find_project_root)
    local FULL_VENV_PATH=$PROJECT_ROOT/$DEFAULT_VENV_PATH
    if [[ ! -d $FULL_VENV_PATH ]]; then
        _create_venv $FULL_VENV_PATH
    fi

    . $FULL_VENV_PATH/$ACTIVATE_PATH
}


function _cmd_install {
    _activate_venv
    pip install -r $PROJECT_FILE
}


function _cmd_run {
    _activate_venv
    echo "TODO: run"
}


function _cmd_shell {
    _activate_venv
    echo "Entering virtualenv shell"
    bash
    echo "Exiting virtualenv shell"
}


function _cmd_help {
    echo "\
vpy - virtualenv wrapper

Usage:
    vpy [command]

Commands:
    install  Install requirements.txt
    run      Run project target
    shell    enter virtual environment shell
    help     print help"
}


function _main {
    cmd=$1
    args=${@:2}

    case $1 in
        "install") _cmd_install $args;;
        "run")     _cmd_run $args;;
        "shell")   _cmd_shell $args;;
        "help")    _cmd_help $args;;
        *)         _cmd_help $args;;
    esac
}
_main ${@:1}
