# Create a New Database

> [!note] Usage
> ```
> $ dex init [-h] --file F [--force]
> ```

The `init` command initializes a new database using descriptions of accounts in a CSV or Journal file.

Specify the name of the file with `--file`.
The format of the file will be inferred from the filename extension, either `.csv` or `.journal`.

If the database exists already the command will print a warning and exit.
To replace an existing database use `--force`.

## CSV File Format

The first line in the file is a header that must contain at least the columns shown below.
Additional columns are allowed but will be ignored.

| column | definition | example |
| --- | --- | --- |
| `fullname` | the name of the account | `expenses:food:groceries` |
| `abbrev` | a short version of the column name (optional) | `groceries` |
| `parser` | rule set for parsing downloads (required for parsing CSVs) |
| `balance` | the initial account balance (optional) |

### `fullname`

Dexter uses the same hierarchical account name conventions as GnuCash, hledger, and other systems.

The segments of a name are separated by colons.
The first segment is the account category.
Every account name must start with one of the basic account types of double-entry bookkeeping:

* `assets` are typically checking or savings accounts
* `liabilities` are credit cards and mortgages or other loans
* `income` is for salary and other types of income
* `expenses` are categories that describe what a purchase was for

Some examples:
```plain
income:salary
assets:bank:checking
expenses:food:groceries
liabilities:chase:visa
```

> **Note**: a fifth account category, `equity`, will be defined automatically.  You don't need to include it in your account file.

There is no limit on the number of segments in a name.

A segment name may appear in more than one account name.
For example, you can have `expenses:car:insurance`, `expenses:home:insurance`, and `expenses:medical:insurance`.

### `abbrev`

The optional abbreviated account name is a name that can be used in reports.

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

### `parser`

If we plan to use the `import` command to parse downloads for asset and liability accounts you need to speficy a name in the `parser` column.

Parsers are defined in the configuration file.
There will typically be one parser for each data source.
For example, a person might have several Chase credit cards, or many different accounts from the same bank.
Their configuration file will have a section named `csv.chase` to tell Dexter how to parse downloads from Chase, and another section named `csv.bank` (perhaps using the bank name) to specify how to parse CSV files downloaded from there.

### `balance`





## Journal Files

```plain
account equity                    ; type: equity
account assets:bank:checking             ; type: assets
account assets:bank:savings             ; type: assets
account expenses:car                       ; type: expenses
account expenses:car:payment                       ; type: expenses
account expenses:car:fuel                       ; type: expenses
account expenses:food                       ; type: expenses
account expenses:food:groceries                 ; type: expenses
account expenses:food:restaurant                ; type: expenses
account expenses:home                       ; type: expenses
account expenses:home:household                 ; type: expenses
account expenses:home:mortgage                  ; type: expenses
account expenses:travel                    ; type: expenses
account income:yoyodyne                  ; type: income
account liabilities:amex                 ; type: liabilities
account liabilities:chase:visa                ; type: liabilities
```

recognizes two different formats

## Shell Command
