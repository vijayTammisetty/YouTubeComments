from django.shortcuts import render, redirect
from django.contrib import messages
from sentimentapp.models import UserModel
from django.core.paginator import Paginator

# Create your views here.

def admin_login(request):

    if request.method == 'POST':
        name = request.POST.get('name')
        password = request.POST.get('password')
        print(name,password)

        if name == 'admin' and password == 'admin':
            print(name, 'rrrrrrrrrrrrr',password)
            messages.success(request,'Admin login successfully')
            return redirect('dashboard')
        
        else:
            messages.error(request,'Wrong name and password')
            return redirect('admin_login')

    return render(request, 'admin/login.html')

    
def dashboard(request):
    pending = UserModel.objects.filter(status='pending').count()
    all = UserModel.objects.all().count()

    context={
        'pending':pending,
        'all':all

    }
    return render(request, 'admin/index.html', context)

def pending_users(request):
    pending_user = UserModel.objects.filter(status='pending').order_by('-user_id')

    paginator = Paginator(pending_user,4)
    page_nnumber = request.GET.get('page')
    p = paginator.get_page(page_nnumber)
     
    context = {
        'page':p
    }
    return render(request,'admin/pending-users.html', context)


def accept_user(request,id):
    users = UserModel.objects.get(user_id=id)
    users.status = 'Accept'
    users.save(update_fields=['status'])
    users.save()
    messages.success(request,'New user add successfully')
    return redirect('pending-users')

def reject_user(request,id):
    user = UserModel.objects.get(user_id=id)
    user.delete()
    messages.success(request,'user rejected successfully ')
    return redirect('pending-users')

def all_users(request):

    all_users = UserModel.objects.filter(status='Accept')
    paginater = Paginator(all_users,4)
    page_number = request.GET.get('page')
    number_of_pages = paginater.get_page(page_number)

    context = {
        'users':number_of_pages
    }
    return render(request, 'admin/all-users.html', context)

def delete(request,id):
    user = UserModel.objects.get(user_id=id)
    user.delete()
    messages.success(request,'user delete successfully')
    return redirect('all-users')

def logout(request):
    messages.success(request,'Admin logout successfully')
    return redirect('home')


