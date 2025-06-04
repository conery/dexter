# Welcome to Dexter

Dexter (Double-Entry Expense Tracker) is a collection of command line applications for managing personal finances.

Its main features are:

* the use of double-entry bookkeeping to categorize expenses

* a workflow that focusses on efficiency, with extensive use of command completion, edit operations triggered by single keystrokes, and automatic fills based on patterns and previous records

* a new budget model that allows for zero-based budgeting entirely within the double-entry bookeeeping framework, without requiring virtual transactions or other extensions

* a database API that allows users to write their own scripts

Dexter is written entirely in Python and can be installed with a `pip` command that pulls the sources from the GitHub repo.

The only external dependence is MongoDB.
Before running Dexter it is necessary to start the MongoDB server running locally.

> _A planned update is to allow the option of connecting to a SQLite database._

The overview section is recommended reading before installing Dexter and trying the examples in the tutorial.

