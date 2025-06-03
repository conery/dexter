# `dex review`

#### Usage

```shell
$ dex review --help
usage: dex review [-h] [--fill_mode N]

options:
  -h, --help     show this help message and exit
```

The `review` command uses a command line interface to display unpaired postings one at a time.
The display shows the outline of a new transaction.
Some of the fields will be filled in automatically using information from an unpaired posting.
The rest must be supplied by the user to create a new posting, which is then combined with the existing posting to form a new transaction.

The only option is `--fill_mode`, which tells Dexter how to initialize the description field in the transaction.
The argument is a number between 0 and 2:

* 0 means "leave the field blank".  It will be displayed in the template as the "description", in italics, as a placeholder to remind users to fill it in.
* 1 means "copy the description from the posting".
* 2 means "copy the posting description and apply regular expressions".

The modes (and how they can be useful) are described in [Review Unpaired Entries](tut_review.md).

## Editing Operations

All operations at initiated by a single keystroke, as shown in the tables below.

> The notation &#8963;X is short for "control-X", _i.e._ hold down the control key when typing X.

### Navigation

If you want to skip a transaction you can hit the down or up arrow to move to the next or previous transaction.  

Dexter exits the loop after the last unpaired posting has been paired.

To exit before then type either &#8963;C or &#8963;D.
The next time you run `dex review` Dexter will resume where you left off.

| keystroke | operation | comment |
| --- | --- | --- |
| &uarr; | move to previous transaction | |
| &darr; | move to next transaction | |
| &#8963;C | exit | |
| &#8963;D | exit | |


### Field Selection

| keystroke | operation | comment |
| --- | --- | --- |
| &#8963;P | edit the description field | mnemonic: "p" is for "payee" |
| &#8963;N | edit the comment field | mnemonic: "n" is for "note" |
| &#8963;G | edit the tags field |  |
| &#8963;T | edit the account field | mnemonic: "t" is for "to" |

### Command Line Editing

**TBD**

