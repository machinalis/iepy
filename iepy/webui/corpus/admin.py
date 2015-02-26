from django.contrib import admin
from django.core import urlresolvers

from corpus.models import (
    IEDocument, Entity, EntityKind, Relation,
    EntityOccurrence, GazetteItem
)

admin.site.site_header = 'IEPY administration'
admin.site.site_title = 'IEPY'
admin.site.index_title = 'IEPY'


@admin.register(EntityKind)
class EntityKindAdmin(admin.ModelAdmin):
    pass


@admin.register(EntityOccurrence)
class EntityOccurrenceAdmin(admin.ModelAdmin):
    pass


@admin.register(Entity)
class EntityAdmin(admin.ModelAdmin):
    list_per_page = 20


@admin.register(IEDocument)
class IEDocumentAdmin(admin.ModelAdmin):
    list_display = ['id', 'human_identifier', 'link_to_document_navigation']
    search_fields = ['text']

    def link_to_document_navigation(self, obj):
        return '<a href="{0}">Rich View</a>'.format(
            urlresolvers.reverse('corpus:navigate_document', args=(obj.id,))
        )
    link_to_document_navigation.short_description = 'Rich View'
    link_to_document_navigation.allow_tags = True
    list_per_page = 20


@admin.register(Relation)
class RelationAdmin(admin.ModelAdmin):
    list_display = ('name', 'left_entity_kind', 'right_entity_kind', 'link_to_label')

    def link_to_label(self, obj):
        return '<a href="{0}">Label evidence</a>'.format(
            urlresolvers.reverse('corpus:next_document_to_label', args=(obj.id,))
        )
    link_to_label.short_description = 'Labeling'
    link_to_label.allow_tags = True

    def get_readonly_fields(self, request, obj=None):
        if obj:  # editing an existing object
            return self.readonly_fields + ('left_entity_kind', 'right_entity_kind')
        return self.readonly_fields


@admin.register(GazetteItem)
class GazetteAdmin(admin.ModelAdmin):
    search_fields = ['text']
    list_display = ('text', 'kind', 'from_freebase',)
    list_filter = ('kind', 'from_freebase',)
    readonly_fields = ('from_freebase', )
