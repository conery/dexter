# Fill Envelopes

This report shows us how much we spent in each expense category:

![expenses before fill](images/fill.report.before.png)

The total in each category is the net amount -- the sum of debits (inflows) minus the sum of credits (outflow).
We can see that in detail in the `restaurant` category:

![restaurant expenses before fill](images/fill.restaurant.before.png)

In this section we are going to add the budget transaction that fills the   envelopes for each expense category.
What we will see is that the budget transaction changes the meaning of expense account balances: when that transaction is added, the balance is interpreted as "the amount of money left in the envelope" ([Envelope Budgeting](envelopes.md)).

> _**Note:**  In the current version of Dexter budget transactions are added to the database by an `import` command.  In future versions there will be a `fill` command that automates several of the steps described here._

## Create the Budget Transaction

Use a text editor to create a new transaction in Journal format.

* The first line should have the transaction date and a brief description (and optionally a comment with extra information).
* The second line should have a posting with the name of an income account that has money we want to distribute to envelopes adn the amount of money we want to distribute
* The remaining lines will have the names of expense accounts and the amount of money we want to put in the envelopes for those accounts.

Here is the transaction to use for the tutorial project.
It allocates most of the monthly paycheck from Yoyodyne (which was for $5,000)  to the four expense categories:

```plain
2024-01-02  Fill envelopes                     ; Apr
    income:yoyodyne             $4700.00
    expenses:car                -$700.00
    expenses:entertainment      -$200.00
    expenses:food               -$600.00
    expenses:home              -$2200.00
```

That transaction is in a file named `fill.apr.journal` in the project directory.
