# Dexter

Dexter is a command line application for tracking personal finances.
The key features are:

* double-entry bookkeeping

* a workflow that focusses on efficiency, with extensive use of command completion, operations triggered by single keystrokes, and predicting fields based on previous records

* a new budget model that implements zero-based budgeting within the double-entry bookeeeping framework, without requiring virtual transactions or other extensions

Several features in Dexter were inspired by Ledger and `hledger`.
Dexter stores account data and transactions in a NoSQL database, so it's not strictly a plain text accounting application, but it does support the `.journal` format used by those applications.
It's a straightforward process to import a journal to initialize a database, use Dexter's workflow to process a batch of CSV files downloaded from banks and credit card companies, and export the results to an updated journal.

## Current Status (April 2025)

Dexter is written entirely in Python.
It can be installed with a `pip` command that pulls the sources from the GitHub repo.

The only external dependence is MongoDB.
Before running Dexter it is necessary to start the MongoDB server running locally.

The workflow and budget model have been implemented and tested in an earlier project.
The current project is a rewrite and cleanup operation that is working through the scripts one by one, simplifying and improving the code and adding more unit tests.

The modules currently in the repo are sufficent to run all the examples described in [The Budget Model](budgets.md):

* initialize a new database by importing records; supports several formats, including plain text accounting `.journal` files
* export records in the database to `.journal` or other formats
* add records from CSV files downloaded from financial institutions
* use regular expressions and other techniques to form transactions based on pairs of debit and credit entries
* report generators to print account balances and expense statements
