# Defining Accounts

The central concept in double-entry bookkeeping is the idea that transactions move funds between accounts.
When we create a new database we need to tell Dexter the names and types of all of our income, asset, expense, and liability accounts.

Account names are defined in a plain text file.
Dexter recognizes two different file formats:

* a `.csv` (comma separated values) file has a header line followed by one line for each account, specifying the names at attributes of each account.

* a `.journal` file has `account` statements in the Journal format used by hledger; each statement has the name of the account followed by tags that define the attributes.

There is one example of each type of file in the example data:
```plain
Finances
├── accounts.csv
├── accounts.journal
```
You should end up with the same records in your new DB using either file.

### Parsers

The key part of your monthly workflow will be importing records you download from banks, credit card companies, and other financial institutions.

As described earlier in [Philosophy](philosophy.md) Dexter will create one new Posting for each record from a CSV file.
In order to do this, it needs to know which columns of the CSV file to use, and it needs to know how to extract the relevant information from those columns.

The example data has three CSV files.
Two (checking account and savings account) are from Alice and Bob's bank.
The format for these files is based on my own bank, Oregon Community Credit Union.
There is nothing unusual about this format and it should be a useful template for other banks (and very likely is exactly the same as many other credit unions).
The credit card format is from Chase Bank and should be the same for all Chase credit cards.

Dexter needs a set of rules, called a **parser**, for each different file format.
Parsers are defined in the configuration file.
If you open the example configuration (`dex.toml`) you'll find the rules for parsing CSV files from OCCU are in a section named `csv.occu`:
```plain
[csv.occu]
description = ...
date = ...
amount = ...
credit = ...
```
The Chase card parser is in a similar section, labeled `csv.chase`.

Every parser has four rules, corresponding to the four attributes of a Posting that need to be filled in.
The name of the rule, to the left of the equal sign, is the name of the attribute.
The right sides are Python expressions that tell Dexter where to look for the data to use for that attribute.

The main thing to know at this point is that when we define an account that will have data downloaded from a financial institution we need to specify which parser to use.

### Defining Your Own Parsers

Simply knowing how to associate an account name with a parser is sufficient for working through the rest of this tutorial.
When you are ready to define your own parsers you'll find a detailed description of rules and hints about what to include in the User Documentation section, under [Configuration](dex_config.md).

## CSV Format for Accounts

The first line in the CSV file is a header that defines the columns that are present in the file.
The column names used by Dexter are:

| column | definition | example |
| --- | --- | --- |
| `fullname` | the name of the account | assets:bank:checking |
| `category` | account category (optional, see below) | assets |
| `abbrev` | a short version of the column name (optional) | checking |
| `parser` | rule set for parsing downloads (required if parsing CSVs) |
| `balance` | the initial account balance (optional) | 1,000.00 |
| `date` | date for initial account balance (required if balance specified) | 2024-12-31 |

**Tip:** When you create your own account file you can use a spreadsheet application.
The columns can be defined in any order, and the file can have additional columns (they will be ignored).
The only requirement is that column names shown above be entered exactly as they are shown, in all lower case.
Then simply export the spreadsheet as a CSV file (making sure to include column names, if that is an option).

### `fullname`

Dexter uses the same hierarchical account name conventions as GnuCash, hledger, and other systems, where
the segments of a name are separated by colons.

Generally the first segment is the account category, one of the basic account types of double-entry bookkeeping:

* `assets` are typically checking or savings accounts
* `liabilities` are credit cards and mortgages or other loans
* `income` is for salary and other types of income
* `expenses` are categories that describe what a purchase was for

Some examples:
```plain
income:salary
assets:bank:checking
expenses:travel
liabilities:chase:visa
```

> **Note**: a fifth account category, `equity`, will be defined automatically.  You don't need to include it in your account file.

There is no limit on the number of segments in a name.

A segment name may appear in more than one account name.
For example, you can have `expenses:car:insurance`, `expenses:home:insurance`, and `expenses:medical:insurance`.

##### A Note About Subaccounts

Suppose you know you want subaccounts for types of food expenses, for example `expenses:food:groceries` and `expenses:food:restaurant`.
That brings up a question:  do you also need to define the "parent" account, `expenses:food`?

