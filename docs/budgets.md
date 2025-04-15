# Envelope Budgeting with Double Entry Bookkeeping

In this section we introduce a new approach to envelope budgeting in a double-entry accounting system.

The philosophy is to allocate income to "envelopes" or "buckets" for different expense categories.
When an expense is incurred, it should be paid for out of the corresponding envelope.

The idea is that when we go to make a purchase and there is not enough money in an envelope we should rethink our plans.
If the envelope labeled "restaurants" has only $20 and there are still two weeks before the next budget period we should probably not go out to that fancy new restaurant tonight.

A related method, known as zero-based budgeting, suggests users allocate all of their income to envelopes.
To use a phrase from [YNAB](https://www.ynab.com/), the goal is to "give every dollar a job."

The budgeting process should help users take the long view by allowing funds in an envelope to roll over to next period.
If we know we're going to need new tires for the car some time in the next year we should add an extra $100 to the car envelope every month so it will be there when we need it.

Of course, we're not taping real envelopes to our refrigerators.
Our envelopes are managed by our personal finance software and have a lot more flexibility.
For one thing, we can allow a negative balance.
If we only have $400 in the car expense envelope but can't delay the tire purchase and need to pay $600 this month it's not a problem.
The car envelope will drop to -$200, but we know it will build back up in the coming months.

Integrating envelope budgeting with double-entry bookkeeping is not simple.
Several people have shared their envelope budget process on the discussion boards for GnuCash and plain text accounting applications ([Budgeting - plaintextaccounting.org](https://plaintextaccounting.org/Budgeting)).
These typically involve setting up new asset accounts to represent envelopes and virtual transactions to coordinate expenses and envelopes.

Our method is much simpler.
We don't require any new accounts or any type of virtual transactions.
A single transaction at the beginning of the month will fill envelopes, and after that all purchases automatically reduce the available funds in the corresponding envelope.

## Account Balances

Before we introduce budget transactions we should review how account balances are computed.

In double-entry bookkeeping the **balance** of an account is the sum of the inflows (debits) minus the sum of the outflows (credits).

Here are a few example transactions (written in the Journal format used by `hledger` and other plain text accounting applications):

<!--codeinclude-->
[intro journal](./demo/demo-1-intro.journal)
<!--/codeinclude-->

In a journal file the signs on the amounts indicate the direction the money flowed:  `+` for a debit and `-` for a credit.

The first transaction is for our monthly paycheck.
It debits (adds to) the checking account, and credits an income source.

The next two transactions show we ate at a restaurant and paid for it using our checking account (either a paper check or a debit card), then bought some tools at a hardware store, also directly from the checking account.
In both cases the negative amount means funds moved out of the checking account and the positive amount means the money was moved into one of the expense accounts.

Because the Journal format uses positve numbers for debits (inflows) and negative numbers for credit (outflows) all we need to do to compute a balance for an account is add the amounts on all lines that name the account.  Looking at the lines above, the three lines that refer to `assets:checking` have amounts $1000, $-75, and $-100, so the balance is $875.

In the examples above the expense account was debited, but it's worth noting that a transaction can credit an expense account.
For example, suppose that lunch at the restaurant was with a friend, and the next day our friend used Venmo to reimburse us for their share.
On our bank statement that will show up as a deposit into our bank account.
The best way to represent this is with a transaction that debits the checking account (it's an inflow into the account) and credits the expense account that was used for the original purchase:

```plain
2024-01-08  venmo from Sam
    assets:checking                 $35.00
    expenses:food:restaurant       $-35.00
```

This transaction has an impact on the balance of both accounts: the checking account now has $875 + $35, or $910, and the restaurant account has $75 - $35, or $40.

## Budget Transactions

The paycheck transaction shown above deposited $5000 in our bank account, and we want to distribute all of it to envelopes, using the following budget:

| Expense Category | Amount | Comment |
| ---- | ----- | ----- |
| Home | $3000 | rent, household items, _etc_ |
| Car  | $1000 | payment, fuel, misc expenses |
| Food | $1000 | groceries, restaurants |

The key idea behind our approach is to use **_expense accounts_**, not asset accounts, to represent envelopes.

> [!NOTE] Envelopes = Expense Accounts
> Envelopes are not simply _associated with_ expense accounts, they _are_ expense accounts.

The transaction below, which we call a **budget allocation transaction**, allocates funds to envelopes using the budget shown above.
Note that it _debits income accounts_ and _credits expense accounts_.
The credits are how we model the process of adding money to the envelope, and the debits are a record of where that money came from.

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
For example, when that credit is combined with the $100 debit at the tool store shown earlier the home account balance is -$3000 plus $100, for a total of -$2900.
But here also there is a method to our madness, to be explained shortly.

Before we get to the explanations, though, there is an important point:

> **Budget transactions are easily ignored.**

It's very easy to recover the original meanings of the balance of income and expense accounts by simply not including budget transactions in balance calculations.

Dexter's expense report uses both definitions of when computing the balance on expense accounts:
```bash
$ tbd...
```

Budget transactions can also be used in `hledger` and other plain text accounting applications.
See [TBD](tbd) for ideas of how to organize journals with budget transactions and examples of `hledger` commands to print reports with and without budgets.

<!-- An `hledger` user who wants to use this budgeting scheme has several options for controlling when budget transactions are part of the journal:

* Put budget transactions in a separate file, and add a line to the main file that includes the budget transaction file.  Commenting out the include statement tells `hledger` to ignore the budget.

* Put a tag on each budget transaction (the example above has a `budget:` tag).  When running an `hldeger` report command use a query that selects all transactions or one that filters out transactions with a `budget:` tag. -->

## Expense Account Balance

The credits in a budget transaction have the same effect on the account as the credits in the Venmo example shown earlier.
In both cases, the transaction decreases the balance in the account.

A budget transaction at the beginning of the month sets a large negative balance on the account.
For example, these are the credits from the example shown above:
```plain
    expenses:home                 $-3000.00
    expenses:car                  $-1000.00
    expenses:food                 $-1000.00
```
In this case we're setting the home balance to -$3000 and the car and food balances to -$1000.

As purchases are recorded, any transaction that debits an expense will add a positive amount.
The dinner at the restaurant debited the food account for $75:
```plain
    expenses:food:restaurant     $75.00
```
The balance increased (became less negative) and now sits at -$925.

For any account, as long as the balance stays negative spending is within the budget.
But as soon as it crosses over into being positive we have spent more than the allocation.

### The Debit Card Analogy

A rough analogy is to think of an expense account as **pre-paid debit card**.
At the beginning of a month the card is "loaded" with the budget amount for that category.
Then throughout the month as the card is used for purchases the balance gets lower and lower.

There are (at least) two problems with this analogy.
First, the balance on a real debit card is a positive number, and using it for transactions lowers the balance.
In our expense accounts the "polarity" is reversed.
Adding money decreases the balance, and spending money increases it.

The second is that our envelopes are expense accounts, but in real life a prepaid debit card is an asset.
A real envelope full of cash has an objective value that lets it be traded or sold, while our expense accounts are abstractions (this is discussed more below in the section on [Nominal Accounts](#nominal-accounts)).

In spite of these flaws the basic idea is similar: initialize the card/account with an amount that estimates how much we want to spend, and as we use the card/account the balance works toward $0, at which point we are out of funds.

### Excess Spending

Running out of funds is not an issue.
If a balance goes positive there is nothing that prevents additional transactions from debiting the account again.

Suppose the car account has a balance of -$400 (_i.e._ there is $400 in the car envelope).
Buying tires for $600 will debit the account for that amount, and now the balance will be +$200.
We can still buy gas and make other transactions that debit the account, those transactions will just push the balance higher.

### Automatic Rollover

One of the important goals for our budgeting process was to be able to carry over any money left in an envelope so it is available for the following month.

Using expense accounts to model envelopes gives us this ability automatically.
Any balance in an expense account -- positive or negative -- is there at the start of the next budget period.

To continue the car example from the previous section, suppose the final balance at the end of the month is +$350.
The budget transaction for the new month will include a credit for $1000, and the balance is negative again, at -$650. 

### Purchases Can Be Made from Any Account

When we eat dinner at a restaurant we have a choice of how to pay for it.
Typically we use a debit card (the modern equivalent of writing a check) or one of our credit cards.
The transactions will look something like this:
```plain
2024-01-07  Chez Ray
    expenses:food:restaurant     $75.00
    assets:checking             $-75.00

2024-01-17  Burger Palace
    expenses:food:restaurant     $25.00
    liability:chase:visa        $-25.00
```

For budgeting purposes it doesn't matter what account was used for the credit (source) side of the transaction.
Whenever a transaction debits an expense account the envelope balance is updated.
After lunch at Burger Palace the food account will have -$1000 + $75 + $25 = -$900.

## Income Account Balance

When a database has a budget transaction it changes how we interpret the balance for income accounts.

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
2024-01-31  allocate interest income    ; budget:
    income:interest                $12.34
    expenses:bank                 $-12.34
```
I have an envelope named `bank` that I use for annual credit card fees, the fee for renting a safe deposit box, and other random charges, so I just put interest there to help pay fees when they crop up.
But of course you could put it in travel, restaurant, or any other place where it would be nice to have some "found money."

## Adjustments to Envelopes

Envelopes are eventually going to have balances -- positive or negative -- that we don't like.

As an example, suppose we have a run of bad luck with the car.
In addition to new tires, we had a higher than expected repair bill and other expenses, so now the balance in the `car` expense account is +$1000, meaning the envelope is $1000 overdrawn.

Here are some ways to deal with the situation.

* Do nothing.  Trust that the amount set aside for the car budget will eventually resolve the situation.

* Realize we are not allocating enough for car expenses. Adjust the budget so that in future months we put more into the car and less someplace else.

* Do a one-time transfer from another envelope.

As an example of the third option, suppose we have extra money in the `home` envelope because we haven't had as many home expenses as we budgeted for, and we're willing to move some of the excess over to the `car` envelope.
This transaction will transfer $1000 from `home` to `car`:
```plain
2024-02-28  move $1K from home to car            ; budget:
    expenses:home                  $1000.00
    expenses:car                  $-1000.00
```

Note that the signs on the amounts are not intuitive: we are not "adding to" `home` by "taking from" `car`.
Just the opposite, in fact.
The debits and credits on this transaction need to be consistent with other transactions that involve these accounts:

* the positive amount on the debit to the `home` account is similar to transactions that debit the home account in a purchase, where it means "take this amount from the envelope"

* the credit to the `car` account, indicated by the minus sign, is comparable to credits in other transactions, for example if we return a purchase or when when money is allocated by a budget transaction; it means "we are adding this much money to the envelope"

**One other important note:** this transaction should have a `budget:` tag to make sure it is not included in reports that use the traditional definition of the expense account balances.

## Using the Equity Account

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

In this situation, the total in the `equity` account is the amount of money we have in the bank.
It's not the same as our real-life equity (net worth), which would include large assets like homes, investment accounts, _etc_.

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

**Important:**  This transaction should also be tagged `budget:` so it is filtered out with other budget transactions when making reports that use the standard definitions of income and expense balance.

## Nominal Accounts

The literature on double-entry bookkeeping distinguishes between two types of accounts.

Assets and liabilities are **real accounts**.  They have counterparts that exist in the real world, outside your accounting system.
They are things like checking and savings accounts at a bank, mortgages and car loans, or credit card accounts.
When we download a CSV file from a financial institution the records in the file become debits or credits to real accounts in our database.

Income and expenses are **nominal accounts**.
These accounts do not have counterparts in the real world.
Their role is to help us organize our transactions.
We create these accounts to match our goals.

As an example of why income is nominal, consider how we might classify a monthly paycheck.
We could have just one account named `income`.
But if we have multiple sources of income -- two jobs, or a side gig selling crafts on Etsy -- it might be worthwhile distinguishing between them and having accounts with names like `income:yoyodyne` for paychecks (using the name of the company) and `income:etsy` for internet sales.

Expenses are even more flexible.
Do we have one general account named `food`?
Or do want to have different accounts for the different ways we spend money on food, _e.g._ `groceries` and `restaurants`?
Or maybe we could better track expenses if we had a hierarchy:  `food:groceries`, `food:restaurants`, `food:snacks`, and so on?
And what about food we buy when travelling?
Do we have `travel:meals` along with the `food` accounts?

The bottom line is that you create nominal accounts to best fit your goals for tracking your own personal finances.

### Budget Transactions Use Nominal Accounts

It's worth pointing out that the budget transactions we discussed above -- allocating funds to envelopes and moving funds between envelopes -- involve only nominal accounts.

A budget plan is based on your needs and your preferences.
The decisions of which money to allocate and what the funds are to be used for are completely in your hands.

It's only natural that the debit and credit accounts in budget transactions are all nominal accounts, which are also under your control.

## Recap

> [!NOTE] Envelope Budgeting in Dexter
>
> * Envelopes are **expense** accounts, not assets.
>
> * When a budget transaction fills envelopes it **credits expense accounts** and **debits income accounts**.
>
> * A transaction that debits an expense account automatically uses funds from that envelope; no additional transactions are required.
>
> * The balance of an expense account represents the amount of money in the envelope.
>
> * Budget transactions lead to a new meaning for the balances of expense and income accounts, but it's easy to filter out these transactions to recover the traditional meanings.
