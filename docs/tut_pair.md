# Pair Transactions

Now that the database has regular expressions we can run the `pair` command.

As usual, we recommend doing a preview first:
```shell
$ dex --pre pair
```

## Output Tables

The preview output will have three sections.  The first is a list of new transactions that will be made as a result of a successful match with a regular expression:
```plain
Matched (38)
2024-04-30   visa       medical               $10.00   Essential Phyiscal Therapy    
2024-04-30   visa       alice                 $25.75   Gist Yarn                     
2024-04-29   visa       restaurant             $9.15   Burrito Boy  
...
```

This is exactly what we want from the regular expressions.
Each of these lines is a transaction that created by pairing a posting based on a CSV record from `chase.csv` with a new posting for an expense category.

There are two column names on each line.
The first is the credit (source) account, and the second is debit (destination) account.
So first line shows a charge on the Visa card to pay for a medical expense.

It's worth mentioning that while most records in the CSV file are purchases, and thus credits to the account, some will be debits, and the regular expression process correctly handles these situations.
Here is an example from later in that output section:
```plain
2024-04-30   interest   savings                $1.89   Interest                      
```
That posting came from `savings.csv`, and corresponds to a deposit into that account.
The record in the CSV file was a debit, and the algorithm paired it with a credit to `income:interest`.

The second section shows transfers, _i.e._ new transcations that were formed by matching the two ends of a bank transfer or card payment.
Our sample data has one of each:
```plain
Transfers (2)
2024-04-09   checking   visa             $2344.50   Chase Payment       
2024-04-05   checking   savings           $300.00   Transfer Monthly
```

Finally, the `pair` command prints a list of postings that did not match regular expressions:
```plain
Unmatched (15)
visa      AMZN Mktp US*ZQ3EI9M73
visa      SP TERRITORIAL SEED CO
visa      SQ *MOUNTAIN ROSE HERBS M
...
```

## Optional:  Update the Regular Expressions

There are different kinds of postings in the unmatched section.
The first line is for a purchase at Amazon.com.
Amazon doesn't give us any information about what that purchase was, so we have no way of writing a regular expression rule to fill in the expense category.
We'll have to deal with this manually later in the workflow.

The second line is for a company named Territorial Seeds.
In this case it might be possible to write a new rule.
If you do a lot of business at a company it would be worthwhile taking some time to add a new rule.
In this case we would make a rule saying "every purchase at Territorial Seeds should be to `expenses:home:garden`."

You can find more information about how to create and test new rules in [Regular Expressions](regexp.md).
A suggested workflow, especially for the first few months you use Dexter, is to run `pair` in preview mode,
scan the output to find new rules to add, update `regexp.csv` and import it again, and then run `pair` again.

## Make New Transactions

When you're ready to actually create the new transactions, run the command again, without the `--preview` option:
```shell
$ dex pair
```

Run the `info` command again to see the updated state of the database:
```plain
$ dex --db dev info

Databases                                                 
┏━━━━━━━━━━━━━━┳━━━━━━━━━┳━━━━━━━━━━━━━┳━━━━━━━┳━━━━━━━━━┓
┃ name         ┃ account ┃ transaction ┃ entry ┃ reg_exp ┃
┡━━━━━━━━━━━━━━╇━━━━━━━━━╇━━━━━━━━━━━━━╇━━━━━━━╇━━━━━━━━━┩
│ dev          │      26 │          42 │   100 │      40 │
└──────────────┴─────────┴─────────────┴───────┴─────────┘
```

Our database is growing -- we have several new postings and transactions!
