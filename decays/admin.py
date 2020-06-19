from django.contrib import admin

from decays.models import *

class ParticleAdmin(admin.ModelAdmin):
    list_display = ('name', 'verbose_name', 'mass', 'charge')

class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'institution')

class AnalyzedEventAdmin(admin.ModelAdmin):
    list_display = ('title', 'submitted', 'created', 'updated')

class DecayTypeAdmin(admin.ModelAdmin):
    list_display = ('human_readable_name', 'parent', 'parent_alias', 'daughter_one', 'daughter_one_alias', 'daughter_two', 'daughter_two_alias', 'daughter_three', 'daughter_three_alias')

class AliasNameAdmin(admin.ModelAdmin):
    list_display = ('name', 'verbose_name')

admin.site.register(Particle, ParticleAdmin)
admin.site.register(AliasName, AliasNameAdmin)
admin.site.register(DecayType, DecayTypeAdmin)
admin.site.register(AnalyzedEvent, AnalyzedEventAdmin)
admin.site.register(Institution)
admin.site.register(Profile, ProfileAdmin)

