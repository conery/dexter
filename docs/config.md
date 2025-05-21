# Configuration

Dexter uses a configuration file to define settings used by various scripts.
Many of these are cosmetic, for example colors to use when printing tables on the terminal.

But there is one important part of the configuration that you need to define as soon as you can:
the **parsers** that extract data from CSV files downloaded from banks, credit card companies, and other financial institutions.

The sections on this page tell you how to set up your configuration:

* where Dexter looks for configuration files
* how to create a template configuation file
* the structure of a configuration file
* how to define parsers

## Finding Configuration Files

Dexter looks in the following locations, in order:

* a path specified by the `--config` option on the command line
* a path stored in an environment variable named DEX_CONFIG
* a file named `dex.toml` in in current directory (where the `dex` command is run)
* a default configuration file in the installed code

## Create a Template

A configuration file is a plain text file that you can edit with any text editor.

The `config` subcommand prints a template configuration file on the terminal.
To see the template, simply type
```shell
$ dex config
```

To save the file in the default location (a file named `dex.toml` in your project directory) just redirect the output:
```shell
$ dex config > ./dex.toml
```

The template defines two parsers.
One is for my bank, Oregon Community Credit Union, which has a format that should be typical of the one used by most banks and should be easily adapted for your bank.
The other is for Chase credit cards.
You should be able to use this as is for your own Chase cards.

> _**TBD:**  Parsers for other widely used credit cards (American Express, Citi, and Apple (Goldman Sachs)) will be added soon.  We also plan to add a section to the GitHub repo for user-contributed parsers._

## The Structure of a Configuration File

As the filename extension `.toml` implies, configuration files use a standard format known as TOML.

