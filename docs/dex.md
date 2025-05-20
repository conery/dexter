# Shell Command

The shell command to run Dexter has the general form of
```shell
$ dex CMND [OPTIONS]
```
where CMND is the name of an operation that implements a step in the expense tracker workflow.

Before we describe the commands there is some important background information you need to know.
Those topics, covered on this page, are:

* the configuration file
* connecting to a database
* running commands in preview mode
* options for commands

## Configuration File

The configuration file we'll use in the tutorial is a file named `dex.toml` in the top level of the project folder:
```plain
Finances
├── dex.toml
...
```

You do not need to make any changes to this file in order to run the example commands in the tutorial, but you should know that it exists.
Many of the settings are cosmetic, for example colors to use when printing tables in the terminal window, and names to use as alternatives to "debit" and "credit".

If you want to make any changes you can find details about the file format in the section on [Configuration](dex_config.md).
You could edit `dex.toml` but a better idea would be to copy that file and make changes in the copy.
You can tell Dexter to use an alternative configuration file with the `--config` option:
```shell
$ dex --config my_dex_config.toml ...
```

## Connecting to a Database

Dexter stores account names, transactions, and other data in a database.
By default it uses a popular NoSQL database server named MongoDB.

> _Coming soon:_  users will have the option of using SQLite.

Dexter looks in the configuration file to find the name of the database.
The default name, speficifed in `dex.toml`, is `dex`.
You can specify an alternative name with the `--db` option:
```shell
$ dex --db my_dex_db ...
```

## Preview Mode

Sometimes it's helpful to know how Dexter will process some data before you actually add it to the database.
A good example is the `import` command, which will read data from CSV files downloaded from a bank or credit card company.

If you want a preview of what will be added to the database use the `--preview` option (which can be abbreviated to `--pre`), _e.g._
```shell
$ dex --pre import Downloads/apr/*.csv
```

## Options for Commands

The `--config`, `--db`, and `--preview` options can be used with any Dexter command.
There are also options that pertain to specific commands.
For example, when importing CSV files we can tell Dexter to use transactions within a specified date range.

To see the list of options for a command, enter the command name and then type `--help` after the command name:
```shell
$ dex import --help
usage: dex import [-h] [--account A] [--start_date D] [--end_date D] [--month D] [--regexp] F [F ...]

positional arguments:
  F               name(s) of file(s) with records to add

options:
  -h, --help      show this help message and exit
  --account A     account name
  --start_date D  starting date
  --end_date D    ending date
  --month D       add records only for this month
  --regexp        CSV files have regular expression definitions
```

There is an important detail in that "usage" string:  command-specific options need to be entered **after the command name.**
For example, this is how we would get a preview of records with dates before Apr 15, 2024:
```shell
$ dex --preview import --end_date 2024-04-15 Downloads/apr/*csv
```

Note that `--preview`, which is defined for all commands, goes before the command name, and `--end_date` is after the command name.

You'll find more information about command line options at [Command Line Options](dex_options.md).
