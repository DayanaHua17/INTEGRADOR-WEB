from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone
from django.contrib.auth.hashers import check_password
from .models import Encomienda, Cliente, Empleado, Reclamo, Motivo, Terminal,Comprobante

# Decorador para verificar si el empleado está logueado
def empleado_requerido(view_func):
    def wrapper(request, *args, **kwargs):
        if 'empleado_id' not in request.session:
            return redirect('login_empleado')
        return view_func(request, *args, **kwargs)
    return wrapper

# Vista del panel principal del empleado logueado
@empleado_requerido
def panel_empleado(request):
    empleado_id = request.session.get('empleado_id')
    empleado = Empleado.objects.get(id=empleado_id) if empleado_id else None
    return render(request, 'layout/base_empleado.html', {'empleado': empleado})

# Vista para el listado de clientes
@empleado_requerido
def listado_clientes(request):
    empleado_id = request.session.get('empleado_id')
    empleado = Empleado.objects.get(id=empleado_id)
    clientes = Cliente.objects.all()
    return render(request, 'listado_clientes.html', {'clientes': clientes, 'empleado': empleado})

# Vista para el listado de encomiendas

@empleado_requerido
def listado_encomiendas(request):
    empleado_id = request.session.get('empleado_id')
    empleado = Empleado.objects.get(id=empleado_id)
    encomiendas = Encomienda.objects.all()
    return render(request, 'listado_encomiendas.html', {'encomiendas': encomiendas, 'empleado': empleado})

# Vista para el registro de clientes
@empleado_requerido
def registro_cliente(request):
    empleado_id = request.session.get('empleado_id')
    empleado = Empleado.objects.get(id=empleado_id)
    if request.method == "POST":
        dni = request.POST.get('dni')
        nombres = request.POST.get('nombres')
        apellidos = request.POST.get('apellidos')
        telefono = request.POST.get('telefono')
        nuevo_cliente = Cliente(dni=dni, nombres=nombres, apellidos=apellidos, telefono=telefono)
        nuevo_cliente.save()
        return redirect('listado_clientes')
    return render(request, 'registro_cliente.html', {'empleado': empleado})

# Vista para registrar encomiendas
@empleado_requerido
def registro_encomienda(request):
    empleado_id = request.session.get('empleado_id')
    empleado = Empleado.objects.get(id=empleado_id)
    terminales = Terminal.objects.all()
    CONDICIONES_ENVIO = [
        ('fragil', 'Frágil'),
        ('normal', 'Normal'),
        ('perecedero', 'Perecedero'),
    ]
    if request.method == "POST":
        descripcion = request.POST.get('descripcion')
        remitente = request.POST.get('remitente')
        destinatario = request.POST.get('destinatario')
        placa_vehiculo = request.POST.get('placa_vehiculo')
        terminal_partida_id = request.POST.get('terminal_partida')
        terminal_destino_id = request.POST.get('terminal_destino')
        volumen = request.POST.get('volumen')
        estado = request.POST.get('estado')
        condicion_envio = request.POST.get('condicion_envio')
        cantidad_paquetes = request.POST.get('cantidad_paquetes')

        remitente_obj = Cliente.objects.get(id=remitente)
        destinatario_obj = Cliente.objects.get(id=destinatario)
        terminal_partida_obj = Terminal.objects.get(id=terminal_partida_id)
        terminal_destino_obj = Terminal.objects.get(id=terminal_destino_id)
        fecha_salida = timezone.now()

        nueva_encomienda = Encomienda(
            descripcion=descripcion,
            remitente=remitente_obj,
            destinatario=destinatario_obj,
            placa_vehiculo=placa_vehiculo,
            terminal_partida=terminal_partida_obj,
            terminal_destino=terminal_destino_obj,
            volumen=volumen,
            estado=estado,
            condicion_envio=condicion_envio,
            cantidad_paquetes=cantidad_paquetes,
            fecha_salida=fecha_salida,
            empleado_registro=empleado,
            empleado_entrega=empleado
        )
        nueva_encomienda.save()

        messages.success(request, 'Encomienda registrada con éxito.')
        return redirect('listado_encomiendas')
    return render(request, 'registro_encomienda.html', {'empleado': empleado, 'terminales': terminales, 'condiciones_envio': CONDICIONES_ENVIO})