> It's unlikely you'll need to know more than what is covered here, but if you're curious or do run into trouble the TOML documentation is at [TOML: Tom's Obvious Minimal Language](https://toml.io/en/)

A line that starts with a hash symbol (`#`) is a comment, and the file can include blank lines to improve readability.

A TOML file is organized by section.
A section name is written in brackets, _e.g._ `[terminology]`.

A section can have subsections, which are indicated by periods in the name.
The default configuration has a section named `[csv]` and then subsections named `[csv.occu]` and `[occu.chase]`.

Configuration settings look like assignment statements in a programming language, with a name, an equal sign, and a value.
Values can be numbers, dates, strings, or compound items like lists of strings.
All of Dexter's configuration settings will be simple numbers or strings.

## Defining a Parser

Our goal is to define a set of rules for extracting data from a CSV file downloaded from a financial institution.

The first step is to find out what information we have to work with in each CSV file.
The first line in a file is header, which is a list of column names, separated by commas.

> _Note: some CSV files omit the header line and just contain data.  It's not likely you will get a file without column names from a financial institution, but if you do you'll need to edit the file and add a header._

This is the header on a file from OCCU:
```
"Transaction ID","Posting Date","Effective Date","Transaction Type","Amount","Check Number","Reference Number","Description","Transaction Category","Type","Balance","Memo","Extended Description"
```
and here is the header in a file from Chase:
```
Transaction Date,Post Date,Description,Category,Type,Amount,Memo
```

It doesn't matter whether the names are enclosed in quotes, or whether a column name is a single word or multiple words.

The order doesn't matter, either.
We just need to be able to figure out which columns we're interested in.

### Configuration Section

If you are writing a new parser the first step is to add a new section to the configuration file.
For example, if you have American Express cards, you'll want to name the parser `amex`, and you'll add a new section named `[csv.amex]`.

### Rules

When the `import` command reads a CSV file it creates one new Posting for each line in the CSV (described in [Philosophy](philosophy.md)).
The new Posting has four attributes:

* description
* date
* amount
* credit (a boolean that is True if the posting is a credit, False if it is a debit)

Every parser has exactly four configuration settings.
The name to the left of the equal sign is the attribute name, and the value on the right side is an expression that tells the parser where to find the value for that attribute.

### Expressions

The values on the right side of a setting are Python expressions.
Even if you don't know Python you should be able to understand the expressions in the default configuration and generalize them to write your own expressions.

To explain the sorts of things that can go into a Python expression we'll use the rules in the example configuration, starting with the simplest and working up to more complex rules.

> _A more detailed description of what is allowed in Python expressions will be included in the Reference section [TBD](tbd.ml)_.


#### `date`

In the Python code the name `rec` (short for "record") refers to the current line in the CSV file.
To access part of a line write the column name in brackets immediately after `rec`.  

For example, the transaction date in an OCCU download is in a column named "Posting Date", so the Python expression that refers to the date column on the current line is `rec["Posting Date"]`.

Here is the rule in the OCCU parser:
```
date = 'rec["Posting Date"]'
```
That simply means "use the "Posting Date" column from the CSV file as the value of the date in the new posting that will be added to the database."

Notice an important detail: the expression on the right side of the rule has a string inside a string.
The outer (single) quotes are needed to tell TOML that the attribute is a string, and the inner (double) quotes tell Python that "Posting Date" is string to use for the column name.

In the Chase download the column has a slightly different name, using "Post" instead of "Posting".
This is the rule in the Chase parser:
```
date = 'rec["Post Date"]'
```

<!-- One last note:  The file from OCCU has two columns with transaction dates, one called "Posting Date" and one called "Effective Date".
The Chase file also has two dates, "Transaction Date" and "Post Date".
In these situations you can choose which one to use. -->

#### `description`

A CSV file from Chase has a column named "Description" that has a brief description of a transaction.
It's usually the name of a business, _e.g._ "CHEVRON" or "IZAKAYA JAPANESE RESTAURANT".
So a simple rule for filling the `description` attribute of the new posting is to just copy the value from this column:
```
description = 'rec["Description"]'
```

The rule for the OCCU download is a little more interesting:
```
description = 'rec["Description"] + rec["Extended Description"]'
```
In Python, if `s` and `t` are strings, the expression `s + t` means "combine `s` and `t` into one longer string".

What's going on here is that neither column, by itself, has enough useful information.
In some transactions we'll want the "Description" column, and in others we'll want the "Extended Description".
The solution is to combine both columns into one long string and save that in the database.

That's going to lead to some pretty ugly looking descriptions.
But keep in mind, the next step in the overall workflow, after importing records, is to run a script that applies regular expressions to postings, and those regular expressions will usually clean things up.
So if the parser saves a description like

```
 Transfer to PayPalPAYPAL INSTANT TRANSFER - INST XFER
```
a regular expression can transform it into
```
PayPal Payment
```

A general rule:

> _When writing expressions for the desciption attribute, make sure you save enough "raw material" from the CSV file so regular expressions later in the workflow have enough to work with._

One final note:  you can save a "marker" in the description so you (and the regular expression) can know where the two parts were in the CSV file.
This rule will put a slash between the two fields from the CSV file:
```
description = 'rec["Description"] + "/" + rec["Extended Description"]'
```
That Python expression combines three strings (a column from the CSV, a slash, and another column) into one longer expression.
Now the PayPal description will look like this:
```
Transfer to PayPal/PAYPAL INSTANT TRANSFER - INST XFER
```

#### `amount`

The rule for the `amount` attribute needs to convert a string from the CSV file (all columns in a CSV file are strings) into a number, and to make sure the number is positive (all amounts on postings in our database are positive).

Python's builtin `float` function is just what we need.
If `s` is a string containing digits (and maybe a decimal point) the expression `float(s)` means "convert `s` into a number".

To write the parser rule, just identify the column that has the transaction amount and pass that to `float`.
Both OCCU and Chase use a column named "Amount" so the rule will have this expression:
```
float(rec["Amount"])
```

In looking at the downloads we can see that both CSV files have positive and negative amounts in this column.
To make sure all our values are positive just pass the result of calling `float` to another builtin function, `abs` (for "absolute value").
The final rule is:
```
amount = 'abs(float(rec["Amount"]))'
```
> _**TBD**:  how to write a rule when a CSV file has separate columns for credit and debits._

#### `credit`

The last attribute we need to define is the `credit` attribute.
The rule has this general form:
```
credit = 'p(...)'
```
where `p` is a "predicate", or in Python terminology, a Boolean expression.
It the expression is True our new posting will be a credit, otherwise it will be a debit.

If a CSV file is for an asset account, for example it comes from a bank and is for a checking or savings account, we want transactions that are **withdrawals or purchases** to become **credits** in our database.
These will eventually be paired with a debit to an expense account to form a complete transaction.
On the other hand, CSV records for **deposits** should become **debits**.

In looking through a CSV file from OCCU it's apparent there are negative numbers in the amount column for purchases/withdrawals and positive numbers for deposits.
So all we need to do is look at the sign in the "Amount" column.
If there is a negative sign we want the new posting to be a credit.

Python has a very useful string method named `startswith` that we can use for our rule.
In Python, if `s` and `t` are strings, the expression `s.startswith(t)` is True if the letters in `t` occur at the beginning of the `s`.
So to see if the amount column has a minus sign at the front the Python code is `rec['Amount'].startswith("-")` .

In English, the rule would be "set `credit` to True if the first character in the Amount column is a minus sign".
This is how to write it in Python:
```
credit = 'rec["Amount"].startswith("-")'
```

For the Chase parser the same logic applies.
If a transaction is a purchase we want it to be a credit, but if it's a return or a card payment we want it to be a debit.
The "Amount" column in this file also has minus signs for credits, so the rule is the same as the rule for the OCCU parser.

### Final Notes on Writing Parsers

Any column from the CSV file can be used in an expression.
Some other columns you might find useful are memos (notes that might be included on an electronic check) and transaction types (where an entry might be a word like "purchase" or "payment").

Many organizations have started including "category" or "transaction category" columns.
These are automatically generated and are often helpful.
For example, if a business is known to be a restaurant, the category column might have "Food & Drink".

A potential strategy for coming up with categories for purchases might be to save these columns as part of the description, maybe at the end, after a special character:
```plain
IZAKAYA JAPANESE RESTAURANT / Food & Drink
```
Then when you write the regular expressions used by the `pair` command (described in [Regular Expressions](dex_pair.md)) you can write a rule that debits your `restaurant` account when it sees this credit.

In my experience, however, these categories are inconsistent and not very useful.
They are based solely on the name of the payee, and often have mistakes.
For example, if you pay for admission to the Ford Theater, you would probably characterize it as entertainment, but the CSV download is likely going to call it an automotive expense.
