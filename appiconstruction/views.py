from django.db.models import Q
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import TemplateView
from django.utils import timezone
from .models import Usuario, SesionUsuario, LogActividad
from django.contrib.auth.forms import UserCreationForm
from django import forms
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib import messages
from .models import (
    # Materiales
    Material, TipoMaterial, MarcaMaterial,
    # Herramientas
    Herramienta, TipoHerramienta, CategoriaHerramienta, MarcaHerramienta, EstadoHerramienta,
    # Obreros
    Obrero, Cargo, Obra,
    # Bodegas
    Bodega, TipoBodega, Bodeguero,
    # Préstamos
    PrestamoMaterial, DevolucionMaterial, PrestamoHerramienta
)

# ========================================
# MATERIALES
# ========================================

class MaterialListView(ListView):
    model = Material
    template_name = 'materiales/material_list.html'
    context_object_name = 'materiales'
    paginate_by = 10
    
    def get_queryset(self):
        queryset = Material.objects.select_related('codigo_tipo', 'codigo_marca').all()
        
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(nombre_material__icontains=search)
        
        tipo = self.request.GET.get('tipo')
        if tipo:
            queryset = queryset.filter(codigo_tipo_id=tipo)
        
        marca = self.request.GET.get('marca')
        if marca:
            queryset = queryset.filter(codigo_marca_id=marca)
        
        return queryset.order_by('nombre_material')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tipos'] = TipoMaterial.objects.all()
        context['marcas'] = MarcaMaterial.objects.all()
        context['search'] = self.request.GET.get('search', '')
        context['tipo_selected'] = self.request.GET.get('tipo', '')
        context['marca_selected'] = self.request.GET.get('marca', '')
        return context


class MaterialDetailView(DetailView):
    model = Material
    template_name = 'materiales/material_detail.html'
    context_object_name = 'material'
    pk_url_kwarg = 'pk'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['obras'] = self.object.obras_asignadas.select_related('codigo_obra').all()
        context['bodegas'] = self.object.bodegas.select_related('codigo_bodega').all()
        return context


class MaterialCreateView(CreateView):
    model = Material
    template_name = 'materiales/material_form.html'
    fields = ['nombre_material', 'precio_material', 'codigo_tipo', 'codigo_marca']
    success_url = reverse_lazy('material_list')
    
    def form_valid(self, form):
        messages.success(self.request, 'Material creado exitosamente.')
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Crear Material'
        context['button_text'] = 'Crear'
        return context


class MaterialUpdateView(UpdateView):
    model = Material
    template_name = 'materiales/material_form.html'
    fields = ['nombre_material', 'precio_material', 'codigo_tipo', 'codigo_marca']
    success_url = reverse_lazy('material_list')
    pk_url_kwarg = 'pk'
    
    def form_valid(self, form):
        messages.success(self.request, 'Material actualizado exitosamente.')
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Editar Material'
        context['button_text'] = 'Actualizar'
        return context


class MaterialDeleteView(DeleteView):
    model = Material
    template_name = 'materiales/material_confirm_delete.html'
    success_url = reverse_lazy('material_list')
    pk_url_kwarg = 'pk'
    context_object_name = 'material'
    
    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'Material eliminado exitosamente.')
        return super().delete(request, *args, **kwargs)


# ========================================
# HERRAMIENTAS
# ========================================

class HerramientaListView(ListView):
    model = Herramienta
    template_name = 'herramientas/herramienta_list.html'
    context_object_name = 'herramientas'
    paginate_by = 10
    
    def get_queryset(self):
        queryset = Herramienta.objects.select_related(
            'codigo_tipo', 'codigo_categoria', 'codigo_marca', 'codigo_estado'
        ).all()
        
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(nombre_herramienta__icontains=search)
        
        tipo = self.request.GET.get('tipo')
        if tipo:
            queryset = queryset.filter(codigo_tipo_id=tipo)
        
        categoria = self.request.GET.get('categoria')
        if categoria:
            queryset = queryset.filter(codigo_categoria_id=categoria)
        
        estado = self.request.GET.get('estado')
        if estado:
            queryset = queryset.filter(codigo_estado_id=estado)
        
        return queryset.order_by('nombre_herramienta')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tipos'] = TipoHerramienta.objects.all()
        context['categorias'] = CategoriaHerramienta.objects.all()
        context['estados'] = EstadoHerramienta.objects.all()
        context['search'] = self.request.GET.get('search', '')
        context['tipo_selected'] = self.request.GET.get('tipo', '')
        context['categoria_selected'] = self.request.GET.get('categoria', '')
        context['estado_selected'] = self.request.GET.get('estado', '')
        return context


