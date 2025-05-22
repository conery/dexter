# Import CSV Files

Now that we have the database set up with account names we're ready to import some data.

The first step in your monthly workflow will be to connect to your banks and other financial institutions and download all of your transactions.
We have some sample data to use for this tutorial in the `Downloads` section of the project folder:
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

The subfolder named `apr` has transactions for a single month, April 2024.

The subfolder for `may` has the same three files, but now the transactions are for two months, April and May of 2024.
The idea is to illustrate how Dexter avoids importing duplicate transactions, and to provide an example of the process we suggest for managing downloads:

* connect to the financial institution's web site

* select an account, download all transactions, using the "year to date" option

* find the file in your Downloads folder, rename it, and move it to the downloads section of your project folder

Selecting "year to date" is simpler than specifying a date range (and remembering which transactions you have already downloaded).
But the main benefit is having a full record of all downloads in a single file that is always up to date for each account.

## Preview the April Transactions

The general form of the `import` command is
```bash
$ dex import F1 F2 ...
```
where the names following `import` are the names of the files to import.

In our case, the April data is all in one folder, and we want to import all of the files, so we can just type `Downloads/apr/*`.

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
entry  2024-05-02           $10.00  liabilities:chase:visa  ESSENTIAL PHYSICAL THERAP  [<Tag.U: '#unpaired'>]
entry  2024-04-30           $25.75  liabilities:chase:visa  SP GIST YARN &amp; FIBER   [<Tag.U: '#unpaired'>]
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
│ dev          │      26 │           2 │    62 │       0 │
└──────────────┴─────────┴─────────────┴───────┴─────────┘
```
Before there were 4 postings, now there are 62.

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


