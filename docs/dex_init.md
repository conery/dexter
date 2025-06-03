# `dex init`

The `init` command initializes a new database using descriptions of accounts in a CSV or Journal file.

#### Usage


```
$ dex init --help
usage: dex init [-h] [--force] F

positional arguments:
  F           name of file with account definitions

options:
  -h, --help  show this help message and exit
```

The command has one argument, the name of the account file.
The format of the file will be inferred from the filename extension, either `.csv` or `.journal`.

> _See [Defining Accounts](accounts.md) for details on how to define account attributes in each file format._


### Database Name

Dexter looks for the name to use for the new database in the following locations, in order:

* the value of the `--db` command line option
* the value of an environment variable named DEX_DB
* the name defined in the configuration file

If no name is found Dexter prints an error message and exits.

If there is already a database with that name Dexter prints a warning and exits.
Use `--force` if you want Dexter to erase the old database and replace it with the new one.

#### Example

To create a new database named `test` using the account definitions in `my_accounts.csv`:
```shell
$ dex --db test my_accounts.csv
```
