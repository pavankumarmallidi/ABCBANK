from django.db import models
class Account(models.Model):
    username=models.CharField(max_length=20,unique=True)
    first_name = models.CharField(max_length=20)
    last_name = models.CharField(max_length=20)
    email = models.EmailField(unique=True)
    account_balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

class Transaction(models.Model):
    transaction_type = models.CharField(max_length=150)
    main_username=models.CharField(max_length=150)  
    sender_username = models.CharField(max_length=150)  
    amount_deducted = models.DecimalField(max_digits=10, decimal_places=2) 
    time_of_transaction = models.DateTimeField(auto_now_add=True)  
    receiver_name = models.CharField(max_length=150) 
    amount_received = models.DecimalField(max_digits=10, decimal_places=2) 
    balance = models.DecimalField(max_digits=10, decimal_places=2)  