from django.shortcuts import render

def frontend(request, exception=None):
    return render(request, 'index.html')