class HerramientaDetailView(DetailView):
    model = Herramienta
    template_name = 'herramientas/herramienta_detail.html'
    context_object_name = 'herramienta'
    pk_url_kwarg = 'pk'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['bodegas'] = self.object.bodegas.select_related('codigo_bodega').all()
        context['obreros'] = self.object.obreros.select_related('id_obrero').all()
        return context


class HerramientaCreateView(CreateView):
    model = Herramienta
    template_name = 'herramientas/herramienta_form.html'
    fields = [
        'nombre_herramienta', 'precio_herramienta', 'dimensiones',
        'codigo_tipo', 'codigo_categoria', 'codigo_marca', 'codigo_estado'
    ]
    success_url = reverse_lazy('herramienta_list')
    
    def form_valid(self, form):
        messages.success(self.request, 'Herramienta creada exitosamente.')
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Crear Herramienta'
        context['button_text'] = 'Crear'
        return context


class HerramientaUpdateView(UpdateView):
    model = Herramienta
    template_name = 'herramientas/herramienta_form.html'
    fields = [
        'nombre_herramienta', 'precio_herramienta', 'dimensiones',
        'codigo_tipo', 'codigo_categoria', 'codigo_marca', 'codigo_estado'
    ]
    success_url = reverse_lazy('herramienta_list')
    pk_url_kwarg = 'pk'
    
    def form_valid(self, form):
        messages.success(self.request, 'Herramienta actualizada exitosamente.')
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Editar Herramienta'
        context['button_text'] = 'Actualizar'
        return context


class HerramientaDeleteView(DeleteView):
    model = Herramienta
    template_name = 'herramientas/herramienta_confirm_delete.html'
    success_url = reverse_lazy('herramienta_list')
    pk_url_kwarg = 'pk'
    context_object_name = 'herramienta'
    
    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'Herramienta eliminada exitosamente.')
        return super().delete(request, *args, **kwargs)


# ========================================
# OBREROS
# ========================================

class ObreroListView(ListView):
    model = Obrero
    template_name = 'obreros/obrero_list.html'
    context_object_name = 'obreros'
    paginate_by = 10
    
    def get_queryset(self):
        queryset = Obrero.objects.select_related('codigo_obra', 'codigo_cargo').all()
        
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(nombre_obrero__icontains=search) | Q(apellido_obrero__icontains=search)
            )
        
        cargo = self.request.GET.get('cargo')
        if cargo:
            queryset = queryset.filter(codigo_cargo_id=cargo)
        
        obra = self.request.GET.get('obra')
        if obra:
            queryset = queryset.filter(codigo_obra_id=obra)
        
        return queryset.order_by('apellido_obrero', 'nombre_obrero')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['cargos'] = Cargo.objects.all()
        context['obras'] = Obra.objects.all()
        context['search'] = self.request.GET.get('search', '')
        context['cargo_selected'] = self.request.GET.get('cargo', '')
        context['obra_selected'] = self.request.GET.get('obra', '')
        return context


class ObreroDetailView(DetailView):
    model = Obrero
    template_name = 'obreros/obrero_detail.html'
    context_object_name = 'obrero'
    pk_url_kwarg = 'pk'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['herramientas'] = self.object.herramientas.select_related('codigo_herramienta').all()
        context['prestamos_materiales'] = self.object.prestamos_materiales.select_related('codigo_material').all()[:10]
        context['prestamos_herramientas'] = self.object.prestamos_herramientas.select_related('codigo_herramienta').all()[:10]
        return context


class ObreroCreateView(CreateView):
    model = Obrero
    template_name = 'obreros/obrero_form.html'
    fields = ['nombre_obrero', 'apellido_obrero', 'codigo_obra', 'codigo_cargo']
    success_url = reverse_lazy('obrero_list')
    
    def form_valid(self, form):
        messages.success(self.request, 'Obrero creado exitosamente.')
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Crear Obrero'
        context['button_text'] = 'Crear'
        return context


