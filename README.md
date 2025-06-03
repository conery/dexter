# Dexter

Dexter (Double-Entry Expense Tracker) is a collection of command line applications for managing personal finances.

Its main features are:

* the use double-entry bookkeeping to categorize expenses

* a workflow that focusses on efficiency, with extensive use of command completion, edit operations triggered by single keystrokes, and automatic fills based on patterns and previous records

* a new budget model that allows for zero-based budgeting entirely within the double-entry bookeeeping framework, without requiring virtual transactions or other extensions

* a database API that allows users to write their own scripts

Dexter is written entirely in Python and can be installed with a `pip` command that pulls the sources from the GitHub repo.

The only external dependence is MongoDB.

## Installation

### Dexter and Python Libraries

Dexter requires Python 3.13 or higher.

It has very few third party libraries (MongoEngine, Rich, and Click) but we recommend creating a virtual environment.

Activate the environment, then:
```bash
$ pip install git+https://github.com/conery/dexter.git
```

To verify Dexter was installed:
```bash
$ dex --help
```

### MongoDB

Install MongoDB and start a local server.
This command will test Dexter's connection to the server by printing a list of Dexter databases on the server:

```bash
$ dex info
```
(the table should be empty).

### Unit Tests (Optional)

If you download a copy of the source code, you can `cd` to the project directory and run unit tests:
```bash
$ 


## Documentation

## Tutorial Data

