from django.contrib import admin

from corpus.models import IEDocument, Entity, EntityKind, Relation


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


class RelationAdmin(admin.ModelAdmin):
    def get_readonly_fields(self, request, obj=None):
        if obj:  # editing an existing object
            return self.readonly_fields + ('left_entity_kind', 'right_entity_kind')
        return self.readonly_fields
admin.site.register(Relation, RelationAdmin)
