from django.shortcuts import render


def homes(request):
    return render(request,'home.html')

def loginpage(request):
    return render(request,'login.html')
def api(request):
    return render(request,'api.html')