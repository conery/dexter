# Using the Equity Account

When a database is initialized we define initial balances for the asset accounts using transactions that debit the asset and credit a special account named `equity`.
Several accounts can be initialized with a single transaction.
This shows our checking account had $1000 and our savings account had $7000 on January 1:
```plain
2024-01-01  initial balances
    assets:checking               $1000.00
    assets:savings                $7000.00
    equity                       $-8000.00
```
To make sure the transaction balances, the amount on the last line is the total amount in all of our accounts.

<!-- In this situation, the total in the `equity` account is the amount of money we have in the bank.
It's not the same as our real-life equity (net worth), which would include large assets like homes, investment accounts, _etc_. -->

### Transfers to Savings Accounts

We can use the `equity` account to model situations where we want to set aside a part of our income for long term savings.

Suppose we want to save $500 every month.
If we actually transfer that much from our checking account to our savings account the database will have a transaction that records the transfer:
```plain
2024-01-01  monthly saving
    assets:savings                  $500.00
    assets:checking                $-500.00
```
This transfer involves two assets, but it doesn't say anything about the monthly budget.
We still need a way to record the fact that part of our income is being allocated to envelopes to use for expenses and part is going to long term savings.

That's where the `equity` account comes into play.
Simply add a credit to the budget transaction that shows the amount that was transferred to savings:

```plain
2024-01-02  fill envelopes                        ; budget:
    income:yoyodyne                $5000.00
    expenses:home                 $-2500.00
    expenses:car                  $-1000.00
    expenses:food                 $-1000.00
    equity:                        $-500.00       ; transferred to savings
```

> Note that we've updated the budget, changing the home expenses from $3000 to $2500 to make room for the savings transfer.

The `equity` line in the budget transactions serves two purposes:

* It makes sure the transaction is balanced, so we can still be sure every dollar has a job.

* It increases the balance of the `equity` account, just the way the credit in the transaction that initialized the account balances did.  So basically we're saying our equity has gone up by $500, which is consistent with the fact that we've added $500 to savings.

### Transfers from Savings Accounts

The previous section showed how to credit the `equity` account when transferring income to a savings account.  We can do the same thing, but in reverse, when we move money out of savings.

Suppose one of our savings accounts was earmarked for a trip to France and now we're ready to go.
We want to move money to our checking account so it can be used, either through direct purchases from checking or to eventually pay off credit card purchases.

There will be a transfer between the two accounts:
```plain
2024-03-15  going to France!
    assets:checking                $3000.00
    assets:savings                $-3000.00
```

But we also want to make sure that money ends up in the `travel` envelope:
```plain
2024-03-15  France savings to travel envelope        ; budget:
    equity:                       $3000.00
    expenses:travel              $-3000.00
```
Note how we're debiting `equity` (when we moved money to savings it was a credit), and the credit to the expense account is adding the money to the travel envelope (just like the credits in the budget transaction). 

**Important:**  This transaction should also be tagged so it is filtered out with other budget transactions when making reports that use the standard definitions of income and expense balance.
