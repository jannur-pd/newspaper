from django.contrib import admin
from .models import *

admin.site.register(News)
admin.site.register(Author)
admin.site.register(Category)
admin.site.register(Image)
admin.site.register(Advertisement)
admin.site.register(SavedArticle)