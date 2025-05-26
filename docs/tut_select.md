# Select Transactions

Before we continue with the expense tracking workflow let's take a short detour to introduce the `select` command.

The general form of this command is
```shell
$ dex select C1 C2 ...
```
where the items following the word "select" are **constraint options**.
Constraints can specify dates, account names, description patterns, and many other attributes of transactions.

If no constraints are given Dexter prints all transactions in the database:
```shell
$ dex select

Transactions                                                                                                                                      
┏━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━┓
┃ date         ┃ credit               ┃ debit                ┃       amount ┃ description                    ┃ comment         ┃ tags            ┃
┡━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━┩
│ 2024-04-01   │ checking             │ restaurant           │       $70.00 │ Check #153: Glenwood           │                 │                 │
│ 2024-04-02   │ checking             │ mortgage             │    $1,000.00 │ Mortgage                       │                 │                 │
│ 2024-04-02   │ visa                 │ expenses:car         │        $5.00 │ Wash-it Express                │                 │                 │
...
```

The complete list of constraints and other options can be found in [`dex select`](dex_select.md).
In this section we'll just show a few that will be useful for exploring our initial set of transactions.

## Date Ranges

Use `--start_date` or `--end_date` (or both) to limit the set of results to a particular range of dates.
```shell
$ dex select --start_date 2024-04-21 --end_date 2024-04-22

Transactions                                                                                                                                      
┏━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━┓
┃ date         ┃ credit               ┃ debit                ┃       amount ┃ description                    ┃ comment         ┃ tags            ┃
┡━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━┩
│ 2024-04-21   │ visa                 │ household            │       $50.00 │ Jerry's Home Eugene            │                 │                 │
│ 2024-04-22   │ visa                 │ restaurant           │       $50.00 │ Hey Neighbor                   │                 │                 │
│ 2024-04-22   │ visa                 │ yard                 │      $100.00 │ Lane Forest Products           │                 │                 │
│ 2024-04-22   │ yoyodyne             │ checking             │    $3,000.00 │ Yoyodyne                       │                 │                 │
│ 2024-04-22   │ checking             │ utility              │      $100.00 │ AT&T                           │                 │                 │
│ 2024-04-22   │ household            │ visa                 │       $20.00 │ Jerry's Home Eugene            │ return          │                 │
└──────────────┴──────────────────────┴──────────────────────┴──────────────┴────────────────────────────────┴─────────────────┴─────────────────┘
```

## Amounts

We can use `--amount` to specify an exact amount, in which case Dexter will print transactions only if they have this amount, or `--min_amount` and `--max_amount` to specify ranges.
```shell
$ dex select --max_amount 10.00

Transactions                                                                                                                                      
┏━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━┓
┃ date         ┃ credit               ┃ debit                ┃       amount ┃ description                    ┃ comment         ┃ tags            ┃
┡━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━┩
│ 2024-04-02   │ visa                 │ expenses:car         │        $5.00 │ Wash-it Express                │                 │                 │
│ 2024-04-30   │ interest             │ checking             │        $0.68 │ Interest                       │                 │                 │
│ 2024-04-30   │ interest             │ savings              │        $1.59 │ Interest                       │                 │                 │
└──────────────┴──────────────────────┴──────────────────────┴──────────────┴────────────────────────────────┴─────────────────┴─────────────────┘
```

## Accounts

TBD

## Entries

The `--entry` option tells Dexter to print individual postings instead of transactions.
Most of the other options, for dates, amounts, _etc_, are make sense for postings.

```shell
$ dex select --entry --account food --full

Entries                                                                                                                       
┏━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━┓
┃ date         ┃ account                   ┃          amount ┃   column   ┃ description                    ┃ tags            ┃
┡━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━┩
│ 2024-04-01   │ expenses:food:restaurant  │          $70.00 │   debit    │ repl Check # 153: Completed/C… │                 │
│ 2024-04-03   │ expenses:food:restaurant  │          $35.00 │   credit   │ repl Transfer from Venmo/VENM… │                 │
│ 2024-04-12   │ expenses:food:groceries   │          $65.00 │   debit    │ repl HATCH CHILE MARKET        │                 │
│ 2024-04-22   │ expenses:food:restaurant  │          $50.00 │   debit    │ match TST* HEY NEIGHBOR - TBD  │                 │
│ 2024-04-23   │ expenses:food:groceries   │          $15.00 │   debit    │ match Everyone's Market/EVERY… │                 │
│ 2024-04-24   │ expenses:food:groceries   │          $15.00 │   debit    │ match NEWMAN'S FISH COMPANY    │                 │
│ 2024-04-26   │ expenses:food:groceries   │          $15.00 │   debit    │ match LONGS MEAT MARKET        │                 │
└──────────────┴───────────────────────────┴─────────────────┴────────────┴────────────────────────────────┴─────────────────┘
```

