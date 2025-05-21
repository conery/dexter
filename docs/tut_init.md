# Initialize the Database

After you have completed setting up account names in your account file you can create a new database.

To create the database for the tutorial project simply type
```shell
$ dex init --file accounts.csv
```

Dexter will find the name for the new database in the configuration file, create the new database, and add the accounts.

> _Note:_  You can use `accounts.journal` instead of `accounts,csv`.  They have the same definitions, just in different formats.  Dexter will figure out which format to use based on the file name extension.

You can use the `info` command to verify the database was created:
```shell
$ dex info

Databases                                                 
┏━━━━━━━━━━━━━━┳━━━━━━━━━┳━━━━━━━━━━━━━┳━━━━━━━┳━━━━━━━━━┓
┃ name         ┃ account ┃ transaction ┃ entry ┃ reg_exp ┃
┡━━━━━━━━━━━━━━╇━━━━━━━━━╇━━━━━━━━━━━━━╇━━━━━━━╇━━━━━━━━━┩
│ dev          │      26 │           2 │     4 │       0 │
└──────────────┴─────────┴─────────────┴───────┴─────────┘
```

The table will have one row for each database on the server.
Since this is the first Dexter database you have created you will see only one row.

You can also use the `select` command (described in detail later, in [Select Transactions](tut_select.md)) to print descriptions of the transactions.
With no command line options the command prints a table showing all transactions in the database:

```shell
$ dex --db dev select

Transactions                                                                                                                                      
┏━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━┓
┃ date         ┃ credit               ┃ debit                ┃       amount ┃ description                    ┃ comment         ┃ tags            ┃
┡━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━┩
│ 2024-12-31   │ equity               │ checking             │    $1,000.00 │ initial balance                │                 │                 │
│ 2024-12-31   │ equity               │ savings              │    $2,500.00 │ initial balance                │                 │                 │
└──────────────┴──────────────────────┴──────────────────────┴──────────────┴────────────────────────────────┴─────────────────┴─────────────────┘
```

This output shows the `init` command created two transactions to set up the initial balances in the two bank accounts, using the `balance` column in the CSV file.

<!-- The `select` command can also display the transactions in Journal format: -->

