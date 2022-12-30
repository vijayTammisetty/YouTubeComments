from django.db import models

# Create your models here.

class UserModel(models.Model):
    user_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)
    email = models.EmailField()
    password = models.CharField(max_length=50)
    # con_password = models.CharField(max_length=40,null=True)
    profile = models.ImageField(upload_to='images/',null=True)
    phone = models.CharField(max_length=50)
    country = models.CharField(max_length=50)
    status = models.CharField(max_length=50, default='pending')


    def __str__(self) :
        return self.name

    class Meta:
        db_table = 'usermodel'



