# History

## The Evolution of Dexter

The first program I wrote to keep track of personal expenses was written in Pascal and ran on an operating system named CPM.

OK, that's too much history.

Fast forward:  after trying several commercial programs and writing my own GUI applications I've come back full circle to a command line API.
My current workflow uses a set of Python scripts that save transactions in a SQLite database.
I moved away from a monolithic GUI because independent scripts are more effective if each one can focus on its part of the workflow.
Using the command line means I can take advantage of command history, completions, and other features.

<!-- The most recent iteration of my Python workflow incoporates the envelope budgeting technique described below.
I've used it successfully for two years now and decided it was worth sharing. -->

The GitHub repo has a rewrite of my current scripts.
My goals were to

* transition from SQLite to a NoSQL database (mongodb)
* clean up and document each script
* create a more extensive set of unit tests

As of May 2025 the scripts in the repo are sufficient to carry out the main steps in my monthly bill-paying workflow.
There are bound to be errors and incomplete sections, so the software is still in pre-release (beta).

## Current Status (May 2025)

The modules currently in the repo are sufficent to run all the examples described in [The Budget Model](budgets.md):

* initialize a new database by importing records; supports several formats, including plain text accounting `.journal` files
* export records in the database to `.journal` or other formats
* add records from CSV files downloaded from financial institutions
* use regular expressions and other techniques to form transactions based on pairs of debit and credit entries
* report generators to print account balances and expense statements
