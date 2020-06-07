# vpy
**Experimental, use at your own risk!**

vpy is a high-level wrapper around virtualenv and pip to provide a NPM like
experience for python3.

pip and virtualenv on their own are great tools, but using them can be tedious
and possibly error prone due to pip's default behaviour when run outside a
virtual environment.

NPM has some desirable qualities. This is an attempt to capture those without
re-creating a dependency management tool from scratch.


## Requirements
- Python3.x
- virtualenv3
- pip3
- bash (TODO: replace with a call to users predefined shell, `$SHELL`)
- git (TODO: Handle git not installed)


## Installation
Copy `vpy` to somewhere in your `$PATH` and make sure the executable bit is set,
`chdmod +x vpy`.


## Basic usage
```bash
$ mkdir my-python-project && cd my-python-project

# Initialize directory as a vpy project
$ vpy init

# Install pypi modules (optionally with version requirements, note must be quoted)
$ vpy install requests "numpy>=1.0.0" "flask<1.0.0"

# Drop into a shell with virtual environment activated
$ vpy shell
```
