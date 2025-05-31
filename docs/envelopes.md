# Envelope Budgeting

Dexter not only keeps track of expenses, it also helps users who want to try to control their expenses by maintaining a budget.

The strategy we use is a familiar method called **Envelope Budgeting.**
The idea is that when we get paid we should put money into envelopes with labels like "groceries", "entertainment", _etc_,.
When we make a purchase, the money should come from one of those envelopes.
If we want to go to a baseball game but the entertainment envelope is empty it means we've already spent all the money we put aside for entertainment and should make other plans.

Putting cash in physical envelopes is apparently still a thing ([Envelope Budgeting: Simple Cash Control](https://www.moneyfit.org/envelope-budget/)) but of course when we use Dexter we're going to set up virtual envelopes.

But it's not obvious how to do this.
Real cash-filled envelopes are, like checking accounts, assets.
The intuitive approach would be to set up an additional set of asset accounts in our expense tracking system.
Some personal finance applications allow users to create virtual accounts to use for budgeting (or other uses).
But then each time an expense occurs we have to add a virtual transaction to update the envelopes.

The approach we use in Dexter seems paradoxical, but in fact it makes a lot of sense, and as we'll see it is also far simpler to manage.

The key idea:

> In Dexter **_envelopes are expense accounts._**

Our envelopes are not asset accounts, they are expense accounts.
In fact, with Dexter, **every expense account automatically becomes the envelope** for that expense category.

The question then becomes, "how do we allocate money to envelopes?"

The short answer is "by crediting the account."
To see why that might be the case, consider these two transactions.
The first is a purchase at a hardware store:
```plain
2024-04-21   Jerrys Home Improvement   ; drill, screwdriver set
    visa                         −$50.00
    household                     $50.00
```
Now suppose a few days later we decide to return one of the things we bought.
This leads to a new transaction:
```plain
2024-04-22   Jerrys Home Improvement   ; we have enough screwdrivers
    household                    −$20.00
    visa                          $20.00
```
Notice how the role of the two accounts is the opposite:
the original purchase has a debit to the expense account, but the return has a credit to that same account.
In double-entry bookkeeping:

* a purchase **debits** an expense account, **increasing** its balance
* a return **credits** the account, **decreasing** its balance

So the long answer to "how do we fill envelopes?" is that we add a new transaction at the start of each month that credits each of the expense categories:
```plain
2024-04-01   Fill envelopes
    groceries                    −$200.00
    household                    −$500.00
    entertainment                −$100.00
    ...
```
If each account starts out at $0 initially, that transaction sets the balance to a negative value.
Now each purchase is going to add to the balance, and as more purchases are made the balance gets closer and closer to $0.
When the balance hits $0 all the money has been spent from the envelope.

To get back to the hardware store example:

* the envelope was "filled" with -$500 on Apr 1
* the purchase on Apr 21 "removed" $50, so the updated balance is -$450
* the return on Apr 22 "put back" $20 by crediting the account, updating the balance to -$470.

But transactions need to be balanced, so now we have a new question: "where is all that money in the envelope fillig transaction coming from?"
That also has a short answer: income accounts.

The last line in the envelope-filling transaction is a debit to the source of income that we're putting in envelopes:
```
    income:salary                $5000.00
```

That also seems very unlikely.
Normally when an income account is used in a posting it's in a transaction that records salary or other income:
```plain
2024-04-22   Yoyodyne
    checking                   $5,000.00
    income:salary             −$5,000.00
```

So now we have a new interpretation for the balance of an income account:  when funds are transferred in to one of our asset accounts (like a deposit to our checking account) the balance of the income account decreases.
As we allocate money to envelopes the balance increases.
In fact, if it reaches $0 we can be sure that all of our income has been "given a job" and has been put in an envelope.

Earlier the claim was made that Dexter's budgeting method was made far simpler by using expense accounts for envelopes.
Now we can see why: the only transaction that needs to be added to manage envelopes is the one that fills the envelopes at the beginning of the month.
After that, every transaction automatically updates the envelope.

* if we use a credit card to buy dinner at a restaurant, the debit to the `restaurant` account increases the balance (takes money from the envelope)
* if we use Venmo to send money to a friend, and Venmo takes that money from our checking account, that transaction will also debit `restaurant`, and again takes money from the same envelope
* if our employer deposits money in our checking account as a reimbursement for a dinner, that transaction can credit `restaurant`, putting money back in the envelope

There is a lot to digest here, even for (maybe especially for) readers who are already familiar with double-entry bookkeeping.
An entire section of this documentation is devoted to Dexter's approach to budgeting ([Envelope Budgeting with Dexter](envelopes_dex.md)).

For now, these are the main ponts to take away from this short introduction:

* expense accounts can be used as virtual envelopes for money to use for the correponding expense category
* an envelope is "filled" by a tranaction that sets the account balance to a negative number
* a transaction that debits an expense account removes money from the envelope by increasing the balance, which moves it closer to $0
* when the balance goes over $0 it means the sum of all purchases exceeds the amount put in the envelope
