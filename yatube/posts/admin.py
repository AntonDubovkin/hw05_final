from django.contrib import admin

from .models import Post, Group


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('pk',
                    'text',
                    'pub_date',
                    'author',
                    'group'
                    )
    list_editable = ('group',)
    search_fields = ('text',)
    list_filter = ('pub_date',)
    empty_value_display = '-пусто-'


class Comment(admin.ModelAdmin):
    list_display = ('name', 'post', 'created',)
    list_filter = ('created')
    search_fields = ('name', 'post', 'created')


admin.site.register(Group)
