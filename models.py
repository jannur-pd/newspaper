from django.db import models
from django.contrib.auth.models import User
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny


class News(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    published_date = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey('Author', on_delete=models.SET_NULL, null=True)
    category = models.ForeignKey('Category', on_delete=models.SET_NULL, null=True)
    image = models.ImageField(upload_to='news_images/', blank=True, null=True)
    def __str__(self):
        return f"{self.category} | {self.title}"

class Author(models.Model):
    name = models.CharField(max_length=100)
    bio = models.TextField(blank=True, null=True)
    email = models.EmailField(unique=True)
    def __str__(self):
        return self.name

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    def __str__(self):
        return self.name


class Image(models.Model):
    news = models.ForeignKey('News', on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='news_images/')


class Advertisement(models.Model):
    title = models.CharField(max_length=100)
    content = models.TextField()
    image = models.ImageField(upload_to='ads/')
    display_start = models.DateTimeField()
    display_end = models.DateTimeField()
    def __str__(self):
        return self.title



class SavedArticle(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='saved_articles')
    news = models.ForeignKey(News, on_delete=models.CASCADE)

    class Meta:
        unique_together = ['user', 'news']

    def __str__(self):
        return f"{self.user.username} saved {self.news.title}"