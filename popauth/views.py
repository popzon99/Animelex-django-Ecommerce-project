from django.shortcuts import render,HttpResponse,redirect
from django.views.generic import View
from django.contrib import messages
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.models import User

#to activate the user accounts
# to get the shortcut link for the cuurent site
from django.contrib.sites.shortcuts import get_current_site
#for decoding and encoding the particular strings 
from django.utils.http import urlsafe_base64_decode,urlsafe_base64_encode
from django.urls import NoReverseMatch,reverse
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes,force_text,DjangoUnicodeDecodeError

#getting token from utils.py file

from . utils import generate_token,TokenGenerator


# for emails
from django.core.mail import send_mail,EmailMultiAlternatives,EmailMessage
from django.core.mail import BadHeaderError,send_mail
from django.core import mail

from django.conf import settings
from django.core.mail import EmailMessage

#reset password generator
from django.contrib.auth.tokens import PasswordResetTokenGenerator


# Create your views here.
#threading function used for sending emails faster or to get faster
import threading

class EmailThread(threading.Thread):

    def __init__ (self,email_message):
        self.email_message=email_message
        threading.Thread.__init__(self)
        
    def run(self):
        self.email_message.send()


        

class ActivateAccountView(View):
    def get(self,request,uidb64,token):
        try:
            uid = force_text(urlsafe_base64_decode(uidb64))
            user= User.objects.get(pk=uid)
        except Exception as identifier:
            user=None
        if user is not None and generate_token.check_token(user,token):
            user.is_active=True
            user.save()
            messages.info(request,"Account Activated Succesfully")
            return redirect('/popauth/login/')
        return render(request,'popauth/activatefail.html')










#signin
def signup(request):
    if request.method == 'POST':
        email=request.POST.get('email')
        password=request.POST.get('pass1')
        confirm_password=request.POST.get('pass2')
        if password != confirm_password:

            messages.error(request,"Password do not Match,Please Try Again!")
            return redirect('/popauth/signup/')
        try:
            if User.objects.get(username=email):
                messages.warning(request,"Email Already Exists")
                return redirect('/popauth/signup/')
        except Exception as identifier:            
            pass 
        try:
            if User.objects.get(email=email):
                messages.warning(request,"Email Already Exists")
                return redirect('/popauth/signup/')
        except Exception as identifier:
            pass        
        # checks for error inputs
        user=User.objects.create_user(email,email,password)
        #to make the user inactive for email verification
        user.is_active=False
        user.save()
        current_site = get_current_site(request)
        email_subject = "Activate Your Account"
        message=render_to_string('popauth/activate.html',{
            'user':user,
            'domain':'127.0.0.1:8000',
            'uid': urlsafe_base64_encode(force_bytes(user.pk)),
            'token':generate_token.make_token(user),
            'protocol':'https' if request.is_secure() else 'http'

        })

        email_message = EmailMessage(email_subject,message,settings.EMAIL_HOST_USER,[email],)
        EmailThread(email_message).start()
        messages.info(request,'Activate Your Account by clicking link on your email')
        # messages.info(request,"Signup Successful Please Login")
        return redirect('/popauth/login/')    
    return render(request,'popauth/signup.html') 

#login

def user_login(request):
      if request.method == 'POST':
        # get parameters
        username=request.POST['email']
        userpassword=request.POST['pass1']
        user=authenticate(username=username,password=userpassword)
       
        if user is not None:
            login(request,user)
            messages.info(request,"Successfully Logged In")
            return render(request, 'popapp/index.html')

        else:
            messages.error(request,"Invalid Credentials")
            return redirect('/popauth/login/')    

         

      return render(request,'popauth/login.html')         



#logout


def user_logout(request):
    logout(request)
    messages.warning(request,"Logout Success")
    return redirect('/popauth/login/') 


#class function for request email password change. 

class RequestResetEmailView(View):
        def get(self,request):
            return render(request,'popauth/request-reset-email.html')

         #function to activate post request
        def post(self,request):
            email=request.POST['email']
            user = User.objects.filter(email=email)

            if user.exists():
                current_site=get_current_site(request)
                email_subject='[Reset Your Password]'
                message=render_to_string('popauth/reset-user-password.html',{
                    'domain':'127.0.0.1:8000',
                    'uid':urlsafe_base64_encode(force_bytes(user[0].pk)),
                    'token':PasswordResetTokenGenerator().make_token(user[0]),
                     'protocol':'https' if request.is_secure() else 'http'
                })

                email_message = EmailMessage(email_subject,message,settings.EMAIL_HOST_USER,[email])
                EmailThread(email_message).start()

                messages.info(request,"WE HAVE SENT YOU AN EMAIL WITH INSTRUCTION ON HOW TO RESET THE PASSWORD")
                return render(request,'popauth/request-reset-email.html')
        

#class based function for set new password

class SetNewPasswordView(View):
    def get(self,request,uidb64,token):
        context = {
            'uidb64':uidb64,
            'token': token
        }
        try:
            user_id = force_text(urlsafe_base64_decode(uidb64))
            user=User.objects.get(pk=user_id)

            if not PasswordResetTokenGenerator().check_token(user,token):
                messages.warning(request,"Password Reset Value Is Invalid")
                return render(request,'popauth/request-reset-email.html')

        except DjangoUnicodeDecodeError as identifier:  
            pass
        
        return render(request,'popauth/set-new-password.html',context)




    def post(self,request,uidb64,token):
            context = {
                'uidb64':uidb64,
                'token': token
                
            }
            password=request.POST.get('pass1')
            confirm_password=request.POST.get('pass2')
            if password != confirm_password:

                messages.error(request,"Password do not Match,Please Try Again!")
                return render(request,'popauth/ set-new-password.html',context)

            try:
                user_id=force_text(urlsafe_base64_decode(uidb64))
                user=User.objects.get(pk=user_id)
                user.set_password(password)
                user.save()
                messages.success(request,"Password Reset Success Please Login With New Password")
                return redirect('/popauth/login/')

            except DjangoUnicodeDecodeError as identifier:
                messages.error(request,"Something Went Wrong")
                return render(request,'popauth/set-new-password.html',context)
  
  
            return render(request,'popauth/set-new-password.html',context)
    
    