class ObreroUpdateView(UpdateView):
    model = Obrero
    template_name = 'obreros/obrero_form.html'
    fields = ['nombre_obrero', 'apellido_obrero', 'codigo_obra', 'codigo_cargo']
    success_url = reverse_lazy('obrero_list')
    pk_url_kwarg = 'pk'
    
    def form_valid(self, form):
        messages.success(self.request, 'Obrero actualizado exitosamente.')
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Editar Obrero'
        context['button_text'] = 'Actualizar'
        return context


class ObreroDeleteView(DeleteView):
    model = Obrero
    template_name = 'obreros/obrero_confirm_delete.html'
    success_url = reverse_lazy('obrero_list')
    pk_url_kwarg = 'pk'
    context_object_name = 'obrero'
    
    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'Obrero eliminado exitosamente.')
        return super().delete(request, *args, **kwargs)


# ========================================
# BODEGAS
# ========================================

class BodegaListView(ListView):
    model = Bodega
    template_name = 'bodegas/bodega_list.html'
    context_object_name = 'bodegas'
    paginate_by = 10
    
    def get_queryset(self):
        queryset = Bodega.objects.select_related('codigo_tipo').all()
        
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(nombre_bodega__icontains=search)
        
        tipo = self.request.GET.get('tipo')
        if tipo:
            queryset = queryset.filter(codigo_tipo_id=tipo)
        
        return queryset.order_by('nombre_bodega')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tipos'] = TipoBodega.objects.all()
        context['search'] = self.request.GET.get('search', '')
        context['tipo_selected'] = self.request.GET.get('tipo', '')
        return context


class BodegaDetailView(DetailView):
    model = Bodega
    template_name = 'bodegas/bodega_detail.html'
    context_object_name = 'bodega'
    pk_url_kwarg = 'pk'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['materiales'] = self.object.materiales.select_related('codigo_material').all()
        context['herramientas'] = self.object.herramientas.select_related('codigo_herramienta').all()
        context['bodegueros'] = self.object.bodegueros.select_related('id_bodeguero').all()
        return context


class BodegaCreateView(CreateView):
    model = Bodega
    template_name = 'bodegas/bodega_form.html'
    fields = ['nombre_bodega', 'direccion_bodega', 'capacidad', 'codigo_tipo']
    success_url = reverse_lazy('bodega_list')
    
    def form_valid(self, form):
        messages.success(self.request, 'Bodega creada exitosamente.')
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Crear Bodega'
        context['button_text'] = 'Crear'
        return context


class BodegaUpdateView(UpdateView):
    model = Bodega
    template_name = 'bodegas/bodega_form.html'
    fields = ['nombre_bodega', 'direccion_bodega', 'capacidad', 'codigo_tipo']
    success_url = reverse_lazy('bodega_list')
    pk_url_kwarg = 'pk'
    
    def form_valid(self, form):
        messages.success(self.request, 'Bodega actualizada exitosamente.')
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Editar Bodega'
        context['button_text'] = 'Actualizar'
        return context


class BodegaDeleteView(DeleteView):
    model = Bodega
    template_name = 'bodegas/bodega_confirm_delete.html'
    success_url = reverse_lazy('bodega_list')
    pk_url_kwarg = 'pk'
    context_object_name = 'bodega'
    
    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'Bodega eliminada exitosamente.')
        return super().delete(request, *args, **kwargs)


# ========================================
# BODEGUEROS
# ========================================

class BodegueroListView(ListView):
    model = Bodeguero
    template_name = 'bodegueros/bodeguero_list.html'
    context_object_name = 'bodegueros'
    paginate_by = 10
    
    def get_queryset(self):
        queryset = Bodeguero.objects.all()
        
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(nombre_bodeguero__icontains=search) | Q(apellido_bodeguero__icontains=search)
            )
        
        return queryset.order_by('apellido_bodeguero', 'nombre_bodeguero')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search'] = self.request.GET.get('search', '')
        return context


