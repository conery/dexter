# Recap

That's the end of the tutorial.
In the previous sections you created a new database and worked through the main steps in Dexter's monthly financial tracking workflow:

* Import records downloaded from banks and card companies. Each record is saved as a new credit or debit posting in the database.
* Use Dexter's "pair" operation to automatically create as many transactions as possible.  New transactions are formed by matching two postings, one a credit and the other a debit.  In some cases both postings are already in the database, in others Dexter uses regular expressions to infer a new posting.
* Use a command line based read-eval-print loop to pair the remaining postings.  This step is designed to do as much as possible with a few keystrokes.
* Use additional commands to select and view transactions based on attributes (date, amount, description, _etc_) or print reports with account balances.

There are several more things Dexter can help with.
They are described in User Documentation section of this website:

* Back up or restore a database, using one of two formats.  A "dox file" is basically a JSON file with one line per record.  The other uses MongoDB commands to make a binary file.
* Export records to a Journal file so they can be incorporated into Ledger or `hledger`.
* Edit or delete records, either individually or in bulk.
* Additional report types.
* Commands that reconcile credit card and bank statements, making sure the records in a database match records reported by a financial institution.

> _**Note:** Some of these operations are working in my old SQLite-based scripts but haven't yet been converted to work with the new database schema._
