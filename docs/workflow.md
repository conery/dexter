# Monthly Workflow

The standard workflow assumes transactions are saved in a database.
Each month a new batch of CSVs is downloaded, added to the database, and refined into a set of transactions.

Because the scripts that initialize a database can read `.journal` files from hledger there is an aternative workflow for users who just want to use Dexter to convert CSV files into transactions or for envelope budgeting.
In this workflow, a temporary database is created using account definitions, new records are loaded from CSV files, and the results are written back out in a `.journal` format that can be read by hldeger.
See [hledger Workflow](hledger.md) for details.


