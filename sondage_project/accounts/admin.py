from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Utilisateur, Anonyme, Participant


@admin.register(Utilisateur)
class UtilisateurAdmin(UserAdmin):
    list_display = ['username', 'email', 'role', 'is_active', 'date_inscription']
    list_filter = ['role', 'is_active']
    fieldsets = UserAdmin.fieldsets + (
        ('Informations supplémentaires', {
            'fields': ('role', 'bio', 'avatar')
        }),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Informations supplémentaires', {
            'fields': ('email', 'role')
        }),
    )


@admin.register(Anonyme)
class AnonymeAdmin(admin.ModelAdmin):
    list_display = ['identifier', 'adresse_ip', 'date_premiere_reponse']
    readonly_fields = ['token', 'date_premiere_reponse']
