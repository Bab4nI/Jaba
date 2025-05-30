from django.db import models

# Create your models here.


class News(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    date = models.DateTimeField(auto_now_add=True)
    link = models.URLField(blank=True, null=True)
    image_url = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        ordering = ["-date"]

    def __str__(self):
        return self.title
