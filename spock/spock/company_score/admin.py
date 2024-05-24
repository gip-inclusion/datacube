from django.contrib import admin

from spock.company_score import models


@admin.register(models.LeMarcheRawTender)
class LeMarcheRawTenderAdmin(admin.ModelAdmin):
    list_display_links = ("title",)
    list_display = ("title", "kind", "status", "amount", "domain", "company_name")
    list_select_related = ("domain__company",)
    ordering = ("domain__domain",)

    @admin.display(description="Type")
    def kind(self, obj):
        return obj.data["kind"]

    @admin.display(description="Etat")
    def status(self, obj):
        return obj.data["status"]

    @admin.display(description="Montant")
    def amount(self, obj):
        return obj.data["amount_exact"] or obj.data["amount"] or "-"

    @admin.display(description="Titre")
    def title(self, obj):
        return obj.data["title"]

    @admin.display(description="Entreprise")
    def company_name(self, obj):
        if obj.domain and obj.domain.company:
            return obj.domain.company.nom_complet
        return "-"

    def has_change_permission(self, request, obj=None):
        return False


@admin.register(models.IFRawConvention)
class IFRawConventionAdmin(admin.ModelAdmin):
    list_display = ("siren", "nb_conventions", "company")
    list_select_related = ("company",)
    search_fields = ("siren", "company__nom_complet")
    list_per_page = 500


@admin.register(models.DomainSirenAssociation)
class DomainSirenAssociationAdmin(admin.ModelAdmin):
    search_fields = ("domain", "siren", "company__nom_complet")
    list_display = ("domain", "siren", "company")
    readonly_fields = ("domain", "company")
    ordering = ("domain",)
    list_per_page = 500


@admin.register(models.ScoredCompany)
class ScoredCompanyAdmin(admin.ModelAdmin):
    search_fields = ("siren", "nom_complet")
    list_display = (
        "siren",
        "nom_complet",
        "kind",
        "tender_count",
        "tender_amount",
        "conventions_count",
        "score",
    )
    ordering = ("-score", "nom_complet")
    readonly_fields = (
        "siren",
        "nom_complet",
        "last_api_entreprise_at",
        "last_api_entreprise_error",
    )

    fieldsets = (
        (
            "Champs de base",
            {
                "fields": (
                    "siren",
                    "nom_complet",
                    "kind",
                    "tender_count",
                    "tender_amount",
                    "conventions_count",
                    "score",
                )
            },
        ),
        (
            "Champs extra",
            {
                "fields": (
                    "headcount",
                    "income",
                    "net_income",
                    "income_year",
                    "last_api_entreprise_at",
                    "last_api_entreprise_error",
                ),
            },
        ),
        (
            "Données brutes API Entreprise",
            {
                "fields": ("api_entreprise_data",),
                "classes": ("collapse",),
            },
        ),
    )

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .prefetch_related(
                "domains__lemarche_tenders",
                "if_conventions",
            )
        )

    @admin.display(description="Catégorie")
    def kind(self, obj):
        return obj.api_entreprise_data["categorie_entreprise"]

    @admin.display(description="Tranche effectif")
    def headcount(self, obj):
        return obj.headcount()

    @admin.display(description="CA")
    def income(self, obj):
        return obj.income()

    @admin.display(description="Bénéfices")
    def net_income(self, obj):
        return obj.net_income()

    @admin.display(description="Année CA")
    def income_year(self, obj):
        year = "-"
        for k, _ in sorted(obj.api_entreprise_data["finances"].items()):
            year = k
        return year

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
