from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone


# ======== PRIMERO: MODELO DE USUARIO ========

class Usuario(AbstractUser):
    """
    Modelo de usuario personalizado con roles
    """
    ROLES = (
        ('ADMIN', 'Administrador'),
        ('BODEGUERO', 'Bodeguero'),
        ('SUPERVISOR', 'Supervisor'),
    )

    rol = models.CharField(max_length=20, choices=ROLES, default='BODEGUERO')
    telefono = models.CharField(max_length=15, blank=True)
    rut = models.CharField(max_length=12, unique=True, null=True, blank=True)
    fecha_contratacion = models.DateField(null=True, blank=True)
    activo = models.BooleanField(default=True)

    supervisor = models.OneToOneField(
        'Supervisor',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='usuario_sistema'
    )

    class Meta:
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'

    def __str__(self):
        return f"{self.get_full_name()} ({self.get_rol_display()})"

    def is_admin(self):
        return self.rol == 'ADMIN'

    def is_bodeguero(self):
        return self.rol == 'BODEGUERO'

    def is_supervisor(self):
        return self.rol == 'SUPERVISOR'

    def get_permisos(self):
        """Retorna los permisos según el rol"""
        if self.is_admin():
            return {
                'obreros': ['view', 'add', 'change', 'delete'],
                'bodegas': ['view', 'add', 'change', 'delete'],
                'bodegueros': ['view', 'add', 'change', 'delete'],
                'materiales': ['view'],
                'herramientas': ['view'],
                'prestamos': ['view'],
                'reportes': ['view', 'export'],
            }
        elif self.is_bodeguero():
            return {
                'materiales': ['view', 'add', 'change', 'delete'],
                'herramientas': ['view', 'add', 'change', 'delete'],
                'prestamos': ['view', 'add', 'change', 'delete'],
                'bodegas': ['view'],
                'obreros': ['view'],
            }
        elif self.is_supervisor():
            return {
                'obras': ['view'],
                'obreros': ['view'],
                'materiales': ['view'],
                'herramientas': ['view'],
                'prestamos': ['view'],
                'bodegas': ['view'],
                'reportes': ['view', 'add', 'export'],
                'informes': ['view', 'add', 'change', 'delete'],
            }
        return {}


# ======== COMUNAS, ESTADOS Y CATEGORÍAS ========

class Comuna(models.Model):
    codigo_comuna = models.AutoField(primary_key=True)
    nombre_comuna = models.CharField(max_length=150)

    def __str__(self):
        return self.nombre_comuna


class CategoriaObra(models.Model):
    codigo_categoria = models.AutoField(primary_key=True)
    nombre_categoria = models.CharField(max_length=150)

    def __str__(self):
        return self.nombre_categoria


class EstadoObra(models.Model):
    codigo_estado = models.AutoField(primary_key=True)
    nombre_estado = models.CharField(max_length=100)

    def __str__(self):
        return self.nombre_estado


# ======== OBRAS ========

class Obra(models.Model):
    codigo_obra = models.AutoField(primary_key=True)
    nombre_obra = models.CharField(max_length=200)
    direccion_obra = models.CharField(max_length=300, blank=True)
    metros_cuadrados = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    fecha_inicio = models.DateField(blank=True, null=True)
    fecha_termino = models.DateField(blank=True, null=True)

    codigo_estado = models.ForeignKey(EstadoObra, on_delete=models.PROTECT, related_name="obras")
    codigo_categoria = models.ForeignKey(CategoriaObra, on_delete=models.PROTECT, related_name="obras")
    codigo_comuna = models.ForeignKey(Comuna, on_delete=models.PROTECT, related_name="obras")

    def __str__(self):
        return self.nombre_obra


# ======== SUPERVISORES E INFORMES ========

class Especializacion(models.Model):
    codigo_especializacion = models.AutoField(primary_key=True)
    nombre_especializacion = models.CharField(max_length=150)

    def __str__(self):
        return self.nombre_especializacion


class Supervisor(models.Model):
    id_supervisor = models.AutoField(primary_key=True)
    nombre_supervisor = models.CharField(max_length=150)
    apellido_supervisor = models.CharField(max_length=150)
    codigo_obra = models.ForeignKey(Obra, on_delete=models.PROTECT, related_name="supervisores")
    codigo_especializacion = models.ForeignKey(
        Especializacion, on_delete=models.SET_NULL, null=True, blank=True, related_name="supervisores"
    )

    def __str__(self):
        return f"{self.nombre_supervisor} {self.apellido_supervisor}"


