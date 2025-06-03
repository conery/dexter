# `dex select`

#### Usage

```shell
$ dex select --help
usage: dex select [-h] [--entry] [--date D] [--start_date D] [--end_date D] [--month M] [--credit A] [--debit A] [--account A] [--column C] [--description X] [--comment X] [--tag X]
                  [--amount N] [--min_amount N] [--max_amount N] [--abbrev] [--order_by C] [--total] [--update F V F V] [--journal | --csv]

options:
  -h, --help        show this help message and exit
  --entry           seach individual debit or credit entries
  --date D          transaction date
  --start_date D    starting date
  --end_date D      ending date
  --month M         define start and end dates based on month name
  --credit A        credit account name (transaction)
  --debit A         debit account name (transaction)
  --account A       account name (entry)
  --column C        entry type (entry)
  --description X   descriptions pattern
  --comment X       comment pattern (transaction)
  --tag X           tag pattern (transaction)
  --amount N        amount
  --min_amount N    minimum amount
  --max_amount N    maximum amount
  --abbrev          print abbreviated account names
  --order_by C      sort order
  --total           print total amount of selected transactions
  --update F V F V  update fields
  --journal         print in Journal format
  --csv             print in CSV format, with a header line
```

