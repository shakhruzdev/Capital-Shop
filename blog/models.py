from django.db import models
from django.contrib.auth import get_user_model
from store.models import BaseModel

User = get_user_model()


class Tag(BaseModel):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class Category(BaseModel):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class Post(BaseModel):
    title = models.CharField(max_length=50)
    description = models.TextField()
    image = models.ImageField(upload_to="post/images/")
    tags = models.ManyToManyField(Tag)
    categories = models.ForeignKey(Category, on_delete=models.CASCADE)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class Comment(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    message = models.TextField()
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='comment_replies')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.user} --> {self.post}'


class Reply(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name='replies')
    message = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'Reply by {self.user} on comment {self.comment.id}'