class Informe(models.Model):
    codigo_informe = models.AutoField(primary_key=True)
    titulo_informe = models.CharField(max_length=250)
    fecha_informe = models.DateTimeField(auto_now=True)
    descripcion = models.TextField(blank=True)
    id_supervisor = models.ForeignKey(Supervisor, on_delete=models.PROTECT, related_name="informes")

    def __str__(self):
        return self.titulo_informe


# ======== MATERIALES ========

class TipoMaterial(models.Model):
    codigo_tipo = models.AutoField(primary_key=True)
    nombre_tipo = models.CharField(max_length=150)

    def __str__(self):
        return self.nombre_tipo


class MarcaMaterial(models.Model):
    codigo_marca = models.AutoField(primary_key=True)
    nombre_marca = models.CharField(max_length=150)

    def __str__(self):
        return self.nombre_marca


from django.db import models

class Material(models.Model):
    codigo_material = models.AutoField(primary_key=True)
    nombre_material = models.CharField(max_length=200)
    codigo_tipo = models.ForeignKey('TipoMaterial', on_delete=models.SET_NULL, null=True, related_name="materiales")
    codigo_marca = models.ForeignKey('MarcaMaterial', on_delete=models.SET_NULL, null=True, related_name="materiales")

    cantidad = models.DecimalField(max_digits=12, blank=True, null=True, decimal_places=2)
    unidad_medida = models.CharField(max_length=20, blank=True)

    # 🔹 Especificaciones técnicas
    color = models.CharField(max_length=50, blank=True)
    condicion = models.CharField(max_length=50, blank=True)  # nuevo, usado, reciclado...
    acabado = models.CharField(max_length=50, blank=True)    # pulido, mate, brillante, rugoso...
    presentacion = models.CharField(max_length=50, blank=True)  # rollo, plancha, tubo, etc.

    
    densidad = models.DecimalField(max_digits=10, decimal_places=3, blank=True, null=True)
    peso_especifico = models.DecimalField(max_digits=10, decimal_places=3, blank=True, null=True)
    resistencia_traccion = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    dureza = models.CharField(max_length=50, blank=True, null=True)
    conductividad_termica = models.DecimalField(max_digits=10, decimal_places=3, blank=True, null=True)
    conductividad_electrica = models.DecimalField(max_digits=10, decimal_places=3, blank=True, null=True)
    punto_fusion = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    espesor = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    largo = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    ancho = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    diametro = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    composicion = models.TextField(blank=True, null=True)  # descripción de la mezcla o composición química
    norma_tecnica = models.CharField(max_length=100, blank=True, null=True)  # ASTM, ISO, etc.
    tratamiento_superficial = models.CharField(max_length=100, blank=True, null=True)
    temperatura_operacion = models.CharField(max_length=50, blank=True, null=True)
    resistencia_quimica = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return self.nombre_material



class ObraMaterial(models.Model):
    codigo_obra = models.ForeignKey(Obra, on_delete=models.CASCADE, related_name="materiales_asignados")
    codigo_material = models.ForeignKey(Material, on_delete=models.CASCADE, related_name="obras_asignadas")
    cantidad_asignada = models.DecimalField(max_digits=12, decimal_places=2)
    fecha_asignacion = models.DateField(blank=True, null=True)

    class Meta:
        unique_together = ("codigo_obra", "codigo_material")

    def __str__(self):
        return f"{self.codigo_material} → {self.codigo_obra}"


# ======== BODEGAS ========

class TipoBodega(models.Model):
    codigo_tipo = models.AutoField(primary_key=True)
    nombre_tipo = models.CharField(max_length=150)

    def __str__(self):
        return self.nombre_tipo


class Bodega(models.Model):
    codigo_bodega = models.AutoField(primary_key=True)
    nombre_bodega = models.CharField(max_length=200)
    direccion_bodega = models.CharField(max_length=300, blank=True)
    capacidad = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    codigo_tipo = models.ForeignKey(TipoBodega, on_delete=models.SET_NULL, null=True, related_name="bodegas")

    def __str__(self):
        return self.nombre_bodega


class Bodeguero(models.Model):
    id_bodeguero = models.AutoField(primary_key=True)
    nombre_bodeguero = models.CharField(max_length=150)
    apellido_bodeguero = models.CharField(max_length=150)
    sueldo = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)

    def __str__(self):
        return f"{self.nombre_bodeguero} {self.apellido_bodeguero}"


