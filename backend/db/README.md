# database setup for nlqx testing

This folder contains the necessary files to set up a PostgreSQL for testing the nlqx examples.

## setup instructions

1. Make sure you have Docker and Docker Compose installed on your system.
1. Navigate to the `db/` directory in your terminal.
1. Run the following command to start the database:

```console
$ docker compose up
```

## connecting to the database

The postgres database will be available at `postgresql://nlqx_user:nlqx_password@localhost:5432/nlqx_test`
