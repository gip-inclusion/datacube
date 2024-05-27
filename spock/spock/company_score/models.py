import math

from django.db import models


class LeMarcheRawTender(models.Model):
    slug = models.SlugField(
        unique=True,
        max_length=255,  # those slugs can become quite long :/
        verbose_name="ID marché",
    )
    data = models.JSONField(verbose_name="Données brutes")
    updated_at = models.DateTimeField(auto_now=True)

    domain = models.ForeignKey(
        "DomainSirenAssociation",
        on_delete=models.SET_NULL,
        null=True,
        related_name="lemarche_tenders",
    )

    def amount_exact(self):
        return self.data.get("amount_exact") or 0

    class Meta:
        verbose_name = "Besoin d'achat"
        verbose_name_plural = "Besoins d'achat"


class IFRawConvention(models.Model):
    siren = models.CharField(max_length=9, verbose_name="SIREN")
    nb_conventions = models.PositiveIntegerField(verbose_name="Nombre de conventions")
    company = models.ForeignKey("ScoredCompany", on_delete=models.SET_NULL, null=True, related_name="if_conventions")

    class Meta:
        verbose_name = "Convention IF"
        verbose_name_plural = "Conventions IF"


class DomainSirenAssociation(models.Model):
    """Cache d'association de noms de domaine à un SIREN.
    Utile pour etre certain de ne jamais retenter 2 fois la même résolution Google
    pour un nom de domaine donné, et ce même si les données source du marché changent.
    Par exemple si un auteur de besoin change de mail, on conserve ici la correspondance.
    Par ailleurs cela permet une modification ou complétion manuelle (dans l'admin) de ces
    informations.
    """

    domain = models.CharField(max_length=255, unique=True)
    siren = models.CharField(max_length=9, null=True, blank=True)
    company = models.ForeignKey(
        "ScoredCompany",
        on_delete=models.SET_NULL,
        null=True,
        related_name="domains",
    )

    def __str__(self) -> str:
        return f"{self.domain}{" - " + self.siren if self.siren else ""}"

    class Meta:
        verbose_name = "Paire domaine-SIREN"
        verbose_name_plural = "Paires domaine-SIREN"


COMPANY_CATEGORY_TO_WEIGHT = {
    "PME": 1,
    "ETI": 3,
    "GE": 10,
}

TRANCHES_EFFECTIF = {
    "00": "0",
    "01": "1 ou 2",
    "02": "3 à 5",
    "03": "6 à 9",
    "11": "10 à 19",
    "12": "20 à 49",
    "21": "50 à 99",
    "22": "100 à 199",
    "31": "200 à 249",
    "32": "250 à 499",
    "41": "500 à 999",
    "42": "1 000 à 1 999",
    "51": "2 000 à 4 999",
    "52": "5 000 à 9 999",
    "53": "10 000 et plus",
}

CONVENTION_WEIGHTS = [5, 10, 7] + [3] * 7 + [1] * 1000


class ScoredCompany(models.Model):
    siren = models.CharField(max_length=9, unique=True)  # our base key
    nom_complet = models.TextField()

    # FIXME(vperron) : JSON for the time being, as the score is not yet implemented
    api_entreprise_data = models.JSONField()

    last_api_entreprise_at = models.DateTimeField()
    last_api_entreprise_error = models.TextField(null=True)

    # Denormalized fields
    tender_count = models.PositiveIntegerField(default=0, verbose_name="Nombre besoins Marché")
    tender_amount = models.PositiveIntegerField(default=0, verbose_name="Montant besoins Marché")
    conventions_count = models.PositiveIntegerField(default=0, verbose_name="Nombre conventions IF")
    score = models.FloatField(
        default=0,
        verbose_name="Score",
        help_text="(nb conventions + log(1 + montant besoins)) / poids catégorie entreprise",
    )

    def __str__(self) -> str:
        return self.nom_complet

    def _get_latest_finance_value(self, key):
        for _, v in sorted(self.api_entreprise_data["finances"].items()):
            return f"{v[key]:,}"
        return None

    def income(self):
        return self._get_latest_finance_value("ca") or "-"

    def net_income(self):
        return self._get_latest_finance_value("resultat_net") or "-"

    def headcount(self) -> str:
        tranche = self.api_entreprise_data.get("tranche_effectif")
        return TRANCHES_EFFECTIF.get(tranche, "-")

    def get_tender_count(self):
        return sum(domain.lemarche_tenders.count() for domain in self.domains.all())

    def get_tender_amount(self):
        amount = 0
        for domain in self.domains.all():
            amount += sum(t.amount_exact() for t in domain.lemarche_tenders.all())
        return amount

    def get_conventions_count(self):
        # FIXME(vperron): We should switch to an OneToOneField here, but
        # orginially and maybe soon we should get multiple conventions
        # for a single company throught the API.
        return sum(c.nb_conventions for c in self.if_conventions.all())

    def get_score(self) -> float:
        def convention_bell(x):
            amount = 0
            i = 0
            while i != x:
                amount += CONVENTION_WEIGHTS[i]
                i += 1
            return amount

        company_kind = self.api_entreprise_data["categorie_entreprise"]
        if company_kind not in COMPANY_CATEGORY_TO_WEIGHT:
            return -1  # can't be computed
        return round(
            (convention_bell(self.get_conventions_count()) + 10 * math.log(1 + self.get_tender_amount()))
            / COMPANY_CATEGORY_TO_WEIGHT[company_kind],
            2,
        )

    class Meta:
        verbose_name = "Entreprise"
        verbose_name_plural = "Entreprises"