class BodegueroBodega(models.Model):
    codigo_bodega = models.ForeignKey(Bodega, on_delete=models.CASCADE, related_name="bodegueros")
    id_bodeguero = models.ForeignKey(Bodeguero, on_delete=models.CASCADE, related_name="bodegas")

    class Meta:
        unique_together = ("codigo_bodega", "id_bodeguero")


class MaterialBodega(models.Model):
    codigo_material = models.ForeignKey(Material, on_delete=models.CASCADE, related_name="bodegas")
    codigo_bodega = models.ForeignKey(Bodega, on_delete=models.CASCADE, related_name="materiales")
    cantidad_almacenada = models.DecimalField(max_digits=12, decimal_places=2)

    class Meta:
        unique_together = ("codigo_material", "codigo_bodega")

    def __str__(self):
        return f"{self.codigo_material} en {self.codigo_bodega}"


# ======== HERRAMIENTAS ========

class CategoriaHerramienta(models.Model):
    codigo_categoria = models.AutoField(primary_key=True)
    nombre_categoria = models.CharField(max_length=150)

    def __str__(self):
        return self.nombre_categoria


class TipoHerramienta(models.Model):
    codigo_tipo = models.AutoField(primary_key=True)
    nombre_tipo = models.CharField(max_length=150)

    def __str__(self):
        return self.nombre_tipo


class MarcaHerramienta(models.Model):
    codigo_marca = models.AutoField(primary_key=True)
    nombre_marca = models.CharField(max_length=150)

    def __str__(self):
        return self.nombre_marca


class EstadoHerramienta(models.Model):
    codigo_estado = models.AutoField(primary_key=True)
    nombre_estado = models.CharField(max_length=100)

    def __str__(self):
        return self.nombre_estado


class Herramienta(models.Model):
    codigo_herramienta = models.AutoField(primary_key=True)
    nombre_herramienta = models.CharField(max_length=200)

    largo = models.CharField(max_length=200, blank=True)
    ancho = models.CharField(max_length=200, blank=True)
    alto = models.CharField(max_length=200, blank=True)
    modelo = models.CharField(max_length=200, blank=True)
    potencia = models.CharField(max_length=10, blank=True)
    voltaje = models.CharField(max_length=10, blank=True)
    tamaño_mandril = models.CharField(max_length=10, blank=True)
    rpm = models.CharField(max_length=10, blank=True)
    alimentacion = models.CharField(max_length=20, blank=True)
    largo_cable = models.CharField(max_length=200, blank=True)
    alcance = models.CharField(max_length=200, blank=True)
    capacidad = models.CharField(max_length=200, blank=True)
    diametro = models.CharField(max_length=200, blank=True)
    ruedas = models.CharField(max_length=10, blank=True)
    textura = models.CharField(max_length=20, blank=True)
    especificaciones = models.CharField(max_length=100, blank=True)

    codigo_tipo = models.ForeignKey(TipoHerramienta, on_delete=models.SET_NULL, null=True, related_name="herramientas")
    codigo_categoria = models.ForeignKey(CategoriaHerramienta, on_delete=models.SET_NULL, null=True, related_name="herramientas")
    codigo_marca = models.ForeignKey(MarcaHerramienta, on_delete=models.SET_NULL, null=True, related_name="herramientas")
    codigo_estado = models.ForeignKey(EstadoHerramienta, on_delete=models.SET_NULL, null=True, related_name="herramientas")

    def __str__(self):
        return self.nombre_herramienta


class HerramientaBodega(models.Model):
    codigo_herramienta = models.ForeignKey(Herramienta, on_delete=models.CASCADE, related_name="bodegas")
    codigo_bodega = models.ForeignKey(Bodega, on_delete=models.CASCADE, related_name="herramientas")
    cantidad_almacenada = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ("codigo_herramienta", "codigo_bodega")

    def __str__(self):
        return f"{self.codigo_herramienta} en {self.codigo_bodega}"


# ======== OBREROS ========

class Cargo(models.Model):
    codigo_cargo = models.AutoField(primary_key=True)
    nombre_cargo = models.CharField(max_length=150)

    def __str__(self):
        return self.nombre_cargo


class Obrero(models.Model):
    id_obrero = models.AutoField(primary_key=True)
    nombre_obrero = models.CharField(max_length=150)
    apellido_obrero = models.CharField(max_length=150)
    codigo_obra = models.ForeignKey(Obra, on_delete=models.SET_NULL, null=True, related_name="obreros")
    codigo_cargo = models.ForeignKey(Cargo, on_delete=models.SET_NULL, null=True, related_name="obreros")

    def __str__(self):
        return f"{self.nombre_obrero} {self.apellido_obrero}"