class BodegueroDetailView(DetailView):
    model = Bodeguero
    template_name = 'bodegueros/bodeguero_detail.html'
    context_object_name = 'bodeguero'
    pk_url_kwarg = 'pk'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['bodegas'] = self.object.bodegas.select_related('codigo_bodega').all()
        return context


class BodegueroCreateView(CreateView):
    model = Bodeguero
    template_name = 'bodegueros/bodeguero_form.html'
    fields = ['nombre_bodeguero', 'apellido_bodeguero', 'sueldo']
    success_url = reverse_lazy('bodeguero_list')
    
    def form_valid(self, form):
        messages.success(self.request, 'Bodeguero creado exitosamente.')
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Crear Bodeguero'
        context['button_text'] = 'Crear'
        return context


class BodegueroUpdateView(UpdateView):
    model = Bodeguero
    template_name = 'bodegueros/bodeguero_form.html'
    fields = ['nombre_bodeguero', 'apellido_bodeguero', 'sueldo']
    success_url = reverse_lazy('bodeguero_list')
    pk_url_kwarg = 'pk'
    
    def form_valid(self, form):
        messages.success(self.request, 'Bodeguero actualizado exitosamente.')
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Editar Bodeguero'
        context['button_text'] = 'Actualizar'
        return context


class BodegueroDeleteView(DeleteView):
    model = Bodeguero
    template_name = 'bodegueros/bodeguero_confirm_delete.html'
    success_url = reverse_lazy('bodeguero_list')
    pk_url_kwarg = 'pk'
    context_object_name = 'bodeguero'
    
    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'Bodeguero eliminado exitosamente.')
        return super().delete(request, *args, **kwargs)


# ========================================
# PRÉSTAMOS DE MATERIALES
# ========================================

class PrestamoMaterialListView(ListView):
    model = PrestamoMaterial
    template_name = 'prestamos/prestamo_material_list.html'
    context_object_name = 'prestamos'
    paginate_by = 15
    
    def get_queryset(self):
        queryset = PrestamoMaterial.objects.select_related(
            'id_obrero', 'codigo_material'
        ).all()
        
        estado = self.request.GET.get('estado')
        if estado == 'pendiente':
            queryset = queryset.filter(devuelto=False)
        elif estado == 'devuelto':
            queryset = queryset.filter(devuelto=True)
        
        obrero = self.request.GET.get('obrero')
        if obrero:
            queryset = queryset.filter(id_obrero_id=obrero)
        
        return queryset.order_by('-fecha_prestamo')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['obreros'] = Obrero.objects.all()
        context['estado_selected'] = self.request.GET.get('estado', '')
        context['obrero_selected'] = self.request.GET.get('obrero', '')
        return context


class PrestamoMaterialCreateView(CreateView):
    model = PrestamoMaterial
    template_name = 'prestamos/prestamo_material_form.html'
    fields = [
        'id_obrero', 'codigo_material', 'cantidad_prestada',
        'fecha_devolucion_esperada', 'observaciones'
    ]
    success_url = reverse_lazy('prestamo_material_list')
    
    def form_valid(self, form):
        messages.success(self.request, 'Préstamo de material registrado exitosamente.')
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Registrar Préstamo de Material'
        context['button_text'] = 'Registrar Préstamo'
        return context


class PrestamoMaterialDetailView(DetailView):
    model = PrestamoMaterial
    template_name = 'prestamos/prestamo_material_detail.html'
    context_object_name = 'prestamo'
    pk_url_kwarg = 'pk'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['devoluciones'] = self.object.devoluciones.all()
        return context


