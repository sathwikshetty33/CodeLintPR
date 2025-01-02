from django.shortcuts import render


def homes(request):
    return render(request,'home.html')