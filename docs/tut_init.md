# Initialize the Database

After you have completed setting up account names in your account file you can create a new database.

To create the database for the tutorial project simply type
```shell
$ dex init --file accounts.csv
```

Dexter will find the name for the new database in the configuration file, create the new database, and add the accounts.

> _Note:_  You can use `accounts.journal` instead of `accounts,csv`.  They have the same definitions, just in different formats.  Dexter will figure out which format to use based on the file name extension.


