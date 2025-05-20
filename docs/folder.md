# Example Data

The example data for this tutorial is in an archive that can be downloaded from the GitHub repo:
```plain
URL
```

The example folder has the following structure:
```plain
Finances/
├── accounts.csv          -- account names used to initialize the database
├── accounts.journal      -- same, but in an alternate format
├── dex.toml              -- Dexter configuration file
├── Downloads             -- directory for CSV records from financial institutions
│   ├── apr
│   └── may
└── regexp.csv            -- regular expressions used by pair command
```

We refer to this folder as a **project directory**.
It has a configuration file, CSV files with the definition of account names, and other data, depending on which subcommand you run.
It is possible to specify paths to each of these items, but we recommend putting all of the files in the same folder to use as the default location.

## Activate the Virtual Environment

The main reason for creating a project directory, however, is so that you can easily activate the Python virtual environment where Dexter was installed.
After you expand the archive, `cd` to the top level folder and type this command:
```shell
$ pyenv local dexter
```
Now whenever you `cd` to this folder the virtual environment will be activated automatically.

## Contents of the Example Folder

The account definitions and the sample CSV files are from a hypothetical couple named Alice and Bob.
The data are intended to be a [Minimal Reproducible Example](https://stackoverflow.com/help/minimal-reproducible-example): complex enough to be realistic without having too much extraneous detail.

In our case that means one income source for each person, one checking account, one savings account, and one credit card.
The expense categories are diverse enough to be able to illustrate the budget model and how subaccounts work, but with only seven categories it is not as complex as a real set of categories might be.

The Downloads folder has two subfolders, named for months.
The `apr` folder has hypothetical transactions for the three accounts for the month of April, 2024.

Dexter will detect when a data set has been previously loaded.
To illustrate how this works, the CSV files in the `may` directory have transactions from April and May, 2024.

<!-- One thing notably absent from the example directory is a file for transactions.
That's because Dexter stores transactions and other work products in a database.
After you define your account names you will use a command that initializes a new database. -->