class ObreroHerramienta(models.Model):
    id_obrero = models.ForeignKey(Obrero, on_delete=models.CASCADE, related_name="herramientas")
    codigo_herramienta = models.ForeignKey(Herramienta, on_delete=models.CASCADE, related_name="obreros")
    fecha_inicio_uso = models.DateField(blank=True, null=True)
    fecha_termino_uso = models.DateField(blank=True, null=True)

    class Meta:
        unique_together = ("id_obrero", "codigo_herramienta")

    def __str__(self):
        return f"{self.codigo_herramienta} → {self.id_obrero}"


# ======== PRÉSTAMOS DE MATERIALES ========

class PrestamoMaterial(models.Model):
    codigo_prestamo = models.AutoField(primary_key=True)
    id_obrero = models.ForeignKey(Obrero, on_delete=models.PROTECT, related_name="prestamos_materiales")
    codigo_material = models.ForeignKey(Material, on_delete=models.PROTECT, related_name="prestamos")
    cantidad_prestada = models.DecimalField(max_digits=12, decimal_places=2)
    fecha_prestamo = models.DateTimeField(default=timezone.now)
    fecha_devolucion_esperada = models.DateField(null=True, blank=True)
    observaciones = models.TextField(blank=True)
    devuelto = models.BooleanField(default=False)

    def __str__(self):
        return f"Préstamo {self.codigo_prestamo} - {self.codigo_material} a {self.id_obrero}"

    class Meta:
        ordering = ['-fecha_prestamo']


class DevolucionMaterial(models.Model):
    codigo_devolucion = models.AutoField(primary_key=True)
    codigo_prestamo = models.ForeignKey(PrestamoMaterial, on_delete=models.PROTECT, related_name="devoluciones")
    cantidad_devuelta = models.DecimalField(max_digits=12, decimal_places=2)
    cantidad_usada = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    merma = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        help_text="Cantidad que sobró pero no se puede reutilizar"
    )
    fecha_devolucion = models.DateTimeField(default=timezone.now)
    observaciones = models.TextField(blank=True)

    def __str__(self):
        return f"Devolución {self.codigo_devolucion} - Préstamo {self.codigo_prestamo.codigo_prestamo}"

    def save(self, *args, **kwargs):
        self.cantidad_usada = self.codigo_prestamo.cantidad_prestada - self.cantidad_devuelta - self.merma
        super().save(*args, **kwargs)
        self.codigo_prestamo.devuelto = True
        self.codigo_prestamo.save()

    class Meta:
        ordering = ['-fecha_devolucion']


class PrestamoHerramienta(models.Model):
    codigo_prestamo = models.AutoField(primary_key=True)
    id_obrero = models.ForeignKey(Obrero, on_delete=models.PROTECT, related_name="prestamos_herramientas")
    codigo_herramienta = models.ForeignKey(Herramienta, on_delete=models.PROTECT, related_name="prestamos")
    fecha_prestamo = models.DateTimeField(default=timezone.now)
    fecha_devolucion_esperada = models.DateField(null=True, blank=True)
    fecha_devolucion_real = models.DateTimeField(null=True, blank=True)
    estado_al_prestar = models.CharField(max_length=100, blank=True)
    estado_al_devolver = models.CharField(max_length=100, blank=True)
    observaciones_prestamo = models.TextField(blank=True)
    observaciones_devolucion = models.TextField(blank=True)
    devuelto = models.BooleanField(default=False)

    def __str__(self):
        return f"Préstamo {self.codigo_prestamo} - {self.codigo_herramienta} a {self.id_obrero}"

    class Meta:
        ordering = ['-fecha_prestamo']


# ======== SESIONES DE USUARIO ========

class SesionUsuario(models.Model):
    """
    Registro de sesiones para auditoría
    """
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='sesiones')
    fecha_inicio = models.DateTimeField(auto_now_add=True)
    fecha_fin = models.DateTimeField(null=True, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)

    class Meta:
        ordering = ['-fecha_inicio']
        verbose_name = 'Sesión de Usuario'
        verbose_name_plural = 'Sesiones de Usuario'

    def __str__(self):
        return f"Sesión {self.usuario.username} - {self.fecha_inicio}"


# ======== LOG DE ACTIVIDADES ========

