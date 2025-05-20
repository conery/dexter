# `dex init`

The `init` command initializes a new database using descriptions of accounts in a CSV or Journal file.

See [Defining Accounts](accounts.md) for details on how to define account attributes in each file format.

#### Usage


```
$ dex init --file F
```

Specify the name of the file with `--file`.
The format of the file will be inferred from the filename extension, either `.csv` or `.journal`.

### Database Name

Dexter looks for the name to use for the new database in the following locations, in order:

* the value of the `--db` command line option
* the value of an environment variable named DEX_DB
* the name defined in the configuration file

If no name is found Dexter prints an error message and exits.

<!-- If the database exists already the command will print a warning and exit.
To replace an existing database use `--force`. -->

#### Example

To create a new database named `test` using the account definitions in `my_accounts.csv`:
```shell
$ dex --db test --file my_accounts.csv
```
