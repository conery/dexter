# Import CSV Files

Now that we have the database set up with account names we're ready to import some data.

The first step in your monthly workflow will be to connect to your banks and other financial institutions and download all of your transactions.
The sample data for this tutorial in the `Downloads` section of the project folder:
```plain
Finances
...
├── Downloads
│   ├── apr
│   │   ├── chase.csv
│   │   ├── checking.csv
│   │   └── savings.csv
│   └── may
│       ├── chase.csv
│       ├── checking.csv
│       └── savings.csv
```

The general form of the `import` command is
```bash
$ dex import F1 F2 ...
```
where the names following `import` are the names of the files to import.

In our case, the April data is all in one folder, and we want to import all of the files, so we can just type `Downloads/apr/*`.


<!-- The subfolder for `may` has the same three files, but now the transactions are for two months, April and May of 2024.
The idea is to illustrate how Dexter avoids importing duplicate transactions, and to provide an example of the process we suggest for managing downloads:

* connect to the financial institution's web site

* select an account, download all transactions, using the "year to date" option

* find the file in your Downloads folder, rename it, and move it to the downloads section of your project folder

Selecting "year to date" is simpler than specifying a date range (and remembering which transactions you have already downloaded).
But the main benefit is having a full record of all downloads in a single file that is always up to date for each account. -->

## File Names

An important detail to note here is that the base name of each CSV file matches the abbreviated name of one of the accounts.
That's how Dexter knows which account name to use for the new postings it is about to create:  records in `chase.csv` will be assigned to `liabilities:visa:chase`, and so on.

Your typical monthly workflow will probably be something like this:

* connect to a financial institution's web site

* select an account, download all transactions

* find the file in your Downloads folder, rename it, and move it to the downloads section of your project folder

It is possible to use a different naming convention, but then files need to be imported one at a time, using the `-account` option to tell Dexter which account to use, _e.g._

```bash
$ dex import --account chase ~/Downloads/ChaseXXXX_Activity20240101_20240525_20240525.CSV
```

> _**Note**_: an item high on our TO DO list is to import CSV files downloaded from an aggregator, in which case the account name must be one of the columns in the data file.

## Preview the April Transactions


As a first step we recommend running the command in preview mode.
Dexter will parse the files and print the records it will import on the terminal.
It's a good way to make sure you're getting the data you expect and to work out any problems with file names or other issues.

Here it the command to preview the CSV files for April:
```shell
$ dex --pre --db dev import Downloads/apr/*
```

## Verify the Output

The output will be shown in sections, one for each input file.
A section will start with a log message that looks like this, with the name of the file that will be processed:
```plain
INFO     Parsing Downloads/apr/chase.csv
```

Next are a series of lines, with one line for each CSV record:
```plain
2024-04-26            $15.00   visa   LONGS MEAT MARKET           #unpaired
2024-04-24            $15.00   visa   NEWMAN'S FISH COMPANY       #unpaired
2024-04-23           $100.00   visa   EUGENE WATER AND ELECTRIC   #unpaired
...
```

Each of these lines will be saved in the database as a posting.
The important information to look for is the date, amount, account, and description.
The account shown here will be the full account name.  Dexter uses the name of the file (in this case, `visa.csv`) to figure out which account to use (`visa` is the abbreviation for `liabilities:chase:visa`).

**Note:**  When you define your own parser you will be making heavy use of preview mode.
This is where you will be able to make sure your parser is extracting the right information from the CSV file.

## Import the April Transactions

When everything looks OK, run the same shell command, but without the `--preview` option:
```shell
$ dex --db dev import Downloads/apr/*
INFO     Parsing Downloads/apr/chase.csv
INFO     Parsing Downloads/apr/checking.csv
INFO     Parsing Downloads/apr/savings.csv 
```

Printing the status of the database should show the new data have been added:
```shell
$ dex info

Databases                                                 
┏━━━━━━━━━━━━━━┳━━━━━━━━━┳━━━━━━━━━━━━━┳━━━━━━━┳━━━━━━━━━┓
┃ name         ┃ account ┃ transaction ┃ entry ┃ reg_exp ┃
┡━━━━━━━━━━━━━━╇━━━━━━━━━╇━━━━━━━━━━━━━╇━━━━━━━╇━━━━━━━━━┩
│ dev          │      18 │           2 │    32 │       0 │
└──────────────┴─────────┴─────────────┴───────┴─────────┘
```
Before there were 4 postings, now there are 32.

#### Save May for Later

If you want you can repeat the steps above for the data in the folder for May.
But we recommend waiting until you have worked through the complete tutorial.
You'll have a smaller and more manageable set of data for each step if you use only the April data the first time through.

## CSV Transactions Are Saved As Postings

The output from the `info` command brings up an important point about terminology.

From the financial institution's perspective, the word "transaction" means "an event that updated the balance of your account", such as a purchase or a deposit.
The web site will show a table of transactions, and most likely the command to save them has a name like "download transactions".

Each transaction from the financial institution will become a single line in the CSV file.
So when we wrote above "Preview the April Transactions" we meant "preview the records in the CSV download for April."

From Dexter's perspective, however, the word "transaction" has the meaning used in double entry bookkeeping.
A transaction is a transfer of money between two (or more) accounts.
Each CSV record becomes a **posting** in the database.
So from now on, when we refer to the data we just imported, we will use the DEB terminology and call these items postings.

The next step in the expense tracking workflow is to create transactions by pairing the new postings.


