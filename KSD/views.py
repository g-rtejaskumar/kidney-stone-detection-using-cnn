from django.shortcuts import render
from Users.forms import UserRegistrationForm

# Create your views here.
def Base(request):
    return render(request,'Base.html')
def Home(request):
    return render(request,'Home.html')
def UserLogin(request):
    return render(request,'UserLogin.html')

def UserRegister(request):
    form = UserRegistrationForm()
    return render(request, 'UserRegistration.html', {'form': form})


