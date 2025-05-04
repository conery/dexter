# Philosophy

Our financial lives a more complex and varied since the 1980s, when I wrote that first Pascal program.
Back then I had one checking account and a few credit cards, and it wasn't too hard to enter each transaction by hand when doing the bills each month.

Nowdays we have a variety of ways to spend money.
We still might write checks by hand, but are more likely to use our bank's online bill paying system.
Whether you want to or not, you'll probably have several credit cards, not just for buying stuff (online or in person), but for making travel arrangements, paying for subscriptions and streaming services, and more.
And then there are PayPal, Venmo, Apple Pay, and other "e-cash" systems.

All of the organizations we deal with -- banks, card companies, and e-cash services -- allow us to download a record of our transactions.
Why not take advantage of all that data?

> _Dexter is designed for users who download all of their transactions._

Given that premise as a starting point, Dexter has several core principles.

#### Every CSV Record Becomes a Posting

Every record in a CSV file downloaded from a financial institution is from a real world event.
It needs to be turned into a posting that debits or credits one of our real accounts, _i.e._ either an asset or a liability account.

<!-- We call these postings __real postings__. -->

#### Postings from CSVs Are Immutable

When importing a CSV record we save the date, description, amount, and type (debit or credit) as part of the posting.
This information is used to compute a unique ID for each posting (so records are not imported twice) and never changes after the posting is saved.

#### Postings from CSVs Are Never Deleted

Postings created from CSV files are a permanent record of real-world transactions.

#### Postings Need to Be Paired to Form Transactions

The CSV records by themselves are not complete transactions.
They are merely building blocks, either a credit or a debit that must be matched with another posting to create a transaction.

There are two ways to form transactions:

* Find two postings that are the source and destination of a transfer.  These postings will have the same amount but different "polarities", _i.e._ one will be a credit and one will be a debit.  Examples are transfers between bank accounts or credit card payments.

* Create a new complementary posting that debits or credits a nominal account.  For example, if a posting is a credit to the checking account (and was not paired with another posting as part of a transfer) it is a check or debit card purchase.  We need to figure out what the purchase was for and create a debit to an expense category.

The next section is an overview of scripts that help streamline this process, _e.g._ by automatically create postings based on pattern matching.

