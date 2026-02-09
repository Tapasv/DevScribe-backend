from django.contrib import admin
from .models import Post, Category, Comment, UserProfile

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'role', 'total_posts', 'total_views', 'created_at']
    list_filter = ['role', 'created_at']
    search_fields = ['user__username', 'user__email']

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'created_at']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name']

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'category', 'published', 'featured', 'views', 'created_at']
    list_filter = ['published', 'featured', 'category', 'created_at']
    search_fields = ['title', 'content', 'excerpt']
    prepopulated_fields = {'slug': ('title',)}
    list_editable = ['published', 'featured']
    readonly_fields = ['views', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'slug', 'author', 'category')
        }),
        ('Content', {
            'fields': ('excerpt', 'content', 'image')
        }),
        ('Settings', {
            'fields': ('published', 'featured')
        }),
        ('Statistics', {
            'fields': ('views', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['name', 'post', 'user', 'created_at', 'approved']
    list_filter = ['approved', 'created_at']
    search_fields = ['name', 'email', 'content']
    list_editable = ['approved']
    readonly_fields = ['created_at']