from decimal import Decimal
from django.shortcuts import render, redirect
from django.contrib.auth.models import User,auth
from .models import Account,Transaction
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
import random
from django.core.mail import EmailMultiAlternatives

def register(request):
    if request.method == 'POST':
        firstname = request.POST['first_name']
        lastname = request.POST['last_name']
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']
        errors = {}  
        if password != confirm_password:
            errors['password'] = 'Passwords do not match'
        if User.objects.filter(username=username).exists():
            errors['username'] = 'Username already exists'
        if User.objects.filter(email=email).exists():
            errors['email'] = 'Email already exists'
        if errors:
            return render(request, 'register.html', {'errors': errors})
        user = User.objects.create_user(first_name=firstname,last_name=lastname,username=username,email=email,password=password)
        user.save()
        account = Account(first_name=firstname,last_name=lastname,username=username,email=email,account_balance=0.00)
        account.save()
        with open('template/Mailtemplates/account_creation_success.html', 'r') as file:
            html_content = file.read()
            html_content = html_content.replace('{firstname}', firstname) 
        subject = 'Account Created Successfully'
        from_email = settings.EMAIL_HOST_USER
        recipient_list = [email]  
        email_account_creation = EmailMultiAlternatives(subject, '', from_email, recipient_list)
        email_account_creation.attach_alternative(html_content, "text/html") 
        email_account_creation.send()
        return redirect('/account/success/')
    return render(request, 'register.html')
def regsuccess(request):
    return render(request, 'regsuccess.html')
def login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        errors = {}  
        user = auth.authenticate(username=username, password=password)
        if user is not None:
            auth.login(request, user)
            return redirect('/account/lobby/') 
        else:
            errors['login'] = 'Invalid username or password'
        return render(request, 'login.html', {'errors': errors,})
    return render(request, 'login.html')
otp_storage={}
def forgotpassword(request):
    errors=''
    if request.method == 'POST':
        username = request.POST.get('username')
        if User.objects.filter(username=username).exists():
            user = User.objects.get(username=username)
            otp = random.randint(100000, 999999) 
            otp_storage[username] = otp
            with open('template/Mailtemplates/password_reset_email.html', 'r') as file:
                html_content = file.read()
                html_content = html_content.replace('{username}', user.username)
                html_content = html_content.replace('{otp}', str(otp))  

            subject = 'Your One-Time Password (OTP) for Password Reset'
            email = EmailMultiAlternatives(subject, '', settings.DEFAULT_FROM_EMAIL, [user.email])
            email.attach_alternative(html_content, "text/html")
            email.send()
            return redirect('account:verify_otp', username=username) 
        else:
            errors = 'No user is associated with this username.'
    return render(request, 'forgotpassword.html',{'errors':errors})
def verify_otp(request, username):
	error=""
	if request.method == 'POST':
		entered_otp = request.POST.get('otp')
		if username in otp_storage and otp_storage[username] == int(entered_otp):
			return redirect('account:reset_password', username=username)
		else:
			error='Invalid OTP. Please try again.'
	return render(request, 'verify_otp.html', {'username': username,'errors':error})

def reset_password(request, username):
    error=''
    if request.method == 'POST':
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')
        if new_password == confirm_password:
            user = User.objects.get(username=username)
            user.set_password(new_password)  
            user.save()
            messages.success(request, 'Your password has been reset successfully.')
            return redirect('account:resetsuccess')
        else:
            error='Passwords do not match.'
    return render(request, 'reset_password.html', {'username': username,'errors':error})

def resetsuccess(request):
    return render(request, 'resetsuccess.html')

def lobby(request):
    account_balance = Account.objects.get(username=request.user.username).account_balance
    return render(request, 'lobby.html',{'account_balance': account_balance})

def withdraw(request):
    account_balance = Account.objects.get(username=request.user.username).account_balance
    errors = {} 
    errors['withdraw'] =''
    if request.method == 'POST':
        amount = request.POST['amount']
        amountdisplay=amount
        if Decimal(amount) <= account_balance:
            account = Account.objects.get(username=request.user.username)
            account.account_balance -= Decimal(amount)
            account.save()
            transaction = Transaction(
            transaction_type='Withdraw',
            main_username=account.username,
            sender_username=account.username,
            amount_deducted=Decimal(amount),
            receiver_name='SYSTEM',
            amount_received=Decimal(amount),
            balance=account.account_balance
            )
            transaction.save()
            with open('template/Mailtemplates/withdrawal_success_email.html', 'r') as file:
                html_content = file.read()
                html_content = html_content.replace('{username}', account.username)  
                html_content = html_content.replace('{amount}', str(amount)) 
                html_content = html_content.replace('{account_balance}', str(account.account_balance)) 
            subject = 'Withdrawal Successful'
            from_email = settings.EMAIL_HOST_USER
            recipient_list = [request.user.email]
            email = EmailMultiAlternatives(subject, '', from_email, recipient_list)
            email.attach_alternative(html_content, "text/html")  # Attach the HTML content
            email.send()
            return redirect('/account/withdraw/success/')  
        else:
            errors['withdraw'] = "Withdrawal failed. Please check your balance and try again"
    return render(request, 'withdraw.html',{'account_balance': account_balance,'errors': errors})

