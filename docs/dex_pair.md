# `dex pair`

#### Usage

```shell
$ dex pair --help
usage: dex pair [-h]

options:
  -h, --help  show this help message and exit
```

When postings created by importing financial transactions are saved by the `import` command Dexter tags the new postings with an `#unpaired` tag.

The `pair` command fetches all of the unpaired postings and tries to find matches for them, as described in [Pair Entries](tut_pair.md).

* two parts of a transfer can be paired to form a new transaction, using one part as the credit and the other as the debit

* it a posting matches a regular expression Dexter can create a new posting and form a new transaction with both postings.

The only command line options are the general options for all commands.
For example, to run `pair` in preview mode to have it print a description of the new transactions instead of adding them to the database:

```shell
$ dex --preview pair
```