class LogActividad(models.Model):
    """
    Registro de todas las actividades del sistema
    """
    ACCIONES = (
        ('CREATE', 'Creación'),
        ('UPDATE', 'Actualización'),
        ('DELETE', 'Eliminación'),
        ('VIEW', 'Visualización'),
        ('LOGIN', 'Inicio de Sesión'),
        ('LOGOUT', 'Cierre de Sesión'),
        ('PRESTAMO', 'Préstamo'),
        ('DEVOLUCION', 'Devolución'),
    )

    usuario = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True, related_name='actividades')
    accion = models.CharField(max_length=20, choices=ACCIONES)
    modelo = models.CharField(max_length=100, blank=True)
    objeto_id = models.IntegerField(null=True, blank=True)
    descripcion = models.TextField()
    fecha = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)

    class Meta:
        ordering = ['-fecha']
        verbose_name = 'Log de Actividad'
        verbose_name_plural = 'Logs de Actividad'

    def __str__(self):
        return f"{self.usuario} - {self.get_accion_display()} - {self.fecha}"
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Sum, Count
from .models import (
    Bodega, Material, Herramienta, MaterialBodega, 
    HerramientaBodega, TipoBodega
)

# ============= DASHBOARD DE INVENTARIO =============

@login_required
def inventario_dashboard(request):
    """Dashboard principal del sistema de inventario"""
    
    # Obtener bodega central
    bodega_central = Bodega.objects.filter(
        nombre_bodega__icontains='central'
    ).first()
    
    # Bodegas regionales ordenadas de norte a sur
    bodegas_regionales = Bodega.objects.exclude(
        codigo_bodega=bodega_central.codigo_bodega if bodega_central else None
    ).order_by('nombre_bodega')
    
    # Estadísticas generales
    total_materiales = Material.objects.count()
    total_herramientas = Herramienta.objects.count()
    total_bodegas = Bodega.objects.count()
    
    # Stock total por tipo
    stock_materiales = MaterialBodega.objects.aggregate(
        total=Sum('cantidad_almacenada')
    )['total'] or 0
    
    stock_herramientas = HerramientaBodega.objects.aggregate(
        total=Sum('cantidad_almacenada')
    )['total'] or 0
    
    # Alertas de stock bajo (menos de 10 unidades)
    materiales_bajo_stock = MaterialBodega.objects.filter(
        cantidad_almacenada__lt=10
    ).select_related('codigo_material', 'codigo_bodega')[:5]
    
    context = {
        'bodega_central': bodega_central,
        'bodegas_regionales': bodegas_regionales,
        'total_materiales': total_materiales,
        'total_herramientas': total_herramientas,
        'total_bodegas': total_bodegas,
        'stock_materiales': stock_materiales,
        'stock_herramientas': stock_herramientas,
        'materiales_bajo_stock': materiales_bajo_stock,
    }
    
    return render(request, 'inventario/dashboard.html', context)


# ============= VISTA DE BODEGA ESPECÍFICA =============

@login_required
def bodega_detalle(request, codigo_bodega):
    """Detalle de inventario de una bodega específica"""
    
    bodega = get_object_or_404(Bodega, codigo_bodega=codigo_bodega)
    
    # Materiales en esta bodega
    materiales = MaterialBodega.objects.filter(
        codigo_bodega=bodega
    ).select_related('codigo_material', 'codigo_material__codigo_tipo', 
                     'codigo_material__codigo_marca')
    
    # Herramientas en esta bodega
    herramientas = HerramientaBodega.objects.filter(
        codigo_bodega=bodega
    ).select_related('codigo_herramienta', 'codigo_herramienta__codigo_tipo',
                     'codigo_herramienta__codigo_categoria')
    
    # Estadísticas de la bodega
    total_materiales = materiales.count()
    total_herramientas = herramientas.count()
    
    context = {
        'bodega': bodega,
        'materiales': materiales,
        'herramientas': herramientas,
        'total_materiales': total_materiales,
        'total_herramientas': total_herramientas,
    }
    
    return render(request, 'inventario/bodega_detalle.html', context)


# ============= TRANSFERENCIA ENTRE BODEGAS =============

