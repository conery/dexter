# Pair Transactions



There are two different ways to create transactions.
One is to look for transfers between accounts.
For example, we might put away a part of our income, which is in the checking account, by making a transfer to the savings account.
Credit card payments are also transfers, from our checking account to the credit card account.

The second method is to look at descriptions of postings to see if we can infer the expense category.
The posting for the first record from the credit card account looks like this:
```plain
entry  2024-05-02           -$10.00  liabilities:chase:visa  ESSENTIAL PHYSICAL THERAP  [<Tag.U: '#unpaired'>]
```
If that's something that will be a recurring event, we can create a new transaction automatically.
Whenever the `pair` command sees a posting with "ESSENTIAL PHYSICAL" in the description, it can create a new posting.
The new posting should have the "opposite polarity", meaning it should be a debit for $10.00, and the account should be `expenses:medical`, the expense category Alice and Bob use for physical therapy sessions.
After adding the new posting to the database Dexter can pair it with the credit to the liability account to make a new transaction.
