# Expense Account Balance

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
    expenses:food                 $75.00
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
In these transactions we used a debit card at one restaurant and a credit card at the other:
```plain
2024-01-07  Chez Ray
    expenses:food:restaurant     $75.00
    assets:checking             $-75.00

2024-01-17  Burger Palace
    expenses:food:restaurant     $25.00
    liabilities:chase:visa      $-25.00
```

For budgeting purposes it doesn't matter which account was used for the credit (source) side of the transaction.
Whenever a transaction debits an expense account the envelope balance is updated.
After lunch at Burger Palace the food account will have -$1000 + $75 + $25 = -$900.
