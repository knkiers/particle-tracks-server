from django.contrib import admin

from decays.models import *

class ParticleAdmin(admin.ModelAdmin):
    list_display = ('name', 'verbose_name', 'mass', 'charge')

class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'institution')

class AnalyzedEventAdmin(admin.ModelAdmin):
    list_display = ('title', 'submitted', 'created', 'updated')

admin.site.register(Particle, ParticleAdmin)
admin.site.register(AliasName)
admin.site.register(DecayType)
admin.site.register(AnalyzedEvent, AnalyzedEventAdmin)
admin.site.register(Institution)
admin.site.register(Profile, ProfileAdmin)

