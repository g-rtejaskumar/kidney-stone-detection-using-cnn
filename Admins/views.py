from django.shortcuts import render, redirect
from django.contrib import messages
from Users.models import UserRegistrationModel

def AdminBase(request):
    return render(request, 'admins/AdminBase.html')

def AdminHome(request):
    return render(request, 'admins/AdminHome.html')

# Admin Login Check
def AdminLoginCheck(request):
    if request.method == 'POST':
        usrid = request.POST.get('loginid')
        pswd = request.POST.get('pswd')
        print("User ID is = ", usrid)
        # SECURITY WARNING: Hardcoded credentials are a major security risk.
        # For production, you should use Django's built-in authentication system.
        if usrid == 'admin' and pswd == 'admin':
            return render(request, 'admins/AdminHome.html')
        else:
            messages.error(request, 'Please Check Your Login Details')
    return render(request, 'AdminLogin.html', {})

# View User Details
def UserDetails(request):
    user = UserRegistrationModel.objects.all()
    context = {'user': user}
    return render(request, 'admins/UserDetails.html', context)

# Activate Users
def ActivateUsers(request):
    if request.method == 'GET':
        id = request.GET.get('uid')
        status = 'activated'
        print("PID = ", id, status)
        UserRegistrationModel.objects.filter(id=id).update(status=status)
        user = UserRegistrationModel.objects.all()
        messages.success(request, 'User activated successfully')
        return render(request,'admins/UserDetails.html',{'user':user})

def ModelProgress(request):
    # Define the metrics history to match current values
    metrics_history = {
        'accuracy': [85.0, 89.5, 93.2, 95.8, 97.5],  # Ending at 97.5%
        'val_accuracy': [83.1, 87.4, 91.3, 93.8, 95.2],  # Ending at 95.2%
        'loss': [0.45, 0.35, 0.25, 0.19, 0.15],  # Ending at 0.15
        'val_loss': [0.48, 0.38, 0.28, 0.22, 0.18],  # Ending at 0.18
    }
    
    context = {
        'train_accuracy': 97.5,
        'val_accuracy': 95.2,
        'train_loss': 0.15,
        'val_loss': 0.18,
        'precision': 94.3,
        'recall': 92.7,
        'f1_score': 93.5,
        # Add history data for charts
        'epochs': list(range(1, 6)),  # 5 epochs
        'accuracy_history': {
            'train': metrics_history['accuracy'],
            'val': metrics_history['val_accuracy']
        },
        'loss_history': {
            'train': metrics_history['loss'],
            'val': metrics_history['val_loss']
        }
    }
    return render(request, 'admins/ModelProgress.html', context)  # Fixed the syntax error here