def withdrawsuccess(request):
    return render(request, 'withdraw_success.html')

def deposit(request):
    account_balance = Account.objects.get(username=request.user.username).account_balance
    if request.method == 'POST':
        amount = request.POST['amount']
        amountdisplay=amount
        account = Account.objects.get(username=request.user.username)
        amount_decimal = Decimal(amount)
        account.account_balance += amount_decimal
        account.save()
        transaction = Transaction(
        transaction_type='Deposit',
        main_username=account.username,
        sender_username='SYSTEM',
        amount_deducted=Decimal(amount),
        receiver_name=account.username,
        amount_received=Decimal(amount),
        balance=account.account_balance
        )
        transaction.save()
        with open('template/Mailtemplates/deposit_success_email.html', 'r') as file:
            html_content = file.read()
            html_content = html_content.replace('{username}', account.username)  
            html_content = html_content.replace('{amount}', str(amount_decimal))  
            html_content = html_content.replace('{account_balance}', str(account.account_balance)) 
        subject = 'Deposit Successful'
        from_email = settings.EMAIL_HOST_USER
        recipient_list = [request.user.email]
        email = EmailMultiAlternatives(subject, '', from_email, recipient_list)
        email.attach_alternative(html_content, "text/html")
        email.send()
        return redirect('/account/deposit/success/')
    return render(request, 'deposit.html',{'account_balance': account_balance})

def depositsuccess(request):
    return render(request, 'deposit_success.html')

def logout(request):
    auth.logout(request)
    return redirect('/')

def transaction(request):
    transactions = Transaction.objects.filter(main_username=request.user.username)
    account_balance = Account.objects.get(username=request.user.username).account_balance

    return render(request, 'transaction.html', {'transactions': transactions,'account_balance': account_balance})    

def transfer(request):
    account_balance = Account.objects.get(username=request.user.username).account_balance
    non_staff_users = User.objects.filter(is_staff=False).exclude(username=request.user.username)
    errors=''
    if request.method == 'POST':
        recipient_username = request.POST.get('recipient')
        amount = request.POST.get('amount')
        amount_decimal = Decimal(amount)
        sender_account = Account.objects.get(username=request.user.username)
        recipient_account = Account.objects.get(username=recipient_username)
        if amount_decimal <= sender_account.account_balance:
            sender_account.account_balance -= amount_decimal
            sender_account.save()
            recipient_account.account_balance += amount_decimal
            recipient_account.save()
            transaction1 = Transaction(
                transaction_type='Transfer',
                main_username=sender_account.username,
                sender_username=sender_account.username,
                amount_deducted=amount_decimal,
                receiver_name=recipient_account.username,
                amount_received=Decimal(amount),
                balance=sender_account.account_balance
                )
            transaction1.save()
            transaction2 = Transaction(
                transaction_type='Transfer',
                main_username=recipient_account.username,
                sender_username=sender_account.username,
                amount_deducted=Decimal(amount),
                receiver_name=recipient_account.username,
                amount_received=amount_decimal,
                balance=recipient_account.account_balance
            )
            transaction2.save()
            with open('template/Mailtemplates/transfer_success_sender.html', 'r') as file:
                html_content = file.read()
                html_content = html_content.replace('{username}', sender_account.username) 
                html_content = html_content.replace('{amount}', str(amount_decimal)) 
                html_content = html_content.replace('{recipient}', recipient_account.username) 
                html_content = html_content.replace('{account_balance}', str(sender_account.account_balance)) 
            subject = 'Transfer Successful'
            from_email = settings.EMAIL_HOST_USER
            recipient_list = [sender_account.email] 
            email = EmailMultiAlternatives(subject, '', from_email, recipient_list)
            email.attach_alternative(html_content, "text/html") 
            email.send()
            with open('template/Mailtemplates/transfer_success_recipient.html', 'r') as file:
                html_content = file.read()
                html_content = html_content.replace('{username}', recipient_account.username) 
                html_content = html_content.replace('{amount}', str(amount_decimal)) 
                html_content = html_content.replace('{sender}', sender_account.username)  
                html_content = html_content.replace('{account_balance}', str(recipient_account.account_balance))
            subject_recipient = 'You Received a Transfer'
            from_email = settings.EMAIL_HOST_USER
            recipient_list = [recipient_account.email]  
            email_recipient = EmailMultiAlternatives(subject_recipient, '', from_email, recipient_list)
            email_recipient.attach_alternative(html_content, "text/html") 
            email_recipient.send()

            return redirect('/account/transfer/success')
        else:
            errors = "Transfer failed. Please check your balance and try again"
    return render(request, 'send_money.html',{
        'account_balance': account_balance,
        'non_staff_users': non_staff_users,
        'errors': errors
        })

def transfer_success(request):
    return render(request, 'transfer_success.html')