The answer is no, you are not required to define every intermediate level account.
But there are two good reasons to do so:

* The parent account can serve as a "miscellaneous" or "unclassified" category.  At some point you might have an expense you know you want to put in the food group but can't decide which subaccount to put it in, so just assign it to `expenses.food` (but if you have a lot of these it may be better to define `expenses:food:misc` for the random food expense).
* When you are allocating income to budget envelopes, you can assign an amount to `expenses:food` to cover all food expenses.  Any expense that debits any food account, no matter where it is in the hierarchy, will take funds from the overall food envelope.

If you want to use intermediate accounts like `expenses:food`, either for miscellaneous expenses or for budgeting, the account needs to be defined in the CSV file with other accounts.

### `category`

If an account name starts with one of the four main account types the category will be inferred from the account name.
Otherwise put the account type in the `category` column.

### `abbrev`

There are two reasons to define an optional abbreviated name for an account.

One use is to define a short name for an expense account so it can be used in reports.
For example, suppose we want to print a table showing all food expenses before Jan 31, 2025.
The `select` command (described later in [Select Transactions](dex_select.md)) will print that table:
```plain
$ dex select --end 2025-01-31 --debit food

2025-01-02  chase:visa       expenses:food:groceries       $22.04  Safeway
2025-01-06  bank:checking    expenses:food:groceries       $77.42  Costco
2025-01-06  bank:checking    expenses:food:groceries        $6.99  Safeway
2025-01-14  chase:visa       expenses:food:restaurant      $40.12  Pizza Palace
...
```

For long outputs the repetition of account name prefixes like "expenses:food" is going to make the table harder to read.
If we specify abbreviations, _e.g._ `groceries` for `expenses:food:groceries` and `visa` for `liabilities:chase:visa`, we can include the `--abbrev` option on the command line to print a more readable table:
```plain
$ dex select --end 2025-01-31 --debit food --abbrev

2025-01-02  visa        groceries       $22.04  Safeway
2025-01-06  checking    groceries       $77.42  Costco
2025-01-06  checking    groceries        $6.99  Safeway
2025-01-14  visa        restaurant      $40.12  Pizza Palace
...
```

The second reason is that when we download CSV files for assets and liability accounts we want to rename the file so the base name (the part before the extension) is the account name.
For example, if we have two bank accounts, one for checking and one for savings, we will download the records for each account separately.
Rename the file for the checking account to `checking.csv` and the file for the savings account to `savings.csv`.
When we run `dex import` to import a file, it will use the file name to figure out which account to use for the new postings.


### `parser`

As noted above, parsers are defined in the [configuration file](dex_config.md).
There will typically be one parser for each data source.
The `parser` column for these accounts will have the name of the configuration section without the `csv.` prefix, _e.g._ `occu` or `chase`.

### `balance`

Use this column to enter the starting balance of an account.

You can use it for assets (bank accounts) and, if using [envelope budgeting](envelopes_dex.md), for expense accounts.
Note that the initial contents of an envelope should be a negative number.
For example, if you want to start out with $100 in the groceries envelope put -100.00 in the balance column.

## Journal File Format for Accounts

Accounts can also be defined in a Journal file, using the syntax supported by hledger.

Write an `account` statement for each account you want to define.

* the line starts with the word `account`
* following that write the name of the account (what would go in the `fullname` column of a CSV file)
* add a semicolon to start a comment
* add the remaining data, if any, in the form of `tag: value` pairs separated by commas

The category tag can be omitted if the full name starts with one of the four basic categories (`assets`, `expenses`, `income`, `liabilities`).

Here are some examples from `accounts.journal` in the example data:

```plain
account assets:bank:checking        ; category: assets, abbrev: checking, parser: occu
account liabilities:chase:visa      ; type: liabilities, abbrev: visa, parser: chase
account income:yoyodyne             ; abbrev: yoyodyne
account expenses:food               ; type: expenses
account expenses:food:groceries     ; type: expenses, abbrev: groceries
```

Instead of putting a balance and date in a comment in the `account` add a transaction statement following the account statements.
This is how to initialize the checking and savings account balances:
```plain
2024-12-31 initial balance
    assets:bank:checking   $1,000.00
    assets:bank:savings    $2,500.00
    equity
```
