from django.http import HttpRequest, HttpResponse
from django.shortcuts import render


def root(request: HttpRequest) -> HttpResponse:
    return render(request, 'index.html')


def markings(request: HttpRequest) -> HttpResponse:
    return render(request, 'markings.html')


def chart(request: HttpRequest) -> HttpResponse:
    return render(request, 'chart.html')
