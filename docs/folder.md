# Create Your Project Directory

The example data for this tutorial is in an archive that can be downloaded from the GitHub repo:
```plain
URL
```

When you expand the archive you will have a new directory named `Finances` with the following structure:
```plain
Finances/
├── accounts.csv          -- account names used to initialize the database
├── accounts.journal      -- same, but in an alternate format
├── dex.toml              -- Dexter configuration file
├── Downloads             -- directory for CSV records from financial institutions
│   ├── apr
│   └── may
└── regexp.csv            -- regular expressions used by pair command
```

We refer to this folder as a **project directory**.
When you start working with your own data we recommend you create your own project directory with the same structure.

* The configuration file has some important information you will need to define.
* You will need only one account definition file.  There are two here to show examples of the two formats Dexter recognizes.
* Regular expressions have patterns that help automatically assign expense categories when CSV files downloaded from banks and card companies are imported.
* The Downloads folder is where you will save those CSV files.

## Activate the Virtual Environment

One of the main reasons for creating a project directory is so that you can easily activate the Python virtual environment where Dexter was installed.
After you expand the archive, `cd` to the top level folder and type this command:
```shell
$ pyenv local dexter
```
Now whenever you `cd` to this folder the virtual environment will be activated automatically and you will be able to type shell commands that run Dexter.

## Example Data

The account definitions and the sample CSV files are distilled from from real data.

To keep things simple, there is one checking account, one savings account, one credit card, and only four budget categories (the complete list of accounts is shown below).
The expense categories are diverse enough to be able to illustrate the budget model and how subaccounts work, but with only four categories it is not as complex as a real set of categories will be.

The Downloads folder has two subfolders, named for months.
The `apr` folder has hypothetical transactions for the three accounts for the month of April, 2024, and the `may` folder has the corresponding files for May, 2024.

<!-- One thing notably absent from the example directory is a file for transactions.
That's because Dexter stores transactions and other work products in a database.
After you define your account names you will use a command that initializes a new database. -->

## Accounts

Here is a complete list of all the accounts used in the tutorial data.

| Category | Full Name | Abbreviated Name |
| --- | --- | --- |
| Assets | assets:bank:checking | checking |
|  | assets:bank:savings | savings |
| Expenses | expenses:car | |
|  | expenses:car:payment | |
|  | expenses:car:fuel | fuel |
|  | expenses:entertainment | entertainment |
|  | expenses:food | |
|  | expenses:food:groceries | groceries |
|  | expenses:food:restaurant |restaurant |
|  | expenses:home | |
|  | expenses:home:mortgage | mortgage |
|  | expenses:home:household | household |
|  | expenses:home:utility | utility |
|  | expenses:home:yard | yard |
| Income | income:yoyodyne | |
|  | income:interest | |
| Liabilities | liabilities:chase:visa | visa |
