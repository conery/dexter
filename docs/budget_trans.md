
# Budget Transactions

The paycheck transaction at the beginning of the month deposited $5000 in our bank account.
If we're using zero-based budgeting we'll want to distribute all of it to envelopes.
Suppose this is our budget:

| Expense Category | Amount | Comment |
| ---- | ----- | ----- |
| Home | $3000 | rent, household items, _etc_ |
| Car  | $1000 | payment, fuel, misc expenses |
| Food | $1000 | groceries, restaurants |

The key idea behind Dexter's approach to budgeting is to use **_expense accounts_**, not asset accounts, to represent envelopes.

<!-- > [!NOTE] Envelopes = Expense Accounts
> Envelopes are not simply _associated with_ expense accounts, they _are_ expense accounts. -->

The transaction below, which we call a **budget allocation transaction**, allocates funds to envelopes according to our budget.
Note that it _debits income accounts_ and _credits expense accounts_.
The credits are how we model the process of adding money to the envelope, and the debit is a record of where that money came from:

```plain
2024-01-02  fill envelopes                        ; budget:
    income:yoyodyne                $5000.00
    expenses:home                 $-3000.00
    expenses:car                  $-1000.00
    expenses:food                 $-1000.00
```

There's a lot going on there!

Using the income account on the debit side makes it look like we're giving our salary back to the company.
We're not, but it does mean we need a new interpretation for the balance of an income account.
The balance on that account is now $5000 - $5000, or $0.
That seems meaningless, but in fact it's very useful information, as we'll explain below.

On the other side, what are all those credits to expense accounts doing?
They certainly play havoc with the balances of those accounts.
For example, when the credit to `expenses:food` is combined with the two transactions shown earlier the food account balance is -$1000 plus $40, for a total of -$960.
But here also there is a method to our madness, to be explained shortly.

Before we get to the explanations, though, there is an important point:

> **Budget transactions are easily ignored.**

It's very easy to recover the original meanings of the balance of income and expense accounts by simply not including budget transactions in balance calculations.

Here is the default report for food expenses after we add budget transactions:

```bash
$ dex report expenses:food --end 2024-01-10

expenses:food  ✉️                                                                                                        
┏━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━┓
┃ date         ┃ description               ┃ credit               ┃ debit                ┃       amount ┃      balance ┃
┡━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━┩
│ 2024-01-01   │ starting balance          │                      │                      │              │        $0.00 │
│ 2024-01-02   │ fill envelopes            │ food                 │ yoyodyne             │    −$1000.00 │    −$1000.00 │
│ 2024-01-07   │ Chez Ray                  │ assets:checking      │ food:restaurant      │       $75.00 │     −$925.00 │
│ 2024-01-08   │ venmo from Sam            │ food:restaurant      │ bank:checking        │      −$35.00 │     −$960.00 │
└──────────────┴───────────────────────────┴──────────────────────┴──────────────────────┴──────────────┴──────────────┘
```

Note there is a small envelope icon in the title bar next to the account name, to remind us that budget transactions are used in balance calculations.

If you want to exclude budget transactions add a `--no_budget` option to the shell command and you'll get the same report as before:

```bash
$ dex report expenses:food --end 2024-01-10 --no_budget

expenses:food:                                                                                                          
┏━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━┓
┃ date         ┃ description               ┃ credit               ┃ debit                ┃       amount ┃      balance ┃
┡━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━┩
│ 2024-01-01   │ starting balance          │                      │                      │              │        $0.00 │
│ 2024-01-07   │ Chez Ray                  │ assets:checking      │ food:restaurant      │       $75.00 │       $75.00 │
│ 2024-01-08   │ venmo from Sam            │ food:restaurant      │ assets:checking      │      −$35.00 │       $40.00 │
└──────────────┴───────────────────────────┴──────────────────────┴──────────────────────┴──────────────┴──────────────┘
```

<!-- Budget transactions can also be used in `hledger` and other plain text accounting applications.
See [TBD](tbd) for ideas of how to organize journals with budget transactions and examples of `hledger` commands to print reports with and without budgets. -->

<!-- An `hledger` user who wants to use this budgeting scheme has several options for controlling when budget transactions are part of the journal:

* Put budget transactions in a separate file, and add a line to the main file that includes the budget transaction file.  Commenting out the include statement tells `hledger` to ignore the budget.

* Put a tag on each budget transaction (the example above has a `budget:` tag).  When running an `hldeger` report command use a query that selects all transactions or one that filters out transactions with a `budget:` tag. -->

