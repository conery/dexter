# Adjustments to Envelopes

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

**One other important note:** this transaction should be tagged to make sure it is not included in reports that use the traditional definition of the expense account balances.

> Dexter can import transactions from a Journal file.  In those files tags use the Ledger/hledger format of a tag name followed by a colon.  In the database and in shell commands tags are denoted by a hash tag before the tag name.
