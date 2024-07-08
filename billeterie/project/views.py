from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .forms import LoginForm, RegisterForm, DestinationForm, TicketForm, PaymentForm,BusForm
from .models import User, Destination, Ticket, Payment,Bus
from django.contrib import messages  # Importez le module messages pour afficher les messages
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
import io
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from datetime import datetime
from django.utils import timezone



# Vue de connexion
def user_login(request):
    form = LoginForm(request.POST or None)
    msg = ""
    if request.method == 'POST':
        if form.is_valid():
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password')
            user = authenticate(email=email, password=password)
            if user is not None:
                login(request, user)
                return redirect('/')
                
            else:
                msg = 'Information invalide'
        else:
            msg = 'Email ou mot de passe invalide'
    else:
        msg = 'Erreur de validation'
    return render(request, 'login.html', {'form': form, 'msg': msg })


def user_register(request):
    msg = None
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.save()
            msg = 'Utilisateur créé'
            return redirect('login')
        else:
            msg = 'Informations invalides'
    else:
        form = RegisterForm()
    return render(request, 'register.html', {'form': form, 'msg': msg})


# Vue pour afficher la liste des destinations disponibles avec leurs prix et photos
def destination_list(request):
    destinations = Destination.objects.all()
    return render(request, 'destination_list.html', {'destinations': destinations})



# Vue pour enregistrer une nouvelle destination
@login_required
def add_destination(request):
    if request.method == 'POST':
        form = DestinationForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('home')  # Rediriger vers la liste des destinations après l'enregistrement réussi
    else:
        form = DestinationForm()
    return render(request, 'add_destination.html', {'form': form})


@login_required
def create_bus(request):
    if request.method == 'POST':
        form = BusForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Le bus a été ajouté avec succès.')
            return redirect('create_bus')  # Remplacez 'bus_list' par le nom de votre vue de liste des bus
        else:
            messages.error(request, 'Veuillez corriger les erreurs ci-dessous.')
    else:
        form = BusForm()
    
    return render(request, 'create_bus.html', {'form': form})




