#!/bin/env python3


import argparse
import json
import os
import subprocess
import sys

from dataclasses import dataclass
from typing import List, Optional


_PROJECT_ROOT = None
_PROJECT_FILE = "vpy.json"
_DEFAULT_VENV_DIR = "venv"
_VENV_CACHE_DIR = "cache"


@dataclass
class CmdRunArgs:
    script_name: str
    script_args: List[str]


@dataclass
class CmdInstallArgs:
    modules: Optional[str]


def main():
    args = _parse_args()
    cmd = args.cmd

    if cmd == "init":
        _cmd_init()

    elif cmd == "install":
        install_args = CmdInstallArgs(modules=args.modules)
        _cmd_install(install_args)

    elif cmd == "run":
        cmd_args = CmdRunArgs(
            script_name=args.name,
            script_args=[],
        )
        _cmd_run(cmd_args)

    elif cmd == "shell":
        _cmd_shell()


def _parse_args():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest='cmd')

    parser_init = subparsers.add_parser("init")

    parser_install = subparsers.add_parser("install")
    parser_install.add_argument("modules", nargs="*", default=None)

    parser_run = subparsers.add_parser("run")
    parser_run.add_argument("name", nargs="?", default="run")

    parser_shell = subparsers.add_parser("shell")

    return parser.parse_args()


def _cmd_shell():
    root = _project_root()
    _create_venv()

    eprint("Entering virtual environment shell")
    _subprocess_cmd("source venv/bin/activate && bash")
    eprint("Exiting virtual environment shell")


def _cmd_init():
    dir_name = os.path.realpath(".").split("/")[-1]
    author = (
        _subprocess_cmd("git config user.name", capture_output=True)[0]
        or os.environ["USER"]
    )

    if os.path.isfile(_PROJECT_FILE):
        eprint("Project file already exists")
        exit(1)

    content = dict(
        name=dir_name,
        author=author,
        scripts=dict(
            run="python -c \"print(\\\"Hello, World!\\\")\""
        ),
        requirements=dict(),
    )

    j = json.dumps(content, indent=4)
    eprint(f"{_PROJECT_FILE} created\n{j}")
    with open(_PROJECT_FILE, "w") as f:
        f.write(j)

    _create_venv()


def _cmd_install(args: CmdInstallArgs):
    cache_dir = os.path.join(_project_root(), _DEFAULT_VENV_DIR, _VENV_CACHE_DIR)
    os.makedirs(cache_dir, exist_ok=True)
    req_file = os.path.join(cache_dir, "requirements.txt")

    proj = _read_project_file()
    for module in args.modules:
        name, version = _parse_module_spec(module)
        proj["requirements"][name] = version

    j = json.dumps(proj, indent=4)
    with open(_PROJECT_FILE, "w") as f:
        f.write(j)

    with open(req_file, "w") as f:
        for name, version in proj["requirements"].items():
            f.write(f"{name} {version}\n")

    _create_venv()
    _subprocess_cmd(f"source venv/bin/activate && pip install -r {req_file}")


def _cmd_run(args: CmdRunArgs):
    proj = _read_project_file()
    script_cmd = proj["scripts"][args.script_name]

    _create_venv()
    _subprocess_cmd(f"source venv/bin/activate && {script_cmd}")


def _read_project_file():
    path = os.path.join(_project_root(), _PROJECT_FILE)
    with open(path, "r") as f:
        return json.loads(f.read())


def _project_root():
    global _PROJECT_ROOT

    if _PROJECT_ROOT is not None:
        return _PROJECT_ROOT

    start_dir = os.getcwd()
    dir_ = start_dir
    while True:
        # TODO: handle file system boundary

        if dir_ == "/":
           eprint("No vpy project found")
           sys.exit(1)

        if os.path.isfile(_PROJECT_FILE):
           _PROJECT_ROOT = dir_
           return _PROJECT_ROOT

        dir_ = os.path.abspath(os.path.join(dir_, ".."))
        os.chdir(dir_)


def _subprocess_cmd(cmd: str, capture_output=False) -> (str, str):
    process = subprocess.Popen(
        cmd,
        shell=True,
        universal_newlines=True,
        stdout=subprocess.PIPE if capture_output else None,
        stderr=subprocess.PIPE if capture_output else None,
    )
    stdout, stderr = process.communicate()

    if capture_output:
        return stdout, stderr

    if stdout is not None:
        eprint(stdout, end="")
    if stderr is not None:
        eprint(stderr, end="")

    return stdout, stderr


def _has_venv():
    venv_path = os.path.join(_project_root(), _DEFAULT_VENV_DIR)
    return os.path.isdir(venv_path)


def _create_venv():
    path = os.path.join(_project_root(), _DEFAULT_VENV_DIR)
    if os.path.isdir(path):
        return

    _subprocess_cmd(f"virtualenv venv")


def _parse_module_spec(module: str) -> (str, str):
    """
    module: "module_name(> | < | >= | <= | ==)?version?"
    """
    # NOTE: Longer comparators needs to be before shorter ones with same leading
    # symbol
    for comp in ["<=", ">=", "==", "<", ">"]:
        if comp in module:
            name, version = module.split(comp)
            version = f"{comp} {version}"
            return name, version
    return module, ""


def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


if __name__ == "__main__":
    main()
