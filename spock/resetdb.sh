#!/bin/bash

# dropdb spock
# createdb spock
# rm -f spock/company_score/migrations/*
# ./manage.py makemigrations company_score
# ./manage.py migrate
# ./manage.py createsuperuser --username admin --email=admin@example.com --no-input
# 
# ./manage.py loaddata scored_companies
# ./manage.py loaddata resolved_domains
# ./manage.py loaddata if_conventions
# time ./manage.py sync_le_marche_tenders
# time python3 -u -m cProfile -o prof-domain manage.py resolve_domain_sirens --wet-run | tee output-domain-resolve.log
# time python3 -u -m cProfile -o prof-companies manage.py resolve_siren_companies --wet-run | tee output-siren-resolve.log
# time python3 -u -m cProfile -o prof-score manage.py compute_score --wet-run | tee output-company-score.log
