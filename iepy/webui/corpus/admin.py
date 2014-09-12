from django.contrib import admin

from corpus.models import IEDocument, Entity, EntityKind


class EntityKindAdmin(admin.ModelAdmin):
    pass
admin.site.register(EntityKind, EntityKindAdmin)


class EntityAdmin(admin.ModelAdmin):
    list_per_page = 20
admin.site.register(Entity, EntityAdmin)


class IEDocumentAdmin(admin.ModelAdmin):
    list_display = ['id', 'human_identifier', 'title']
    list_per_page = 20
admin.site.register(IEDocument, IEDocumentAdmin)
