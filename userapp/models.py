from django.db import models

# Create your models here.
class User(models.Model):
    user_id = models.AutoField(primary_key=True)
    user_name=models.CharField(max_length=50)
    user_email = models.EmailField(max_length=50)
    user_password = models.CharField(max_length=50)
    user_phone = models.CharField(max_length=50)
    user_location = models.CharField(max_length=50,default='Unknown')
    user_profile = models.ImageField(upload_to='images/user')
    status = models.CharField(max_length=15,default='accepted')
    otp = models.CharField(max_length=6,default=0) 
    otp_status = models.CharField(max_length=15, default='Not Verified')
  
  

    class Meta:
        db_table = 'User_details'