@login_required
def purchase_ticket(request, destination_id):
    destination = get_object_or_404(Destination, pk=destination_id)
    user = request.user  # Récupérer l'utilisateur connecté

    if request.method == 'POST':
        ticket_form = TicketForm(request.POST)
        if ticket_form.is_valid():
            # Vérifier si l'heure de départ est supérieure à la time zone actuelle
            now = timezone.now()
            if destination.heure_depart > now.time():
                # Compter les tickets existants pour cette destination et cette date
                departure_date = ticket_form.cleaned_data['departure_date']
                tickets = Ticket.objects.filter(destination=destination, departure_date=departure_date)
                if tickets.count() < destination.bus.nombre_place:
                    ticket = ticket_form.save(commit=False)
                    ticket.destination = destination
                    ticket.user = user
                    ticket.is_confirmed = True

                    # Vérifier si le montant payé est suffisant
                    if ticket.amount_paid < destination.montant:
                        messages.error(request, "Le montant payé est insuffisant.")
                    else:
                        ticket.save()

                        # Créer le paiement associé
                        payment = Payment.objects.create(ticket=ticket, transaction_id="SIMULATED_TRANSACTION_ID")

                        # Générer le PDF du ticket
                        template_path = 'ticket_pdf_template.html'
                        context = {
                            'ticket': ticket,
                            'destination': destination,
                            'departure_time': destination.heure_depart,  # Ajouter l'heure de départ au contexte
                        }
                        template = get_template(template_path)
                        html = template.render(context)

                        # Convertir en PDF
                        pdf_buffer = io.BytesIO()
                        pisa_status = pisa.CreatePDF(html, dest=pdf_buffer)
                        if pisa_status.err:
                            return HttpResponse('Une erreur est survenue lors de la génération du PDF.')

                        pdf_buffer.seek(0)  # Revenir au début du buffer
                        ticket.pdf.save(f'ticket_{ticket.id}.pdf', pdf_buffer, save=True)

                        # Réinitialiser le buffer pour la réponse
                        pdf_buffer.seek(0)
                        response = HttpResponse(pdf_buffer, content_type='application/pdf')
                        response['Content-Disposition'] = f'attachment; filename="ticket_{ticket.id}.pdf"'
                        messages.success(request, "Votre achat a été effectué avec succès !")
                        return response  # Télécharger automatiquement le PDF
                else:
                    # Rechercher d'autres bus programmés pour la même destination à la même heure
                    other_buses = Destination.objects.filter(
                        name=destination.name, 
                        heure_depart=destination.heure_depart
                    ).exclude(id=destination_id)

                    for bus_dest in other_buses:
                        if Ticket.objects.filter(destination=bus_dest, departure_date=departure_date).count() < bus_dest.bus.nombre_place:
                            ticket = ticket_form.save(commit=False)
                            ticket.destination = bus_dest
                            ticket.user = user
                            ticket.is_confirmed = True

                            # Vérifier si le montant payé est suffisant
                            if ticket.amount_paid < bus_dest.montant:
                                messages.error(request, "Le montant payé est insuffisant.")
                            else:
                                ticket.save()

                                # Créer le paiement associé
                                payment = Payment.objects.create(ticket=ticket, transaction_id="SIMULATED_TRANSACTION_ID")

                                # Générer le PDF du ticket
                                template_path = 'ticket_pdf_template.html'
                                context = {
                                    'ticket': ticket,
                                    'destination': bus_dest,
                                    'departure_time': bus_dest.heure_depart,  # Ajouter l'heure de départ au contexte
                                }
                                template = get_template(template_path)
                                html = template.render(context)

                                # Convertir en PDF
                                pdf_buffer = io.BytesIO()
                                pisa_status = pisa.CreatePDF(html, dest=pdf_buffer)
                                if pisa_status.err:
                                    return HttpResponse('Une erreur est survenue lors de la génération du PDF.')

                                pdf_buffer.seek(0)  # Revenir au début du buffer
                                ticket.pdf.save(f'ticket_{ticket.id}.pdf', pdf_buffer, save=True)

                                # Réinitialiser le buffer pour la réponse
                                pdf_buffer.seek(0)
                                response = HttpResponse(pdf_buffer, content_type='application/pdf')
                                response['Content-Disposition'] = f'attachment; filename="ticket_{ticket.id}.pdf"'
                                messages.success(request, "Votre achat a été effectué avec succès dans un autre bus !")
                                return response  # Télécharger automatiquement le PDF

                    messages.error(request, 'Aucun bus disponible pour cette destination et cette heure.')
            else:
                messages.error(request, 'L\'heure de départ doit être supérieure à la time zone actuelle.')
        else:
            messages.error(request, "Les informations du ticket sont incorrectes. Veuillez réessayer.")
    else:
        ticket_form = TicketForm()

    return render(request, 'purchase_ticket.html', {'destination': destination, 'ticket_form': ticket_form})

@login_required
def payment_list(request):
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    destination_id = request.GET.get('destination')
    
    payments = Payment.objects.all().order_by('-payment_date')

    if start_date and end_date:
        start_date = datetime.strptime(start_date, '%Y-%m-%d')
        end_date = datetime.strptime(end_date, '%Y-%m-%d')
        payments = payments.filter(payment_date__range=(start_date, end_date))
    
    if destination_id:
        payments = payments.filter(ticket__destination_id=destination_id)
    
    destinations = Destination.objects.all()

    return render(request, 'payment_list.html', {
        'payments': payments,
        'start_date': start_date,
        'end_date': end_date,
        'destinations': destinations,
        'selected_destination': destination_id
    })

























@login_required
# Vue de déconnexion
@login_required
def user_logout(request):
    logout(request)
    return redirect('login')  # Rediriger vers la page de connexion après la déconnexion