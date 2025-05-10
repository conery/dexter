# Command Line Application

Dexter is a command line application.
The shell command to run it has the general form of
```shell
$ dex CMND [OPTIONS]
```
where CMND is the name of an operation (initialize new database, import CSVs, _etc_) and OPTIONS vary from one command to another.

We recommend setting up a **project directory** to use when running Dexter.
The directory will have a configuration file, csv files for defining account names and other data, and a folder for saving downloaded CSVs:
```
Finances
├── accounts.csv
├── dex.toml
├── Downloads
│   ├── chase.visa.csv
│   ├── checking.csv
│   └── savings.csv
└── regexp.csv
```

A typical session with Dexter starts with going to this folder and running Dexter commands to carry out your expense tracking workflow:
```shell
$ cd Finances
$ dex report --audit
$ dex import Downloads/*.csv
$ dex pair
...
```

