# Command Line Options

There are two types of command line options:  those that are common to all commands, and options that are specific to each command.

Following a common Unix convention, option names can be abbreviated as long as they are distinct from other options.
For example, the `select` command has options named `debit` and `date`.
If you want to specify a value for `debit` you can use `--debit` or `--deb` or even `--de`, but not just `--d` because both "debit" and "date" start with "d".

### Common Options

The first part of the main help message shows the names of the common options:
```shell
options:
  -h, --help            show this help message and exit
  --dbname X            database name
  --log X
  --preview
  --config F            TOML file with configuration settings
```

**Note:**  Common options must be typed before a subcommand name.

#### `dbname`

The name of the database to use.
If no name is given, Dexter will look for an environment variable named `DEX_DB`.

Example:  initialize a new database named `foo`:
```shell
$ dex --db foo init ...
```

#### `log`

This option controls the amount of information printed on the terminal.

Alternatives are `quiet` (don't print anything), `info` (the default), and `debug` (which prints a ton of stuff, intended for developers who are tracking down problems).

Example:  initialize a new database but dont' print status messages.
```shell
$ dex --db foo --log quiet init ...
```


#### `preview`

If this option is specified Dexter will print descriptions of data it will use but won't actually carry out the operation.

As an example of how to use it, suppose you have downloaded a CSV file and saved it in `Downloads/checking.csv` and now you want to import it.
If you want to see a list of the Postings that Dexter extracts from the file include the `-preview` option:
```shell
$ dex --preview import Downloads/checking.csv 
```

To save the records in the database run the command again without `--preview`.

#### `config`

Dexter uses a configuration file to specify many different runtime options.
By default it looks for a file named `dex.toml` in the current directory or a file name specified with the `DEX_CONFIG` enfironment variable.

Use the `config` option to specify an alternative file.

<!-- > _**Note**: You will need to create a configuration file if you are going to import data from CSV files because the configuration file is where Dexter gets the specification of which fields to use in each CSV file.  See [Configuration](dex_config.md) for more information._ -->

### Subcommand Options

If a subcommand has options they are specified after the command name.

For example, the `select` command has options to speficy attributes of transactions to search for.
These include the start and end dates, descriptions, amounts, and so on.
This command searches the database named `dev` to find car expenses (transactions that debit the `car` account) with dates before Jan 31 2025:
```shell
$ dex --db dev select --end 2025-01-31 --debit car
```

> _**Important:** Notice how the `--db` option, which is common to all `dex` subcommands, comes before the command name, while the `--end` and `--debit` options for `select` are after the command name._

### Date Range Options

Several subcommands have `--start_date`, `--end_date`, and `--month` options.

For `--start_date` and `--end_date` you can specify dates with a variety of formats.
If the format includes spaces or slashes make sure you put quotes around the date.
All of these are ways of specifying an end date of Jan 31, 2025:
```plain
--end_date 2025-01-31
--end_date 'Jan 31, 2025'
--end_date '1/31/2025'
--end_date '1/31'
```
(for the last example, the year is inferred from the current date).

> _If the day number is 12 or less a date is ambiguous.  Is 1/7 Jan 7 or Jul 1?  For dates with slashes Dexter uses the American convention that the month number precedes the day number._

The `--month` option is a shorthand for specifying both a starting and ending date.
The argument should be a 3-letter month abbreviation, from `jan`, `feb`, _etc_ up to `dec`.
Dexter will convert the month name into a pair of dates within the last year.

Suppose today's date is May 5, 2025.

* If you specify `--mon apr` the start date will be Apr 1, 2025 and the end date Apr 30, 2025.
* If you specify `--mon sep` you will get a starting date of Sep 1, 2024 and an ending date of Sep 30, 2024.