@login_required
def transferir_material(request):
    """Transferir materiales entre bodegas"""
    
    if request.method == 'POST':
        bodega_origen_id = request.POST.get('bodega_origen')
        bodega_destino_id = request.POST.get('bodega_destino')
        material_id = request.POST.get('material')
        cantidad = float(request.POST.get('cantidad', 0))
        
        try:
            # Obtener registros
            material_origen = MaterialBodega.objects.get(
                codigo_bodega_id=bodega_origen_id,
                codigo_material_id=material_id
            )
            
            # Verificar stock suficiente
            if material_origen.cantidad_almacenada < cantidad:
                messages.error(request, 'Stock insuficiente en bodega de origen')
                return redirect('transferir_material')
            
            # Reducir en origen
            material_origen.cantidad_almacenada -= cantidad
            material_origen.save()
            
            # Aumentar en destino (o crear si no existe)
            material_destino, created = MaterialBodega.objects.get_or_create(
                codigo_bodega_id=bodega_destino_id,
                codigo_material_id=material_id,
                defaults={'cantidad_almacenada': 0}
            )
            material_destino.cantidad_almacenada += cantidad
            material_destino.save()
            
            messages.success(
                request, 
                f'Transferencia exitosa: {cantidad} unidades de {material_origen.codigo_material.nombre_material}'
            )
            return redirect('inventario_dashboard')
            
        except MaterialBodega.DoesNotExist:
            messages.error(request, 'Material no encontrado en bodega de origen')
        except Exception as e:
            messages.error(request, f'Error en la transferencia: {str(e)}')
    
    # GET request
    bodegas = Bodega.objects.all()
    materiales = Material.objects.all()
    
    context = {
        'bodegas': bodegas,
        'materiales': materiales,
    }
    
    return render(request, 'inventario/transferir_material.html', context)


# ============= AJUSTE DE INVENTARIO =============

@login_required
def ajustar_inventario(request, codigo_bodega):
    """Ajustar cantidades de inventario (agregar/quitar stock)"""
    
    bodega = get_object_or_404(Bodega, codigo_bodega=codigo_bodega)
    
    if request.method == 'POST':
        material_id = request.POST.get('material')
        cantidad = float(request.POST.get('cantidad', 0))
        tipo_ajuste = request.POST.get('tipo_ajuste')  # 'agregar' o 'quitar'
        motivo = request.POST.get('motivo', '')
        
        try:
            material_bodega, created = MaterialBodega.objects.get_or_create(
                codigo_bodega=bodega,
                codigo_material_id=material_id,
                defaults={'cantidad_almacenada': 0}
            )
            
            if tipo_ajuste == 'agregar':
                material_bodega.cantidad_almacenada += cantidad
                messages.success(
                    request, 
                    f'Se agregaron {cantidad} unidades. Motivo: {motivo}'
                )
            elif tipo_ajuste == 'quitar':
                if material_bodega.cantidad_almacenada >= cantidad:
                    material_bodega.cantidad_almacenada -= cantidad
                    messages.success(
                        request, 
                        f'Se quitaron {cantidad} unidades. Motivo: {motivo}'
                    )
                else:
                    messages.error(request, 'Stock insuficiente para quitar esa cantidad')
                    return redirect('ajustar_inventario', codigo_bodega=codigo_bodega)
            
            material_bodega.save()
            return redirect('bodega_detalle', codigo_bodega=codigo_bodega)
            
        except Exception as e:
            messages.error(request, f'Error al ajustar inventario: {str(e)}')
    
    # GET request
    materiales = Material.objects.all()
    
    context = {
        'bodega': bodega,
        'materiales': materiales,
    }
    
    return render(request, 'inventario/ajustar_inventario.html', context)
 

# ============= REPORTE DE INVENTARIO =============

@login_required
def reporte_inventario(request):
    """Reporte completo de inventario por bodega"""
    
    # Filtros
    buscar = request.GET.get('buscar', '')
    bodega_id = request.GET.get('bodega', '')
    
    # Query base
    inventario = MaterialBodega.objects.select_related(
        'codigo_material', 'codigo_bodega'
    )
    
    # Aplicar filtros
    if buscar:
        inventario = inventario.filter(
            Q(codigo_material__nombre_material__icontains=buscar) |
            Q(codigo_bodega__nombre_bodega__icontains=buscar)
        )
    
    if bodega_id:
        inventario = inventario.filter(codigo_bodega_id=bodega_id)
    
    # Estadísticas
    total_items = inventario.count()
    valor_total = inventario.aggregate(total=Sum('cantidad_almacenada'))['total'] or 0
    
    bodegas = Bodega.objects.all()
    
    context = {
        'inventario': inventario,
        'bodegas': bodegas,
        'total_items': total_items,
        'valor_total': valor_total,
        'buscar': buscar,
        'bodega_seleccionada': bodega_id,
    }
    
    return render(request, 'inventario/reporte.html', context)