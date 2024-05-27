# Generated by Django 5.0.4 on 2024-05-23 12:35

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="DomainSirenAssociation",
            fields=[
                ("id", models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("domain", models.CharField(max_length=255, unique=True)),
                ("siren", models.CharField(blank=True, max_length=9, null=True)),
            ],
            options={
                "verbose_name": "Paire domaine-SIREN",
                "verbose_name_plural": "Paires domaine-SIREN",
            },
        ),
        migrations.CreateModel(
            name="ScoredCompany",
            fields=[
                ("id", models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("siren", models.CharField(max_length=9, unique=True)),
                ("nom_complet", models.TextField()),
                ("api_entreprise_data", models.JSONField()),
                ("last_api_entreprise_at", models.DateTimeField()),
                ("last_api_entreprise_error", models.TextField(null=True)),
                ("tender_count", models.PositiveIntegerField(default=0, verbose_name="Nombre besoins Marché")),
                ("tender_amount", models.PositiveIntegerField(default=0, verbose_name="Montant besoins Marché")),
                ("conventions_count", models.PositiveIntegerField(default=0, verbose_name="Nombre conventions IF")),
                (
                    "score",
                    models.FloatField(
                        default=0,
                        help_text="(nb conventions + log(1 + montant besoins)) / poids catégorie entreprise",
                        verbose_name="Score",
                    ),
                ),
            ],
            options={
                "verbose_name": "Entreprise",
                "verbose_name_plural": "Entreprises",
            },
        ),
        migrations.CreateModel(
            name="LeMarcheRawTender",
            fields=[
                ("id", models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("slug", models.SlugField(max_length=255, unique=True, verbose_name="ID marché")),
                ("data", models.JSONField(verbose_name="Données brutes")),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "domain",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="lemarche_tenders",
                        to="company_score.domainsirenassociation",
                    ),
                ),
            ],
            options={
                "verbose_name": "Besoin d'achat",
                "verbose_name_plural": "Besoins d'achat",
            },
        ),
        migrations.CreateModel(
            name="IFRawConvention",
            fields=[
                ("id", models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("siren", models.CharField(max_length=9, verbose_name="SIREN")),
                ("nb_conventions", models.PositiveIntegerField(verbose_name="Nombre de conventions")),
                (
                    "company",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="if_conventions",
                        to="company_score.scoredcompany",
                    ),
                ),
            ],
            options={
                "verbose_name": "Convention IF",
                "verbose_name_plural": "Conventions IF",
            },
        ),
        migrations.AddField(
            model_name="domainsirenassociation",
            name="company",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="domains",
                to="company_score.scoredcompany",
            ),
        ),
    ]