class DevolucionMaterialCreateView(CreateView):
    model = DevolucionMaterial
    template_name = 'prestamos/devolucion_material_form.html'
    fields = ['cantidad_devuelta', 'merma', 'observaciones']
    
    def dispatch(self, request, *args, **kwargs):
        self.prestamo = get_object_or_404(PrestamoMaterial, pk=kwargs.get('prestamo_id'))
        if self.prestamo.devuelto:
            messages.warning(request, 'Este préstamo ya ha sido devuelto.')
            return redirect('prestamo_material_detail', pk=self.prestamo.codigo_prestamo)
        return super().dispatch(request, *args, **kwargs)
    
    def form_valid(self, form):
        form.instance.codigo_prestamo = self.prestamo
        
        # Validar cantidades
        total = form.instance.cantidad_devuelta + form.instance.merma
        if total > self.prestamo.cantidad_prestada:
            messages.error(
                self.request,
                'La suma de cantidad devuelta y merma no puede superar la cantidad prestada.'
            )
            return self.form_invalid(form)
        
        messages.success(self.request, 'Devolución registrada exitosamente.')
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('prestamo_material_detail', kwargs={'pk': self.prestamo.codigo_prestamo})
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['prestamo'] = self.prestamo
        context['title'] = 'Registrar Devolución de Material'
        context['button_text'] = 'Registrar Devolución'
        return context


# ========================================
# PRÉSTAMOS DE HERRAMIENTAS
# ========================================

class PrestamoHerramientaListView(ListView):
    model = PrestamoHerramienta
    template_name = 'prestamos/prestamo_herramienta_list.html'
    context_object_name = 'prestamos'
    paginate_by = 15
    
    def get_queryset(self):
        queryset = PrestamoHerramienta.objects.select_related(
            'id_obrero', 'codigo_herramienta'
        ).all()
        
        estado = self.request.GET.get('estado')
        if estado == 'pendiente':
            queryset = queryset.filter(devuelto=False)
        elif estado == 'devuelto':
            queryset = queryset.filter(devuelto=True)
        
        obrero = self.request.GET.get('obrero')
        if obrero:
            queryset = queryset.filter(id_obrero_id=obrero)
        
        return queryset.order_by('-fecha_prestamo')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['obreros'] = Obrero.objects.all()
        context['estado_selected'] = self.request.GET.get('estado', '')
        context['obrero_selected'] = self.request.GET.get('obrero', '')
        return context


class PrestamoHerramientaCreateView(CreateView):
    model = PrestamoHerramienta
    template_name = 'prestamos/prestamo_herramienta_form.html'
    fields = [
        'id_obrero', 'codigo_herramienta', 'fecha_devolucion_esperada',
        'estado_al_prestar', 'observaciones_prestamo'
    ]
    success_url = reverse_lazy('prestamo_herramienta_list')
    
    def form_valid(self, form):
        messages.success(self.request, 'Préstamo de herramienta registrado exitosamente.')
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Registrar Préstamo de Herramienta'
        context['button_text'] = 'Registrar Préstamo'
        return context


class PrestamoHerramientaDetailView(DetailView):
    model = PrestamoHerramienta
    template_name = 'prestamos/prestamo_herramienta_detail.html'
    context_object_name = 'prestamo'
    pk_url_kwarg = 'pk'


class DevolucionHerramientaView(UpdateView):
    model = PrestamoHerramienta
    template_name = 'prestamos/devolucion_herramienta_form.html'
    fields = ['estado_al_devolver', 'observaciones_devolucion']
    pk_url_kwarg = 'pk'
    
    def dispatch(self, request, *args, **kwargs):
        prestamo = self.get_object()
        if prestamo.devuelto:
            messages.warning(request, 'Esta herramienta ya ha sido devuelta.')
            return redirect('prestamo_herramienta_detail', pk=prestamo.codigo_prestamo)
        return super().dispatch(request, *args, **kwargs)
    
    def form_valid(self, form):
        from django.utils import timezone
        form.instance.fecha_devolucion_real = timezone.now()
        form.instance.devuelto = True
        messages.success(self.request, 'Devolución de herramienta registrada exitosamente.')
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('prestamo_herramienta_detail', kwargs={'pk': self.object.codigo_prestamo})
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['prestamo'] = self.object
        context['title'] = 'Registrar Devolución de Herramienta'
        context['button_text'] = 'Registrar Devolución'
        return context
    
# ======== FUNCIONES AUXILIARES ========

def es_admin(user):
    """Verifica si el usuario es administrador"""
    return user.is_authenticated and user.rol == 'ADMIN'

def es_bodeguero(user):
    """Verifica si el usuario es bodeguero"""
    return user.is_authenticated and user.rol == 'BODEGUERO'

