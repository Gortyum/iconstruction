from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone

# ======== PRIMERO: MODELO DE USUARIO ========

class Usuario(AbstractUser):
    """
    Modelo de usuario personalizado con roles
    DEBE IR PRIMERO ANTES DE CUALQUIER OTRO MODELO
    """
    ROLES = (
        ('ADMIN', 'Administrador'),
        ('BODEGUERO', 'Bodeguero'),
    )
    
    rol = models.CharField(max_length=20, choices=ROLES, default='BODEGUERO')
    telefono = models.CharField(max_length=15, blank=True)
    rut = models.CharField(max_length=12, unique=True, null=True, blank=True)
    fecha_contratacion = models.DateField(null=True, blank=True)
    activo = models.BooleanField(default=True)
    
    # NO incluir relación con Bodeguero aquí para evitar circular import
    
    class Meta:
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'
    
    def __str__(self):
        return f"{self.get_full_name()} ({self.get_rol_display()})"
    
    def is_admin(self):
        return self.rol == 'ADMIN'
    
    def is_bodeguero(self):
        return self.rol == 'BODEGUERO'
    
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
            }
        elif self.is_bodeguero():
            return {
                'materiales': ['view', 'add', 'change', 'delete'],
                'herramientas': ['view', 'add', 'change', 'delete'],
                'prestamos': ['view', 'add', 'change', 'delete'],
                'bodegas': ['view'],
                'obreros': ['view'],
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
    fecha_informe = models.DateField()
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


class Material(models.Model):
    codigo_material = models.AutoField(primary_key=True)
    nombre_material = models.CharField(max_length=200)
    precio_material = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    codigo_tipo = models.ForeignKey(TipoMaterial, on_delete=models.SET_NULL, null=True, related_name="materiales")
    codigo_marca = models.ForeignKey(MarcaMaterial, on_delete=models.SET_NULL, null=True, related_name="materiales")

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
    precio_herramienta = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    dimensiones = models.CharField(max_length=200, blank=True)
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
    merma = models.DecimalField(max_digits=12, decimal_places=2, default=0, 
                                help_text="Cantidad que sobró pero no se puede reutilizar")
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