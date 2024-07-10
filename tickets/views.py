from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.contrib import messages
from .models import Ticket
from .forms import TicketForm
from django.views.generic import View
from django.http import HttpResponse, JsonResponse
from django.template.loader import get_template
from .utils import quicksort, busqueda_binaria, Cola,render_to_pdf

ticket_cola = Cola()

def inicio(request):
    try:
        tickets = list(ticket_cola)
        attended_tickets = list(Ticket.objects.filter(atendido_en__isnull=False))
        tickets_ordenados = quicksort(tickets, key=lambda x: x.creado_en)
        attended_tickets_ordenados = quicksort(attended_tickets, key=lambda x: x.atendido_en)
        return render(request, 'tickets/index.html', {
            'tickets': tickets_ordenados,
            'attended_tickets': attended_tickets_ordenados
        })
    except Exception as e:
        messages.error(request, f'Error al cargar la página de inicio: {str(e)}')
        return redirect('inicio')

def crear_ticket(request):
    try:
        if request.method == 'POST':
            form = TicketForm(request.POST)
            if form.is_valid():
                ticket = form.save()
                ticket_cola.encolar(ticket)
                messages.success(request, 'El ticket ha sido creado exitosamente.')
                return redirect('inicio')
            else:
                messages.error(request, 'Hubo un error al crear el ticket. Por favor, verifica los datos e intenta nuevamente.')
        else:
            form = TicketForm()
        return render(request, 'tickets/crear_ticket.html', {'form': form})
    except Exception as e:
        messages.error(request, f'Error al crear el ticket: {str(e)}')
        return redirect('crear_ticket')

def atender_ticket(request, ticket_id):
    try:
        ticket = get_object_or_404(Ticket, id=ticket_id)
        primer_ticket = next(iter(ticket_cola), None)

        if primer_ticket and ticket != primer_ticket:
            messages.error(request, 'Solo puedes atender al primer ticket en la cola.')
            return redirect('inicio')

        ticket.atendido_en = timezone.now()
        ticket.save()
        ticket_cola.desencolar()
        messages.success(request, 'El ticket ha sido atendido exitosamente.')
        return redirect('inicio')
    except Exception as e:
        messages.error(request, f'Error al atender el ticket: {str(e)}')
        return redirect('inicio')

def tickets_atendidos(request):
    try:
        orden = request.GET.get('orden', 'atendido_en')  # Por defecto, ordenar por 'atendido_en'
        direccion = request.GET.get('direccion', 'asc')  # Por defecto, ordenar ascendentemente
        tickets = list(Ticket.objects.filter(atendido_en__isnull=False))

        reverse = direccion == 'desc'
        if orden == 'creado_en':
            tickets_ordenados = quicksort(tickets, key=lambda x: x.creado_en, reverse=reverse)
        elif orden == 'nombre':
            tickets_ordenados = quicksort(tickets, key=lambda x: (x.nombre.lower(), x.apellidos.lower()), reverse=reverse)
        elif orden == 'edad':
            tickets_ordenados = quicksort(tickets, key=lambda x: x.edad, reverse=reverse)
        else:
            tickets_ordenados = quicksort(tickets, key=lambda x: x.atendido_en, reverse=reverse)
        
        orden_direcciones = {
            'nombre': 'desc' if orden == 'nombre' and direccion == 'asc' else 'asc',
            'edad': 'desc' if orden == 'edad' and direccion == 'asc' else 'asc',
            'creado_en': 'desc' if orden == 'creado_en' and direccion == 'asc' else 'asc',
            'atendido_en': 'desc' if orden == 'atendido_en' and direccion == 'asc' else 'asc'
        }
        
        return render(request, 'tickets/tickets_atendidos.html', {
            'tickets': tickets_ordenados,
            'orden': orden,
            'direccion': direccion,
            'orden_direcciones': orden_direcciones
        })
    except Exception as e:
        messages.error(request, f'Error al cargar la página de tickets atendidos: {str(e)}')
        return redirect('inicio')

def buscar_ticket(request):
    try:
        criterio = request.GET.get('criterio')
        valor = request.GET.get('valor')
        tickets = list(ticket_cola)

        if not criterio or not valor:
            messages.error(request, 'Por favor, proporciona un criterio y valor de búsqueda.')
            return redirect('inicio')

        if criterio == 'edad':
            valor = int(valor)
            resultado = busqueda_binaria(tickets, valor, key=lambda x: x.edad)
        elif criterio == 'dni':
            resultado = busqueda_binaria(tickets, valor, key=lambda x: x.dni)
        elif criterio == 'nombre':
            resultado = busqueda_binaria(tickets, valor, key=lambda x: x.nombre)
        elif criterio == 'apellidos':
            resultado = busqueda_binaria(tickets, valor, key=lambda x: x.apellidos)
        else:
            messages.error(request, 'Criterio de búsqueda no válido.')
            return redirect('inicio')

        if not resultado:
            messages.error(request, 'No se encontraron resultados para la búsqueda.')

        return render(request, 'tickets/index.html', {'tickets': resultado})
    except Exception as e:
        messages.error(request, f'Error al buscar el ticket: {str(e)}')
        return redirect('inicio')

class ListEmpleadosPdf(View):

    def get(self, request, *args, **kwargs):
        try:
            tickets = Ticket.objects.all()
            data = {
                'count': tickets.count(),
                'tickets': tickets
            }
            pdf = render_to_pdf('tickets/ticket.html', data)
            return HttpResponse(pdf, content_type='application/pdf')
        except Exception as e:
            messages.error(request, f'Error al generar el PDF: {str(e)}')
            return redirect('inicio')