def registrar_actividad(request, accion, modelo='', objeto_id=None, descripcion=''):
    """Registra una actividad en el log"""
    if request.user.is_authenticated:
        ip = request.META.get('REMOTE_ADDR')
        LogActividad.objects.create(
            usuario=request.user,
            accion=accion,
            modelo=modelo,
            objeto_id=objeto_id,
            descripcion=descripcion,
            ip_address=ip
        )

def get_client_ip(request):
    """Obtiene la IP del cliente"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


# ======== FORMULARIOS ========

class RegistroForm(UserCreationForm):
    """Formulario de registro de usuarios"""
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=True, label='Nombre')
    last_name = forms.CharField(max_length=30, required=True, label='Apellido')
    telefono = forms.CharField(max_length=15, required=False, label='Teléfono')
    rut = forms.CharField(max_length=12, required=False, label='RUT')
    
    class Meta:
        model = Usuario
        fields = ('username', 'email', 'first_name', 'last_name', 'telefono', 'rut', 'password1', 'password2')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
            if field_name == 'password1':
                field.help_text = 'Mínimo 8 caracteres. No puede ser muy similar a tu información personal.'
            elif field_name == 'password2':
                field.help_text = 'Ingresa la misma contraseña para verificación.'


class LoginForm(forms.Form):
    """Formulario de inicio de sesión"""
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Usuario'
        }),
        label='Usuario'
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Contraseña'
        }),
        label='Contraseña'
    )


# ======== VISTAS DE AUTENTICACIÓN ========

class LoginView(View):
    """Vista de inicio de sesión"""
    template_name = 'auth/login.html'
    
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('dashboard')
        form = LoginForm()
        return render(request, self.template_name, {'form': form})
    
    def post(self, request):
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            
            if user is not None:
                if user.activo:
                    login(request, user)
                    
                    # Registrar sesión
                    SesionUsuario.objects.create(
                        usuario=user,
                        ip_address=get_client_ip(request),
                        user_agent=request.META.get('HTTP_USER_AGENT', '')
                    )
                    
                    # Registrar actividad
                    registrar_actividad(
                        request,
                        'LOGIN',
                        descripcion=f'Inicio de sesión de {user.get_full_name()}'
                    )
                    
                    messages.success(request, f'¡Bienvenido {user.get_full_name()}!')
                    
                    # Redireccionar según el rol
                    next_url = request.GET.get('next', 'dashboard')
                    return redirect(next_url)
                else:
                    messages.error(request, 'Tu cuenta está inactiva. Contacta al administrador.')
            else:
                messages.error(request, 'Usuario o contraseña incorrectos.')
        
        return render(request, self.template_name, {'form': form})


class RegistroView(View):
    """Vista de registro de nuevos usuarios"""
    template_name = 'auth/registro.html'
    
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('dashboard')
        form = RegistroForm()
        return render(request, self.template_name, {'form': form})
    
    def post(self, request):
        form = RegistroForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.rol = 'BODEGUERO'  # Por defecto se registra como bodeguero
            user.activo = False  # Requiere activación por administrador
            user.save()
            
            messages.success(
                request,
                'Registro exitoso. Tu cuenta será activada por un administrador.'
            )
            return redirect('login')
        
        return render(request, self.template_name, {'form': form})


class LogoutView(View):
    """Vista de cierre de sesión"""
    
    def get(self, request):
        if request.user.is_authenticated:
            # Cerrar sesión activa
            sesion = SesionUsuario.objects.filter(
                usuario=request.user,
                fecha_fin__isnull=True
            ).first()
            if sesion:
                sesion.fecha_fin = timezone.now()
                sesion.save()
            
            # Registrar actividad
            registrar_actividad(
                request,
                'LOGOUT',
                descripcion=f'Cierre de sesión de {request.user.get_full_name()}'
            )
            
            logout(request)
            messages.info(request, 'Has cerrado sesión exitosamente.')
        
        return redirect('login')


# ======== DASHBOARD ========

class DashboardView(LoginRequiredMixin, TemplateView):
    """Dashboard principal según el rol del usuario"""
    template_name = 'dashboard/dashboard.html'
    login_url = 'login'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        if user.is_admin():
            # Estadísticas para administrador
            context['total_obreros'] = Obrero.objects.count()
            context['total_bodegas'] = Bodega.objects.count()
            context['total_bodegueros'] = Bodeguero.objects.count()
            context['obreros_recientes'] = Obrero.objects.order_by('-id_obrero')[:5]
            
        elif user.is_bodeguero():
            # Estadísticas para bodeguero
            context['total_materiales'] = Material.objects.count()
            context['total_herramientas'] = Herramienta.objects.count()
            context['prestamos_pendientes'] = PrestamoMaterial.objects.filter(devuelto=False).count()
            context['prestamos_herramientas_pendientes'] = PrestamoHerramienta.objects.filter(devuelto=False).count()
            context['materiales_recientes'] = Material.objects.order_by('-codigo_material')[:5]
            context['prestamos_recientes'] = PrestamoMaterial.objects.order_by('-fecha_prestamo')[:5]
        
        # Actividades recientes del usuario
        context['actividades_recientes'] = LogActividad.objects.filter(
            usuario=user
        ).order_by('-fecha')[:10]
        
        return context


# ======== GESTIÓN DE USUARIOS (SOLO ADMIN) ========

class GestionUsuariosView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    """Vista para gestión de usuarios (solo admin)"""
    template_name = 'auth/gestion_usuarios.html'
    login_url = 'login'
    
    def test_func(self):
        return self.request.user.is_admin()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['usuarios'] = Usuario.objects.all().order_by('-date_joined')
        context['usuarios_pendientes'] = Usuario.objects.filter(activo=False)
        return context


# ======== ACTIVAR/DESACTIVAR USUARIOS ========

@login_required
@user_passes_test(es_admin)
def activar_usuario(request, user_id):
    """Activa un usuario (solo admin)"""
    usuario = get_object_or_404(Usuario, id=user_id)
    usuario.activo = True
    usuario.save()
    
    registrar_actividad(
        request,
        'UPDATE',
        'Usuario',
        user_id,
        f'Usuario {usuario.username} activado'
    )
    
    messages.success(request, f'Usuario {usuario.get_full_name()} activado exitosamente.')
    return redirect('gestion_usuarios')


@login_required
@user_passes_test(es_admin)
def desactivar_usuario(request, user_id):
    """Desactiva un usuario (solo admin)"""
    usuario = get_object_or_404(Usuario, id=user_id)
    if usuario != request.user:
        usuario.activo = False
        usuario.save()
        
        registrar_actividad(
            request,
            'UPDATE',
            'Usuario',
            user_id,
            f'Usuario {usuario.username} desactivado'
        )
        
        messages.success(request, f'Usuario {usuario.get_full_name()} desactivado.')
    else:
        messages.error(request, 'No puedes desactivar tu propia cuenta.')
    
    return redirect('gestion_usuarios')


@login_required
@user_passes_test(es_admin)
def cambiar_rol_usuario(request, user_id):
    """Cambia el rol de un usuario (solo admin)"""
    usuario = get_object_or_404(Usuario, id=user_id)
    
    if request.method == 'POST':
        nuevo_rol = request.POST.get('rol')
        if nuevo_rol in ['ADMIN', 'BODEGUERO']:
            usuario.rol = nuevo_rol
            usuario.save()
            
            registrar_actividad(
                request,
                'UPDATE',
                'Usuario',
                user_id,
                f'Rol de {usuario.username} cambiado a {nuevo_rol}'
            )
            
            messages.success(request, f'Rol de {usuario.get_full_name()} actualizado.')
    
    return redirect('gestion_usuarios')


# ======== MODIFICAR MIXINS EXISTENTES ========
# Agregar esto a TODAS las vistas existentes que necesiten protección

class AdminRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Mixin que requiere que el usuario sea administrador"""
    login_url = 'login'
    
    def test_func(self):
        return self.request.user.is_admin()
    
    def handle_no_permission(self):
        messages.error(self.request, 'No tienes permisos para acceder a esta sección.')
        return redirect('dashboard')


class BodegueroRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Mixin que requiere que el usuario sea bodeguero"""
    login_url = 'login'
    
    def test_func(self):
        return self.request.user.is_bodeguero()
    
    def handle_no_permission(self):
        messages.error(self.request, 'No tienes permisos para acceder a esta sección.')
        return redirect('dashboard')