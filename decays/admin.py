from django.contrib import admin

from decays.models import *

class ParticleAdmin(admin.ModelAdmin):
    list_display = ('name', 'verbose_name', 'mass', 'charge')

admin.site.register(Particle, ParticleAdmin)
admin.site.register(AliasName)
admin.site.register(DecayType)
admin.site.register(AnalyzedEvent)
admin.site.register(Institution)
admin.site.register(Profile)

