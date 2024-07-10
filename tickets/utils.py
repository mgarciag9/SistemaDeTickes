from io import BytesIO # nos ayuda a convertir un html en pdf
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator


class Nodo:
    def __init__(self, data=None):
        self.data = data  # Dato que almacena el nodo
        self.next = None  # Puntero al siguiente nodo en la cola

class Cola:
    def __init__(self):
        self.frente = None  # Puntero al frente de la cola
        self.final = None   # Puntero al final de la cola

    def encolar(self, item):
        # Crear un nuevo nodo con el ítem
        nuevo_nodo = Nodo(item)
        if self.final:
            # Si la cola no está vacía, apuntar el final actual al nuevo nodo
            self.final.next = nuevo_nodo
        self.final = nuevo_nodo  # Actualizar el final de la cola
        if not self.frente:
            # Si la cola estaba vacía, actualizar también el frente
            self.frente = nuevo_nodo

    def desencolar(self):
        if self.frente:
            # Obtener el dato del frente de la cola
            item = self.frente.data
            # Mover el frente al siguiente nodo
            self.frente = self.frente.next
            if not self.frente:
                # Si la cola quedó vacía, también actualizar el final
                self.final = None
            return item
        raise Exception("La cola está vacía")  # Lanzar excepción si la cola está vacía

    def esta_vacia(self):
        return self.frente is None  # Verificar si la cola está vacía

    def __iter__(self):
        # Hacer que la cola sea iterable
        actual = self.frente
        while actual:
            yield actual.data
            actual = actual.next

    def __len__(self):
        # Obtener la longitud de la cola
        actual = self.frente
        contador = 0
        while actual:
            contador += 1
            actual = actual.next
        return contador

def quicksort(arr, key=lambda x: x, reverse=False):
    # Caso base: si el array tiene uno o ningún elemento, está ordenado
    if len(arr) <= 1:
        return arr
    pivot = arr[len(arr) // 2]  # Elegimos el elemento medio como pivote
    if reverse:
        # Particionamos el array en tres partes: menor, igual y mayor que el pivote, para orden descendente
        izquierda = [x for x in arr if key(x) > key(pivot)]
        medio = [x for x in arr if key(x) == key(pivot)]
        derecha = [x for x in arr if key(x) < key(pivot)]
    else:
        # Particionamos el array en tres partes: menor, igual y mayor que el pivote, para orden ascendente
        izquierda = [x for x in arr if key(x) < key(pivot)]
        medio = [x for x in arr if key(x) == key(pivot)]
        derecha = [x for x in arr if key(x) > key(pivot)]
    # Ordenamos recursivamente y concatenamos los resultados
    return quicksort(izquierda, key, reverse) + medio + quicksort(derecha, key, reverse)

def busqueda_binaria(arr, objetivo, key=lambda x: x):
    bajo, alto = 0, len(arr) - 1  # Definimos los límites inferior y superior
    resultados = []  # Lista para almacenar los resultados
    while bajo <= alto:
        medio = (bajo + alto) // 2  # Calculamos el índice medio
        if key(arr[medio]) < objetivo:
            bajo = medio + 1  # Ajustamos el límite inferior
        elif key(arr[medio]) > objetivo:
            alto = medio - 1  # Ajustamos el límite superior
        else:
            # Si encontramos el objetivo, exploramos a izquierda y derecha para encontrar todos los elementos iguales
            izquierda = medio
            while izquierda >= 0 and key(arr[izquierda]) == objetivo:
                izquierda -= 1
            derecha = medio
            while derecha < len(arr) and key(arr[derecha]) == objetivo:
                derecha += 1
            # Agregamos los elementos encontrados a la lista de resultados
            resultados = arr[izquierda + 1:derecha]
            break
    return resultados  # Devolvemos la lista de resultados

def render_to_pdf(template_src, context_dict={}):
    template = get_template(template_src)
    html  = template.render(context_dict)
    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html.encode("ISO-8859-1")), result)
    if not pdf.err:
        return HttpResponse(result.getvalue(), content_type='application/pdf')
    return None

phone_regex = RegexValidator(regex=r'^\d{9,15}$', message="El número de teléfono debe contener entre 9 y 15 dígitos.")
 
def valida_cedula(value):
    cedula = str(value)
    if not cedula.isdigit():
        raise ValidationError('La cédula debe contener solo números.')

    longitud = len(cedula)
    if longitud != 10:
        raise ValidationError('La cédula debe tener 10 dígitos.')

    coeficientes = [2, 1, 2, 1, 2, 1, 2, 1, 2]
    total = 0
    for i in range(9):
        digito = int(cedula[i])
        coeficiente = coeficientes[i]
        producto = digito * coeficiente
        if producto > 9:
            producto -= 9
        total += producto

    digito_verificador = (total * 9) % 10
    if digito_verificador != int(cedula[9]):
        raise ValidationError('La cédula no es válida.')

