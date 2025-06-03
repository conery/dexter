# Installation

> [!note] OS Versions
> These instructions are for macOS and should work on Linux.
> Instructions for Powershell are planned.

## Overview

Dexter is a command line application.
The shell command to run it has the general form of
```shell
$ dex CMND [OPTIONS]
```
where CMND is the name of an operation (initialize new database, import CSVs, _etc_) and OPTIONS vary from one command to another.

A typical session with Dexter starts with going to the folder where you work on your finances and running Dexter commands to carry out your expense tracking workflow:
```shell
$ cd Finances
$ dex report --audit
$ dex import Downloads/*.csv
$ dex pair
...
```

## Virtual Environment

Dexter depends on a several third-party libraries.
We recommend setting up a new virtual environment for Dexter and its dependences.

Start by choosing a Python version.
Dexter requires Python 3.13 or higher:
```shell
$ pyenv shell 3.13.1
```

Make a new environment based on the selected Python.
You can name it anything; this example makes an environment named `dexter`:
```shell
$ pyenv virtualenv dexter
```

Run `pip` to download and install Dexter:
```shell
$ pip install git+https://github.com/conery/dexter.git
```

## Help Messages

To test the installation ask `dex` to print a help message.
If you run `dex` with no arguments you'll see an abbreviated help message:
```shell
$ dex
usage: dex [-h] [--dbname X] [--log X] [--preview] [--config F] {config,init,import,...}
```

Use `-h` or `--help` to see a longer message:
```shell
$ dex -h
usage: dex [-h] [--dbname X] [--log X] [--preview] [--config F] {config,init,import,...}

options:
  -h, --help            show this help message and exit
  --dbname X            database name
  --log X
  --preview
  --config F            TOML file with configuration settings

subcommands:
    config              print default config file
    init                initialize a database
    import              add new records from files
    ...
```

To print the help message for a subcommand, type the command name before typing `-h` or `--help`, _e.g._
```shell
$ dex init --help
usage: dex init [-h] --file F

options:
  -h, --help  show this help message and exit
  --file F    name of file with account definitions
```