# Vista para el listado de reclamos
@empleado_requerido
def listado_reclamos(request):
    empleado_id = request.session.get('empleado_id')
    empleado = Empleado.objects.get(id=empleado_id)
    reclamos = Reclamo.objects.all()
    return render(request, 'listado_reclamos.html', {'reclamos': reclamos, 'empleado': empleado})

# Vista para actualizar el estado de una encomienda
@empleado_requerido
def actualizar_estado_encomienda(request, encomienda_id):
    empleado_id = request.session.get('empleado_id')
    empleado = Empleado.objects.get(id=empleado_id)
    encomienda = get_object_or_404(Encomienda, id=encomienda_id)
    comprobante = Comprobante.objects.filter(encomienda=encomienda).first()

    if request.method == 'POST':
        nuevo_estado = request.POST.get('estado')
        nuevo_estado_pago = request.POST.get('estado_pago')
        encomienda.estado = nuevo_estado
        if comprobante:
            comprobante.estado_pago = nuevo_estado_pago
            comprobante.save()
        encomienda.save()
        messages.success(request, 'La encomienda se actualizó de manera exitosa.')
        return redirect('estado_actualizado')

    return render(request, 'actualizar_estado_encomienda.html', {
        'encomienda': encomienda,
        'comprobante': comprobante,
        'empleado': empleado
    })

@empleado_requerido
def estado_actualizado(request):
    empleado_id = request.session.get('empleado_id')
    empleado = Empleado.objects.get(id=empleado_id)
    return render(request, 'estado_actualizado.html', {'empleado': empleado})

# Vista para cerrar la sesión del empleado
@empleado_requerido
def logout_view(request):
    logout(request)
    return redirect('login_empleado')

# Vista para la página principal del cliente
def index_cliente(request):
    return render(request, 'index_cliente.html')

# Vista para la sección "Nosotros"
def nosotros(request):
    return render(request, 'nosotros.html')

# Vista para la sección "Contáctanos"
def contactanos(request):
    return render(request, 'contactanos.html')

# Vista para el formulario de reclamos
def reclamos(request):
    if request.method == 'POST':
        motivo = request.POST.get('motivo')
        descripcion = request.POST.get('descripcion')
        nuevo_reclamo = Reclamo(motivo=motivo, descripcion=descripcion)
        nuevo_reclamo.save()
        messages.success(request, 'Reclamo enviado con éxito.')
        return redirect('reclamos')
    return render(request, 'reclamos.html')

# Vista de inicio de sesión para el empleado
def login_empleado(request):
    if request.method == 'POST':
        email = request.POST.get('correo')
        password = request.POST.get('password')
        try:
            empleado = Empleado.objects.get(correo=email)
            if check_password(password, empleado.password):
                request.session['empleado_id'] = empleado.id
                messages.success(request, 'Sesión iniciada con éxito')
                return redirect('panel_empleado')
            else:
                messages.error(request, 'Correo o contraseña incorrectos')
        except Empleado.DoesNotExist:
            messages.error(request, 'El correo ingresado no pertenece a ningún empleado registrado.')
    return render(request, 'login_empleado.html')


@empleado_requerido
def actualizar_estado_form(request, encomienda_id=None):
    encomienda = None
    comprobante = None
    monto = 'N/A'

    if encomienda_id:
        encomienda = get_object_or_404(Encomienda, id=encomienda_id)
        comprobante = Comprobante.objects.filter(encomienda=encomienda).first()
        monto = comprobante.monto if comprobante else 'N/A'
    
    if request.method == 'POST' and encomienda:
        # Obtener el estado de la encomienda y estado de pago del formulario
        nuevo_estado = request.POST.get('estado')
        nuevo_estado_pago = request.POST.get('estado_pago')
        
        # Actualizar los datos de la encomienda y el comprobante
        encomienda.estado = nuevo_estado
        if comprobante:
            comprobante.estado_pago = nuevo_estado_pago
            comprobante.save()
        encomienda.save()
        
        # Mensaje de éxito y redirección al listado de encomiendas
        messages.success(request, 'La encomienda se actualizó de manera exitosa.')
        return redirect('listado_encomiendas')

    return render(request, 'actualizar_estado_form.html', {
        'encomienda': encomienda,
        'comprobante': comprobante,
        'monto': monto
    })