# Income Account Balance

When a database has a budget allocation transaction it changes how we interpret the balance for income accounts.

Currently your income transactions probably all have the same general form as the example shown above:
```plain
2024-01-02  paycheck
    assets:checking            $5000.00
    income:yoyodyne           $-5000.00
```
Unless there is a reason you have to return some income, all of the entries for the income account are credits and the balance keeps getting more and more negative.

Now consider what happens when we include the budget transaction:
```plain
2024-01-02  fill envelopes                        ; budget:
    income:yoyodyne                $5000.00
    expenses:home                 $-3000.00
    expenses:car                  $-1000.00
    expenses:food                 $-1000.00
```

That transaction, like every other transaction, should be balanced.
The sum of the credits to the expense accounts should match the amount debited to the income account.

So one way to look at this transaction is that the income is being divided among all the expense accounts:  the total over all credits (money put in envelopes) should equal the debit (the income amount).

### Giving Every Dollar a Job

After including the budget transaction, if the income account balance is not $0 it means something is wrong.

* If the balance is less than $0 it means there is left over income that was not distributed to an envelope.

* If the amount is greater than $0 it means the budget is off -- we're trying to allocate more money than we have.

When the balance is $0 we've successfully given every dollar a job.

**Note:**  "Give every dollar a job" does not mean "spend every dollar."  A monthly budget can include putting money into a savings account.  We'll see how to do that below, in [Using the Equity Account](#using-the-equity-account).

### COLA

One way you can end up with unallocated income is if one of your income sources gives you a raise.

A common workflow is to download CSV records from your bank, add them to the database, and print reports.
When the balance reports shows the income account has an amount less than $0 it's a signal to edit your budget to make sure it matches your new income.

Dexter's `fill` command creates a budget transaction automatically from one or more deposits.
It uses a budget table defined in the configuration table.
If a deposit is higher, due to a cost of living adjustment (COLA) or for some other reason, the transaction is unbalanced and the income account will have a positive balance.

### Interest Income

Another common occurrence is that your asset accounts will earn interest each month.

One way to deal with is to have a rule or a script that runs every month to compute the total earned in all accounts and insert a new budget transaction that allocates that amount to one of your envelopes:
```plain
2024-01-31  allocate interest income           ; budget:
    income:interest                $12.34
    expenses:bank                 $-12.34
```
I have an envelope named `bank` that I use for annual credit card fees, the fee for renting a safe deposit box, and other random charges, so I just put interest there to help pay fees when they crop up.
But of course you could put it in travel, restaurant, or any other place where it would be nice to have some "found money."

