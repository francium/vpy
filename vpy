#!/bin/bash

# Strict mode - http://redsymbol.net/articles/unofficial-bash-strict-mode/
set -euo pipefail
IFS=$'\n\t'


DEFAULT_VENV_PATH="venv"
PROJECT_ROOT=""
PROJECT_FILE="vpy.json"
ACTIVATE_PATH="bin/activate"
CACHE_DIR="cache"


function echoerr {
    echo "$@" 1>&2;
}


function _validate_requirements {
    which python3 > /dev/null
    if (( $? != 0 )); then
        echoerr "Python3 not found in PATH"
        exit 1
    fi

    which virtualenv3 > /dev/null
    if (( $? != 0 )); then
        echoerr "Virtualenv3 not found in PATH"
        exit 1
    fi

    which jq > /dev/null
    if (( $? != 0 )); then
        echoerr "jq not found in PATH"
        exit 1
    fi
}
_validate_requirements


function _find_project_root {
    if [[ $PROJECT_ROOT != "" ]]; then return; fi

    pushd . > /dev/null
    while true; do
        # TODO: Handle filesystem boundary
        if [[ $PWD == "/" ]]; then
            echoerr "No vpy project found"
            exit 1
        fi

        if [[ -f $PROJECT_FILE ]]; then
            local dir=$PWD
            popd > /dev/null

            PROJECT_ROOT=$dir
            return
        fi
        cd ..
    done
}


function _create_venv {
    local venv_path=$1

    echoerr "Creating virtual environment $venv_path"
    virtualenv $DEFAULT_VENV_PATH
}


function _activate_venv {
    _find_project_root

    local full_venv_path=$PROJECT_ROOT/$DEFAULT_VENV_PATH
    if [[ ! -d $full_venv_path ]]; then
        _create_venv $full_venv_path
    fi

    . $full_venv_path/$ACTIVATE_PATH
}


function _cmd_init {
    dir_name=${PWD##*/}
    author=$(git config user.name || echo $USER)

    if [[ -f $PROJECT_FILE ]]; then
        echoerr "Project file vpy.json already exists"
        exit 1
    fi

    cat << EOF > vpy.json
{
    "name": "$dir_name",
    "author": "$author",
    "scripts": {
        "run": "python -c \"print('Hello, World!')\""
    },
    "requirements": {
    }
}
EOF

    echoerr "Project initialize"
    cat $PROJECT_FILE
}


function _cmd_install {
    _activate_venv
    if (( $? != 0 )); then
        exit 1
    fi

    local dir=$PROJECT_ROOT/$DEFAULT_VENV_PATH/$CACHE_DIR
    mkdir -p $dir

    jq \
        -r \
        '.requirements | to_entries | map("\(.key) == \(.value)") | join("\n")' \
        $PROJECT_ROOT/$PROJECT_FILE \
    > $dir/requirements.txt

    pip install -r $dir/requirements.txt
}


function _cmd_run {
    if [[ -z "${1:-}" ]]; then
        local script="run"
    else
        local script=$1
        local args=${@:2}
    fi

    _activate_venv
    if (( $? != 0 )); then
        exit 1
    fi

    target=$( \
        jq \
            -r \
            ".scripts | to_entries | map(select(.key | match(\"$script\"))) | .[0].value" \
            $PROJECT_ROOT/$PROJECT_FILE \
    )
    if [[ $target == "null" ]]; then
        echoerr "Script '$script' not found"
    fi

    eval "$target $args"
}


function _cmd_shell {
    _activate_venv
    if (( $? != 0 )); then
        exit 1
    fi

    echoerr "Entering virtualenv shell"
    bash
    echoerr "Exiting virtualenv shell"
}


function _cmd_help {
    echoerr "\
vpy - virtualenv wrapper

Usage:
    vpy [command]

Commands:
    init     TODO
    install  Install requirements.txt
    run      Run project target
    shell    enter virtual environment shell
    help     print help"
}


function _main {
    cmd=$1
    args=${@:2}

    case $1 in
        "init")    _cmd_init $args;;
        "install") _cmd_install $args;;
        "run")     _cmd_run $args;;
        "shell")   _cmd_shell $args;;
        "help")    _cmd_help $args;;
        *)         _cmd_help $args;;
    esac
}
_main ${@:1}
