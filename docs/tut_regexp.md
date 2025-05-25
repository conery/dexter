# Import Regular Expressions

Now that we have postings based on the CSV records from our bank and credit card we're ready to start combining them into full transactions.
To do that we'll use Dexter's `pair` command.

## A Pairing Example

As an example of what we want that command to do, consider the posting created by importing the first record in `chase.csv`:
The posting for the first record from the credit card account looks like this:
```plain
entry  2024-04-30           -$10.00  liabilities:chase:visa  ESSENTIAL PHYSICAL THERAP  [<Tag.U: '#unpaired'>]
```
In our hypothetical data set, that's a payment Alice made to her physical therapist.
The minus sign in the amount means it is a credit to the `visa` account.

> _Note: the terminal output shows credits/negative numbers in red, without the minus sign._

That's something that we expect to see often.
Our monthly financial workflow would be more efficient if Dexter could automatically create a new transaction for us:  whenever it sees a credit with a description that matches "ESSENTIAL PHYSICAL" it should create a debit to `expenses:medical`, the expense category Alice and Bob use for PT sessions, and then create a new transaction using the two postings.

## Pairing Rules

The key word in that previous paragraph is "match".
Dexter uses Python regular expressions to make pairs of postings.
For each record read from a CSV file, it looks through a set of **pairing rules** to find a rule that can be applied to the CSV record.
The parts of a rule are:

* a pattern to match against the posting description
* the action to take when a description matches the pattern
* the account name to use for the new pairing
* a pattern for the transaction description

As an example, here is the rule for the physical therapy session:
```plain
trans,ESSENTIAL PHYSICAL THERAP,Essential Phyiscal Therapy,medical
```
The parts are:

* `trans` is the action to take -- it means "make a new transaction"
* "ESSENTIAL PHYSICAL THERAP" is the pattern
* "Essential Phyiscal Therapy" is the description that will go in the new transaction
* "medical" is the abbreviated account name to use in the new posting

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
In this case, if there is a payment made from the checking account, there should be a matching deposit in the credit card account.

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
$ dex --db dev import --regexp regexp.csv
```

Run the `info` command again, and now you will see the pairing rules have been added (the count in the `reg_exp` column changes from 0 to 40):
```shell
$ dex info

Databases                                                 
┏━━━━━━━━━━━━━━┳━━━━━━━━━┳━━━━━━━━━━━━━┳━━━━━━━┳━━━━━━━━━┓
┃ name         ┃ account ┃ transaction ┃ entry ┃ reg_exp ┃
┡━━━━━━━━━━━━━━╇━━━━━━━━━╇━━━━━━━━━━━━━╇━━━━━━━╇━━━━━━━━━┩
│ dev          │      26 │           2 │    62 │      40 │
└──────────────┴─────────┴─────────────┴───────┴─────────┘
```






