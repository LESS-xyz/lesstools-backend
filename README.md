Proper work of payment and holding mechanism demands the database to be initialized with the needed entities of supported networks and tokens which are eligible for monthly payments.

For populating database with base token and network entities run
```shell
manage.py loaddata lesstools/fixtures/base_payment_entities.json
```
after applying migrations.

If the current database state of plan price, network and token entities (rates incl.) is needed to be used as a base one, it can be saved by running:
```shell
manage.py dumpdata --indent 4 networks rates accounts.PlanPrice -o lesstools/fixtures/base_payment_entities.json
```
\
Both commands can be run inside docker containers preceded by:
```shell
docker-compose exec web python manage.py ...
```

[Django docs about fixtures](https://docs.djangoproject.com/en/3.2/howto/initial-data/#providing-data-with-fixtures)
