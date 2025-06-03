# `dex import`

The `import` command parses one or more CSV files and adds new Postings to the database.

#### Usage

```
$ dex import [-h] [--account A] [--start_date D] [--end_date D] [--month D] [--regexp] F [F ...]

positional arguments:
  F               name(s) of file(s) with records to add

options:
  -h, --help      show this help message and exit
  --account A     account name
  --start_date D  starting date
  --end_date D    ending date
  --month D       add records only for this month
```

The `import` command adds new records to the database.
There are two kinds of data:

* transactions downloaded from a financial institution, which will become postings in the database
* regular expression rules used by the `pair` and `review` commands.


## Importing Regular Expressions

If you want to import regular expresion rules, include the `--regexp` option on the command line:
```shell
$ dex import --regexp F
```

The tutorial data includes a file named `regexp.csv` you can use as a starting point for your own rules.
The file format and instructions for creating rules are explained in [Regular Expressions](regexp.md).

## Importing Financial Records

By default Dexter assumes you want to import financial records, so if you type
```shell
$ dex import F1
``` 
Dexter will assume the file `F1` contains transactions.

The file name extension tells Dexter what file format to expect.

* A `.journal` extension means the file contains Journal commands.  Currently only `account` commands and transaction definitions are recognized by Dexter.

* A `.csv` extension means the file contains transactions downloaded from a financial institution.

Journal files are meant to be used to initialize a new database (using the `dex init` command) or to import a small number of transactions, for example budget transactions.

The remainder of this page has instructions for importing CSV files.


## Import a Single Transaction File

To import a single file just specify the file name and use the `--account` option to tell Dexter which account to use for the new postings.

Suppose you log in to your bank and download the transactions for your checking account.
The bank web site will give the file a name that may or may not include the account name.
Let's suppose it's simply "Download.csv" and your browser puts it in your main Downloads folder.
This command will import those records as postings to the your checking account in the database:
```shell
$ dex import ~/Downloads/Download.csv --account checking
```

The `--account` option tells Dexter to look up the account with the abbreviated name `checking`, and to use the parser associated with that account to process every record in the file.

If the file name is the same as the abbreviated name you can omit the `--account` option.
For example, if you download the CSV file, then move it to the Downloads folder in your project directory and rename it with the account name, you don't need to specify the name with `--account`:
```
$ mv ~/Downloads/Download.csv ./Downloads/checking.csv
$ dex import Downloads/checking.csv
```

## Import Multiple CSV Files

It's often more efficient to do a "bulk import" of several CSV files.
In order to do this each file needs to have the name of an account.
You can't use `--account` because the files belong to different accounts.

For example, if your project's Download folder has files named `checking.csv` and `savings.csv` you can use one command to import them both:
```
$ dex import Downloads/checking.csv Downloads/savings.csv
```

If all the CSV files in Downloads are named for accounts you can also just type
```
$ dex import Downloads/*.csv
```

## Is Bulk Import Really More Efficient?

It takes a bit of work to organize downloads before a bulk import.
This is a common situation:

* log in to the bank web site, download files from each account
* the bank gives them all the same name (`Download.csv`) so your browser puts them in your main Downloads with a generic name like `Download.csv`
* the files have to be renamed and moved to your project Download folder, _e.g._
```
$ mv ~/Downloads/Download.csv ./Downloads/checking.csv
```

Although that seems like a lot of work it is probably worth the effort, for several reasons.

1. If you don't rename the files you can accumulate a lot of duplicate names like `Download (1).csv`, `Download (2).csv`, _etc_, depending on how many accounts you have at the bank.
1. You'll have to remember which file goes with which account in order to give the right name with the `--account` option wheh you import them one at a time.
1. If you get into a pattern of download, move, download the next, move, ... it's easier to get the names correct.

And finally, if you select the "year to date" option at the bank web site your CSV file will contain all the transactions for that account.
Dexter checks to make sure it doesn't re-import a record, so it's OK to import a file that has all records for the year.
Now you'll have CSV files, with names that reflect the account they came from, that can be used for other purposes as well.

## TBD: Working with Aggregators

There are several web sites that serve as "aggregators".
They can connect to your banks and credit card companies and download all of your records for you.
Then you just need to log in to the aggregator and do one download to get those records.

A future extension will allow parsers to specify a column in the CSV file to use as the account name.

<!-- The two that I have tried (Mint and Empower) worked fairly well but had enough drawbacks that I stopped using them.
There were often "gaps" in the data that caused me to lose several days worth of records.
These sites also did too much "preprocessing" and filtered out columns from the original records that I wanted to use.

Recently several new services have started up, all using Plaid.
I'm looking forward to trying them out. -->
