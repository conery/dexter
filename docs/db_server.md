
> [!note] Database Connections
> The current version of Dexter works with a NoQL database named MongoDB.
> It expects to connect to server running on your computer.
> A SQLite connection is in the works.

### Install MongoDB

Unlike plain text accounting applications, Dexter stores transactions and other work products in a database.

The easiest way to install MongoDB is to use Homebrew:
```shell
$ brew tap mongodb/brew
$ brew install mongodb-community
```

Then start the server:
```shell
$ brew services start mongodb-community
```

The server should run automatically every time you restart your computer.

