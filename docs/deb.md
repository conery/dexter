# Double-Entry Bookkeeping

There are plenty of good descriptions of double-entry bookkeeping at other sites, including [GnuCash](https://gnucash.org/viewdoc.phtml?rev=5&lang=C&doc=guide), [Beancount](https://beancount.github.io/docs/the_double_entry_counting_method.html), and  [Accounting for Computer Scientists](https://martin.kleppmann.com/2011/03/07/accounting-for-computer-scientists.html).
This section is a quick overview of the basic ideas necessary to describe the philosophy behind Dexter.

## Accounts

An __account__ in a bookkeeping system is a source or a destination for money.

A __real__ account in the system corresponds to an real-world account like a bank account or credit card account.
They have specific identifiers (the name of the company, account number, _etc_) and, at any point in time, a balance that reflects the amount of money we own (in a bank account) or owe (to a credit card company).

The two main types of real accounts are __assets__, which we _own_, like checking and savings accounts, and __liabilities__, like credit cards and loans, which are things we _owe_.

A __nominal__ account is more abstract.
These accounts are used to model sources of __income__ and categories for __expenses__.
When we set up a bookkeeping system we define nominal accounts to suit our needs.

A good example of the flexibility we have in defining a nominal accounts is to consider how to define categories for monthly expenses.
We'll want set up accounts for the basic categories with names like `home`, `car`, `food`, and `entertainment`.
But if the goal is to do a better job of controlling monthly expenses a person might want to replace `food` with separate `groceries` and `restaurant` accounts, with the idea that the latter is a discretionary expense that can be controlled.
Most systems, including Dexter, allow accounts to be organized in a hierarchy, so we might have a generic `food` account along with subaccounts `food:groceries` and `food:restaurant`.

Income is also an abstraction.
There could just be one catch-all account named `income` that models all money that comes our way during a month, but a more useful structure would be to have different accounts for `salary`, `interest`, `tips`, _etc_.
Each person will set up their own income accounts depending on how they earn money.

## Transactions

Whenever we spend or earn money we want to record it as a __transaction__ in the bookkeeping system.

In the simplest kind of transaction there will be one source account and one destination account.
For example, when our paycheck is deposited in our bank account, the source account is `salary` and the destination account is `checking`.

When we make a purchase, the source account is where the funds are coming from, for exampe a checking account.
The destination is the expense account set up for the type of purchase.

Some more examples:

* if want to transfer some money to a savings account there would be a new transaction where the source is `checking` and the destination is `savings`.

* if we use our debit card to buy groceries there will be a transaction where the source is `checking` and the destination is `groceries`.

* if we pay for dinner using a credit card we need to add a transaction where the card account is the source and the `restaurant` account is the destination

* paying the credit card bill is another type of transfer, this time with `checking` account as source and the credit card account as destination.

Note that an account can be on either side of a transaction.
In some of these examples `checking` was the source account and in others it was the destination.

A transaction can have any number of sources or destinations.
As an example, suppose we buy $200 worth of stuff at Costco using our credit card.
If $150 of that was for food and the remaining $50 for toilet paper, laundry soap, and other household supplies, the transaction could have one source (the credit card) and two destinations (`groceries` and `home`).

## Terminology

In bookkeeping terminology, a source account is the _credit_ account and the destination account is the _debit_ account.

The components of a transaction are called _postings_ (or sometimes just "posts").
A posting has the name of an account, an amount, and an indication of whether the account is being used as the source (credit) or debit (destination).

Historically businesses that used double-entry accounting would keep one journal, or ledger, for each account.
When transactions were recorded, one posting was entered in the journal for the credit account and a matching posting was entered in the journal for the debit account.

With modern accounting software the records are commonly stored in the same file or database.
Here is how the Costco transaction from above might be shown in a text file that uses the **Journal format** of plain-text accounting applications (Dexter can also read and write files using this format):

```
2024-01-17  Costco
    groceries         $150.00      ; cheese, wine, cookies for party
    home               $50.00      ; TP, soap, misc household
    visa             $-200.00
```

The first line describes the transaction itself.
Below that are three postings, showing the account name and amount.
In a Journal file the sign of the amount indicates whether the posting is a debit (positive amount) or credit (negative) amount.
In the case $200 is coming from the `visa` account, with $150 going to `groceries` and $50 going to `home`.

## Transactions Should Be Balanced

The heart of double-entry bookkeeping is the reuirement that each transaction should be balanced:  the sum of the debits must match the sum of the credits.

> _TBD: examples of errors, how DEB helps find them_


