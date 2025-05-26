# Initialize the Database

To create the database for the tutorial project simply type
```shell
$ dex init --file accounts.csv
```

Dexter will find the name for the new database in the configuration file, create the  database, and add the accounts.

> _Note:_  You can use `accounts.journal` instead of `accounts.csv`.  They have the same definitions, just in different formats.  Dexter will figure out which format to use based on the file name extension.

You can use the `info` command to verify the database was created:
```shell
$ dex info

Databases                                                 
┏━━━━━━━━━━━━━━┳━━━━━━━━━┳━━━━━━━━━━━━━┳━━━━━━━┳━━━━━━━━━┓
┃ name         ┃ account ┃ transaction ┃ entry ┃ reg_exp ┃
┡━━━━━━━━━━━━━━╇━━━━━━━━━╇━━━━━━━━━━━━━╇━━━━━━━╇━━━━━━━━━┩
│ dev          │      18 │           2 │     4 │       0 │
└──────────────┴─────────┴─────────────┴───────┴─────────┘
```

The table will have one row for each database on the server.
Since this is the first Dexter database you have created you will see only one row.

That output shows there are two transactions in the database already.
Those are the transactions that set the starting balance of the checking and savings accounts.

You can also use the `select` command (introduced later, in [Select Transactions](tut_select.md)) to print descriptions of the transactions:

```shell
$ dex --db dev select

Transactions                                                                                                                                      
┏━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━┓
┃ date         ┃ credit               ┃ debit                ┃       amount ┃ description                    ┃ comment         ┃ tags            ┃
┡━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━┩
│ 2023-12-31   │ equity               │ checking             │    $1,000.00 │ initial balance                │                 │                 │
│ 2023-12-31   │ equity               │ savings              │    $2,500.00 │ initial balance                │                 │                 │
└──────────────┴──────────────────────┴──────────────────────┴──────────────┴────────────────────────────────┴─────────────────┴─────────────────┘
```

<!-- The `select` command can also display the transactions in Journal format: -->

> _**Note:** The initial balances are defined with the account names in `accounts.csv`.  For more information about what else can be put in this file see [Defining Accounts](accounts.md)._

