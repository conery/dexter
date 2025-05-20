# Initialize the Database

After you have completed setting up account names in your account file you can create a new database.

To create the database for the tutorial project simply type
```shell
$ dex init --file accounts.csv
```

Dexter will find the name for the new database in the configuration file, create the new 

Specify the name of the file with `--file`.
The format of the file will be inferred from the filename extension, either `.csv` or `.journal`.

<!-- If the database exists already the command will print a warning and exit.
To replace an existing database use `--force`. -->

#### Example

To create a new database named `dev`...
