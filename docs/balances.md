# Account Balances

Before we introduce budget transactions we should review how account balances are computed.

In double-entry bookkeeping the **balance** of an account is the sum of the inflows (debits) minus the sum of the outflows (credits).

Here are a few example transactions (written in the Journal format used by `hledger` and other plain text accounting applications):

```plain
2024-01-02  paycheck
    assets:checking             $5000.00
    income:yoyodyne            $-5000.00

2024-01-06  Tools R Us
    expenses:home                $100.00
    assets:checking             $-100.00

2024-01-07  Chez Ray
    expenses:food:restaurant      $75.00
    assets:checking              $-75.00
```

In a journal file the signs on the amounts indicate the direction the money flowed:  `+` for a debit and `-` for a credit.

The first transaction is for our monthly paycheck.
It debits (adds to) the checking account, and credits an income source.

The next two transactions show we bought some tools at a hardware store and paid for them using our checking account (either a paper check or a debit card), then ate at a restaurant, also paying for it directly from the checking account.
In both cases the negative amount means funds moved out of the checking account and the positive amount means the money was moved into one of the expense accounts.

Because the Journal format uses positve numbers for debits (inflows) and negative numbers for credit (outflows) all we need to do to compute a balance for an account is add the amounts on all lines that name the account.
Looking at the lines above, the three lines that refer to `assets:checking` have amounts $5000, $-75, and $-100, so the balance is $4875.

In the examples so far the expense account was debited, but it's worth noting that a transaction can credit an expense account.
For example, suppose that lunch at the restaurant was with a friend, and the next day our friend used Venmo to reimburse us for their share.
The best way to represent this is with a transaction that debits the checking account (it's an inflow into the account) and credits the food expense account.
Note how the signs are the opposite of what they were in the original purchase:

```plain
2024-01-08  venmo from Sam
    assets:checking                 $35.00
    expenses:food:restaurant       $-35.00
```

This transaction has an impact on the balance of both accounts: the checking account now has $4875 (the previous balance) + $35, or $4910, and the restaurant account has $75 - $35, or $40.

This command shows the balance of `expenses:food`, including all subcategories (`expenses:food:groceries`, `expenses:food:restaurant`, _etc_), from the start of the year through the date of the Venmo transaction:

```bash
$ dex report expenses:food: --end 2024-01-10

expenses:food:                                                                                                          
┏━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━┓
┃ date         ┃ description               ┃ credit               ┃ debit                ┃       amount ┃      balance ┃
┡━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━┩
│ 2024-01-01   │ starting balance          │                      │                      │              │        $0.00 │
│ 2024-01-07   │ Chez Ray                  │ assets:checking      │ food:restaurant      │       $75.00 │       $75.00 │
│ 2024-01-08   │ venmo from Sam            │ food:restaurant      │ assets:checking      │      −$35.00 │       $40.00 │
└──────────────┴───────────────────────────┴──────────────────────┴──────────────────────┴──────────────┴──────────────┘
```
