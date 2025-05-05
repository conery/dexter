# `hldeger` Workflow

Dexter stores account data and transactions in a NoSQL database, so it's not strictly a plain text accounting application, but it does support the `.journal` format used by Ledger, hledger, and similar applications.
It's a straightforward process to import a journal with account definitions to initialize a database, use Dexter's workflow to process a batch of CSV files downloaded from banks and credit card companies, and export the results as a journal file.


