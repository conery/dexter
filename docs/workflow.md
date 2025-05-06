# Monthly Workflow

The standard workflow assumes transactions are saved in a database.
Each month a new batch of CSVs is downloaded, added to the database, and refined into a set of transactions.

Because the scripts that initialize a database can read `.journal` files from hledger there is an aternative workflow for users who just want to use Dexter to convert CSV files into transactions or for envelope budgeting.
In this workflow, a temporary database is created using account definitions, new records are loaded from CSV files, and the results are written back out in a `.journal` format that can be read by hldeger.
See [hledger Workflow](hledger.md) for details.

## Initialize the Database

Before importing the first batch of CSV files a new database must be initialized.
This step will be skipped in future months.

The command that creates the DB reads a file with account names.
The file can be a `.journal` file or a CSV file.
See [Defining Accounts](accounts.md) for details.

Run `dex init` to create a new database.
The command line arguments specify the name of the database and the name of the file with account defintions.

Example:
```
$ dex init ....
```

## Download CSVs

Log in to bank and credit card company web sites.
Download all of the transactions for the current period (typically the month since the last batch of downloads).

For convenience it's possible to specify YTD as the date range.
Dexter will skip any previously imported records.

We recommend setting up a folder to hold all your downloads and moving all the CSV files to this folder.

Run the command that imports all CSVs:
```
$ dex import ...
```

## Pair CSV Records

After running `import` the DB will have a new set of Posting records.
The goal now is to create Transaction records.

The `pair` command has two phases.
In phase one it looks for sets of postings that are the source and destination of 




