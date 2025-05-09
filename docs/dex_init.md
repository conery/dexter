# Create a New Database

The `init` command initializes a new database using descriptions of accounts in a CSV or Journal file.

#### Usage

```
$ dex init --file F [--force]
```

Specify the name of the file with `--file`.
The format of the file will be inferred from the filename extension, either `.csv` or `.journal`.

If the database exists already the command will print a warning and exit.
To replace an existing database use `--force`.

## CSV File Format

The first line in the file is a header that defines the columns that are present in the file.
The column names used by Dexter are:

| column | definition | example |
| --- | --- | --- |
| `fullname` | the name of the account | `expenses:food:groceries` |
| `category` | account category (optional, see below) | `expenses` |
| `abbrev` | a short version of the column name (optional) | `groceries` |
| `parser` | rule set for parsing downloads (required if parsing CSVs) |
| `balance` | the initial account balance (optional) |

Additional columns are allowed but will be ignored.

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
For example, suppose we want to print a table showing all food expenses before Jan 31, 2025:
```plain
$ dex select --end 2025-01-31 --debit food

2025-01-02  chase:visa       expenses:food:groceries       $22.04  Safeway
2025-01-06  bank:checking    expenses:food:groceries       $77.42  Costco
2025-01-06  bank:checking    expenses:food:groceries        $6.99  Safeway
2025-01-14  chase:visa       expenses:food:restaurant      $40.12  Pizza Palace
...
```

For long outputs the repetition of "expenses:food" is going to make the table harder to read.
If we specify `groceries` as an abbreviation for `expenses:food:groceries` and `restaurant` as an abbreviation for `expenses:food:restaurant` we can include the `--abbrev` option on the command line to print a more readable table:
```plain
$ dex select --end 2025-01-31 --debit food --abbrev

2025-01-02  chase:visa       groceries       $22.04  Safeway
2025-01-06  bank:checking    groceries       $77.42  Costco
2025-01-06  bank:checking    groceries        $6.99  Safeway
2025-01-14  chase:visa       restaurant      $40.12  Pizza Palace
...
```

The second reason is that when we download CSV files for assets and liability accounts we want to rename the file so the base name (the part before the extension) is the account name.
For example, if we have two bank accounts, one for checking and one for savings, we will download the records for each account separately.
Rename the file for the checking account to `checking.csv` and the file for the savings account to `savings.csv`.
When we run `dex import` to import a file, it will use the file name to figure out which account to use for the new postings.


### `parser`

If you plan to use the `import` command to parse downloads for asset and liability accounts you need to speficy a name in the `parser` column.

Parsers are defined in the [configuration file](dex_config.md).
There will typically be one parser for each data source.
For example, a person might have several Chase credit cards.
Their configuration file will have a section named `csv.chase` to tell Dexter how to parse downloads from Chase.
The `parser` column for these columns will have the word `chase` (without the `csv.` prefix).

### `balance`

Use this column to enter the starting balance of an account.

You can use it for assets (bank accounts) and, if using [envelope budgeting](envelopes_dex.md), for expense accounts.
Note that the initial contents of an envelope should be a negative number.
For example, if you want to start out with $100 in the groceries account put -100.00 in the balance column.

## Example

> **TBD** _plan to show the accounts used as a running example in the rest of the docs_

## Journal File Format

Accounts can also be defined in a Journal file, using the syntax supported by hledger.

Write an `account` statement for each account you want to define.

* the line starts with the word `account`
* following that write the name of the account (what would go in the `fullname` column of a CSV file)
* add a semicolon to start a comment
* add the remaining data, if any, in the form of `tag: value` pairs separated by commas

This example shows how to define a checking account with an initial balance of $1000, a credit card account, and three expense categories (one with subaccounts):

```plain
account assets:bank:checking         ; abbrev: checking, balance: 1000.00, parser: bank
account liabilities:chase:visa       ; abbrev: visa, parser: chase
account expenses:car                 ; abbrev: car
account expenses:food                ; abbrev: food
account expenses:food:groceries      ; abbrev: groceries
account expenses:food:restaurant     ; abbrev: restaurant
account home                         ; type: expenses
```
