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
│ 2024-04-02   │ checking             │ bob                  │      $118.99 │ Downtown Athletic Club         │                 │                 │
│ 2024-04-02   │ checking             │ medical              │      $232.03 │ Medical Insurance              │                 │                 │
│ 2024-04-02   │ checking             │ mortgage             │    $1,037.24 │ Rocket Mortgage                │                 │                 │
...
```

The complete list of constraints and other options can be found in [`dex select`](dex_select.md).
In this section we'll just show a few that will be useful for exploring our initial set of transactions.

## Date Ranges

Use `--start_date` or `--end_date` (or both) to limit the set of results to a particular range of dates.
```shell
$ dex select --start_date 2024-04-07 --end_date 2024-04-13

Transactions                                                                                                                                      
┏━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━┓
┃ date         ┃ credit               ┃ debit                ┃       amount ┃ description                    ┃ comment         ┃ tags            ┃
┡━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━┩
│ 2024-04-08   │ checking             │ medical              │       $15.08 │ CSV                            │                 │                 │
│ 2024-04-09   │ checking             │ visa                 │    $2,344.50 │ Chase Payment                  │                 │                 │
│ 2024-04-10   │ visa                 │ shared               │       $39.95 │ Cooks Illustrated              │                 │                 │
│ 2024-04-13   │ visa                 │ shared               │       $15.99 │ Prime Video                    │                 │                 │
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
│ 2024-04-05   │ visa                 │ shared               │        $7.00 │ Disney Plus                    │                 │                 │
│ 2024-04-06   │ visa                 │ alice                │        $3.00 │ Wikimedia                      │                 │                 │
│ 2024-04-22   │ checking             │ charity              │        $5.00 │ OPB                            │                 │                 │
...
```

## Accounts

TBD

## Entries

```shell
$ dex select --entry --tag '#unpaired'

Entries                                                                                                                       
┏━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━┓
┃ date         ┃ account                   ┃          amount ┃   column   ┃ description                    ┃ tags            ┃
┡━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━┩
│ 2024-04-01   │ checking                  │         $300.00 │   credit   │ Check # 152: Completed/Check … │ #unpaired       │
│ 2024-04-01   │ visa                      │           $3.00 │   credit   │ WASH-IT EXPRESS                │ #unpaired       │
│ 2024-04-03   │ checking                  │         $203.00 │   credit   │ KAYENTA CHEV-XX6444 JUNCTION … │ #unpaired       │
│ 2024-04-03   │ checking                  │         $503.00 │   credit   │ HIGHWAY 160 HIGHWAY 160 Kayen… │ #unpaired       │
...
```

