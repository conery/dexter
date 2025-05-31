# Import Regular Expressions

The next step in the workflow is to "pair" the postings we just imported.
Dexter uses pattern matching rules as a key part of this process.
So before we run the `pair` command we have to load the patterns into the database.

> _The pattern matching rules for the tutorial are in a file named `regexp.csv`. You do not need to make any changes to this file, but you can open it with a text editor while you are reading the examples shown below._

## A Pairing Example

As an example of what we want the `pair` command to do, consider one of the postings created by importing the checking account data:
```plain
2024-04-24     -$15.00   visa   NEWMAN'S FISH COMPANY       #unpaired
```
The minus sign in the amount means it is a credit (withdrawal) to the checking account.

> _**Note:** the terminal output shows credits/negative numbers in red, without the minus sign._

If we regularly shop at this store we will see this kind of posting again in the future.
Our monthly financial workflow would be more efficient if Dexter could automatically create a new transaction for us:  whenever it sees a credit with a description that matches "NEWMAN" it should create a debit to `expenses:food:groceries`.
It could then create a new transaction using the two postings.

## Pairing Rules

The key word in that previous paragraph is "match".
Dexter uses Python regular expressions to make pairs of postings.
For each record read from a CSV file, it looks through a set of **pairing rules** to find a rule that can be applied to the CSV record.
The parts of a rule are:

* a pattern to match against the posting description
* the action to take when a description matches the pattern
* the account name to use for the new pairing
* a pattern for the transaction description

As an example, here is the rule for Newman's:
```plain
trans,NEWMAN,Newman's Fish,groceries
```
The parts are:

* `trans` is the action to take -- it means "make a new transaction"
* "NEWMAN" is the pattern
* "Newman's Fish" is the description that will go in the new transaction
* the last column is the account name to use in the new posting

The pattern and new description in this example are pretty boring -- all the rule is doing is turning the all-uppercase input into a more readable mixed case.
In other cases, however, the pattern matching rules can be very helpful.
For example, a CSV record in the checking account can have a description like "Payment to Chase Credit Card" or ""Payment to Citi Credit Card".
We can make a rule that matches any card name and then include that name in the transaction description:
```plain
xfer,Payment to (\w+),{0} Payment,
```
The `\w+` in the pattern means "any string of letters" and the `{0}` in the new description means "whatever letters were found in the input".

> _The full set of instructions for writing pairing rules can be found in [Regular Expressions](regexp.md)._

## Transfers

The `xfer` in the rule shown above for the Chase payment is a second type of action the `pair` script can take.
Here the goal isn't to create a new posting but to try to find two complementary postings that already exist.
In this case, if there is a card payment made from the checking account, there should be a matching deposit in the credit card account.

Transfer rules are also used for transactions that move money between bank accounts.
The sample data has a transfer from checking to savings each month.

In each case -- card payments and bank transfers -- the pairing rules should have patterns that tell Dexter how to identify the two halves of a transfer so it can pair them to make a new transaction.

## `fill` and `sub` Rules

The CSV file can have two other kinds of rules, called "fill" and "sub" (short for "substitution") rules.
These are used by the `review` command, so we won't discuss them until that section of the tutorial.

## The `regexp.csv` File

Pairing rules need to be saved in a CSV file and then loaded into the database.
Adding rules to the database uses the same `import` command that parses downloads.
Simply add the `--regexp` option to tell Dexter that the file being imported has pairing rules instead of downloaded transactions.

The rules for the sample data are in a file named `regexp.csv`.
Type this command to add them to the `dev` database:
```shell
$ dex import --regexp regexp.csv
```

Run the `info` command again, and now you will see the pairing rules have been added (the count in the `reg_exp` column changes from 0 to 29):
```shell
$ dex info

Databases                                                 
┏━━━━━━━━━━━━━━┳━━━━━━━━━┳━━━━━━━━━━━━━┳━━━━━━━┳━━━━━━━━━┓
┃ name         ┃ account ┃ transaction ┃ entry ┃ reg_exp ┃
┡━━━━━━━━━━━━━━╇━━━━━━━━━╇━━━━━━━━━━━━━╇━━━━━━━╇━━━━━━━━━┩
│ dev          │      18 │           2 │    32 │      29 │
└──────────────┴─────────┴─────────────┴───────┴─────────┘
```
