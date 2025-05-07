# Envelope Budgeting with Dexter

[Envelope budgeting](https://en.wikipedia.org/wiki/Envelope_system) is a systen where income is allocated to "envelopes" or "buckets" for different expense categories 
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
A single **budget transaction** at the beginning of the month will fill envelopes, and after that all purchases automatically reduce the available funds in the corresponding envelope.

