from django.contrib import admin
from .models import Brand, Product, Order, Cart, Like, Comment, Size, Color, Genre, Promocode, PromoCodeObj


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ['id', 'name']
    list_display_links = ['name']


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['id', 'name']
    list_display_links = ['id', 'name']


@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'product']
    list_display_links = ['id', 'user', 'product']


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'message']
    list_display_links = ['id', 'user', 'message']


@admin.register(Size)
class SizeAdmin(admin.ModelAdmin):
    list_display = ['id', 'name']
    list_display_links = ['id', 'name']


@admin.register(Color)
class ColorAdmin(admin.ModelAdmin):
    list_display = ['id', 'name']
    list_display_links = ['id', 'name']


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ['id', 'name']
    list_display_links = ['id', 'name']


admin.site.register(Order)
admin.site.register(Cart)
admin.site.register(Promocode)
admin.site.register(PromoCodeObj)
