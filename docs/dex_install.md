# Installation

> [!note] OS Versions
> These instructions are for macOS and should work on Linux.
> Instructions for Powershell are planned.

### Install Dexter

Dexter depends on a several third-party libraries.
We recommend setting up a new virtual environment for Dexter and its dependences.

Start by typing a command that goes to your Finances folder:
```shell
$ cd Finances
```

Choose a Python version.
Dexter was developed using 3.13.1 but any version newer than 3.11 should work:
```shell
$ pyenv local 3.13.1
```

Make a new environment based on the selected Python.
You can name it anything; this example makes an environment named `dexter`:
```shell
$ pyenv virtualenv dexter
```

If you type this command your new environment will always be activated whenver you `cd` to Finances:
```shell
$ pyenv local dexter
```

### Help Messages

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
$ dex init -h
usage: dex init [-h] --file F [--format C]

options:
  -h, --help  show this help message and exit
  --file F    name of file with account definitions
  --format C  file format
```

### Install MongoDB

The easiest way to install MongoDB is to use Homebrew:
```shell
$ brew tap mongodb/brew
$ brew install mongodb-community
```

Then start the server:
```shell
$ brew services start mongodb-community
```

The server should run automatically every time you restart your computer.

