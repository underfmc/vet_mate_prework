from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    url_name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'


class Article(models.Model):
    title = models.CharField(max_length=200)
    image = models.ImageField(upload_to='posts/', null=True, blank=True)
    content = models.TextField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE,
                                 related_name='articles')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Статья'
        verbose_name_plural = 'Статьи'
