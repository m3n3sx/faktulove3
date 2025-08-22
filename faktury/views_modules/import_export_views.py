"""
Import/Export views - placeholder
"""
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse


@login_required
def export_kontrahenci(request):
    """Export contractors - placeholder"""
    messages.info(request, "Funkcja eksportu kontrahentów będzie dostępna wkrótce.")
    return redirect('kontrahenci')


@login_required  
def import_kontrahenci(request):
    """Import contractors - placeholder"""
    messages.info(request, "Funkcja importu kontrahentów będzie dostępna wkrótce.")
    return redirect('kontrahenci')


@login_required
def export_produkty(request):
    """Export products - placeholder"""
    messages.info(request, "Funkcja eksportu produktów będzie dostępna wkrótce.")
    return redirect('produkty')


@login_required
def import_produkty(request):
    """Import products - placeholder"""
    messages.info(request, "Funkcja importu produktów będzie dostępna wkrótce.")
    return redirect('produkty')


@login_required
def export_faktury(request):
    """Export invoices - placeholder"""
    messages.info(request, "Funkcja eksportu faktur będzie dostępna wkrótce.")
    return redirect('panel_uzytkownika')


@login_required
def import_faktury(request):
    """Import invoices - placeholder"""
    messages.info(request, "Funkcja importu faktur będzie dostępna wkrótce.")
    return redirect('panel_uzytkownika')
