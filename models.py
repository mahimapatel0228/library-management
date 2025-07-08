from django.db import models
from django.utils import timezone

class Book(models.Model):
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    isbn = models.CharField(max_length=13, blank=True, null=True)
    publisher = models.CharField(max_length=255, blank=True, null=True)
    pages = models.IntegerField(default=0)
    stock = models.IntegerField(default=1)

    def __str__(self):
        return f"{self.title} by {self.author}"

class Member(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField()
    debt = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return self.name

class Transaction(models.Model):
    member = models.ForeignKey(Member, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    issue_date = models.DateField(default=timezone.now)
    return_date = models.DateField(blank=True, null=True)
    returned = models.BooleanField(default=False)
    rent_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return f"{self.member} - {self.book}"
