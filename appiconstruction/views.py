from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django import forms
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
    PrestamoMaterial, DevolucionMaterial, PrestamoHerramienta, Informe
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
    
    def dispatch(self, request, *args, **kwargs):
        # Redireccionar supervisores a su dashboard específico
        if request.user.is_authenticated and request.user.is_supervisor():
            return redirect('supervisor_dashboard')
        return super().dispatch(request, *args, **kwargs)
    
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
        if nuevo_rol in ['ADMIN', 'BODEGUERO', 'SUPERVISOR']:
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
    
# AGREGAR ESTAS VISTAS AL ARCHIVO views.py

from django.http import HttpResponse, JsonResponse
from django.db.models import Count, Sum, Q, Avg
from django.utils import timezone
from datetime import datetime, timedelta
import csv


# ======== MIXINS PARA SUPERVISOR ========

class SupervisorRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Mixin que requiere que el usuario sea supervisor"""
    login_url = 'login'
    
    def test_func(self):
        return self.request.user.is_supervisor()
    
    def handle_no_permission(self):
        messages.error(self.request, 'No tienes permisos para acceder a esta sección.')
        return redirect('dashboard')


def es_supervisor(user):
    """Verifica si el usuario es supervisor"""
    return user.is_authenticated and user.rol == 'SUPERVISOR'


# ======== DASHBOARD SUPERVISOR ========

class SupervisorDashboardView(SupervisorRequiredMixin, TemplateView):
    """Dashboard para supervisores"""
    template_name = 'supervisor/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Estadísticas generales
        context['total_obras'] = Obra.objects.count()
        context['total_obreros'] = Obrero.objects.count()
        context['total_materiales'] = Material.objects.count()
        context['total_herramientas'] = Herramienta.objects.count()
        
        # Préstamos
        context['prestamos_materiales_activos'] = PrestamoMaterial.objects.filter(devuelto=False).count()
        context['prestamos_herramientas_activos'] = PrestamoHerramienta.objects.filter(devuelto=False).count()
        
        # Informes recientes del supervisor
        if self.request.user.supervisor:
            context['mis_informes'] = Informe.objects.filter(
                id_supervisor=self.request.user.supervisor
            ).order_by('-fecha_informe')[:5]
        
        return context


# ======== REPORTES ========

class ReportesView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    """Vista principal de reportes"""
    template_name = 'reportes/reportes.html'
    
    def test_func(self):
        return self.request.user.is_supervisor() or self.request.user.is_admin()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['puede_generar'] = True
        return context


# ======== REPORTE DE MATERIALES ========

@login_required
@user_passes_test(lambda u: u.is_supervisor() or u.is_admin())
def reporte_materiales(request):
    """Genera reporte de materiales"""
    formato = request.GET.get('formato', 'html')
    
    # Obtener datos
    materiales = Material.objects.select_related('codigo_tipo', 'codigo_marca').all()
    
    # Estadísticas
    total_materiales = materiales.count()
    valor_total = materiales.aggregate(Sum('precio_material'))['precio_material__sum'] or 0
    
    if formato == 'csv':
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="reporte_materiales.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['Código', 'Nombre', 'Tipo', 'Marca', 'Precio'])
        
        for material in materiales:
            writer.writerow([
                material.codigo_material,
                material.nombre_material,
                material.codigo_tipo.nombre_tipo if material.codigo_tipo else '',
                material.codigo_marca.nombre_marca if material.codigo_marca else '',
                material.precio_material
            ])
        
        return response
    
    # Formato HTML
    context = {
        'materiales': materiales,
        'total_materiales': total_materiales,
        'valor_total': valor_total,
        'fecha_generacion': timezone.now()
    }
    return render(request, 'reportes/reporte_materiales.html', context)


# ======== REPORTE DE PRÉSTAMOS ========

@login_required
@user_passes_test(lambda u: u.is_supervisor() or u.is_admin())
def reporte_prestamos(request):
    """Genera reporte de préstamos"""
    formato = request.GET.get('formato', 'html')
    fecha_inicio = request.GET.get('fecha_inicio')
    fecha_fin = request.GET.get('fecha_fin')
    estado = request.GET.get('estado', 'todos')
    
    # Filtrar préstamos
    prestamos = PrestamoMaterial.objects.select_related(
        'id_obrero', 'codigo_material'
    ).all()
    
    if fecha_inicio:
        prestamos = prestamos.filter(fecha_prestamo__gte=fecha_inicio)
    if fecha_fin:
        prestamos = prestamos.filter(fecha_prestamo__lte=fecha_fin)
    if estado == 'pendientes':
        prestamos = prestamos.filter(devuelto=False)
    elif estado == 'devueltos':
        prestamos = prestamos.filter(devuelto=True)
    
    # Estadísticas
    total_prestamos = prestamos.count()
    pendientes = prestamos.filter(devuelto=False).count()
    devueltos = prestamos.filter(devuelto=True).count()
    
    if formato == 'csv':
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="reporte_prestamos.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['Código', 'Obrero', 'Material', 'Cantidad', 'Fecha Préstamo', 'Estado'])
        
        for prestamo in prestamos:
            writer.writerow([
                prestamo.codigo_prestamo,
                str(prestamo.id_obrero),
                prestamo.codigo_material.nombre_material,
                prestamo.cantidad_prestada,
                prestamo.fecha_prestamo.strftime('%d/%m/%Y'),
                'Devuelto' if prestamo.devuelto else 'Pendiente'
            ])
        
        return response
    
    context = {
        'prestamos': prestamos,
        'total_prestamos': total_prestamos,
        'pendientes': pendientes,
        'devueltos': devueltos,
        'fecha_generacion': timezone.now(),
        'fecha_inicio': fecha_inicio,
        'fecha_fin': fecha_fin
    }
    return render(request, 'reportes/reporte_prestamos.html', context)


# ======== REPORTE DE OBREROS ========

@login_required
@user_passes_test(lambda u: u.is_supervisor() or u.is_admin())
def reporte_obreros(request):
    """Genera reporte de obreros"""
    formato = request.GET.get('formato', 'html')
    
    obreros = Obrero.objects.select_related('codigo_cargo', 'codigo_obra').all()
    
    # Estadísticas
    total_obreros = obreros.count()
    por_cargo = obreros.values('codigo_cargo__nombre_cargo').annotate(
        total=Count('id_obrero')
    )
    por_obra = obreros.values('codigo_obra__nombre_obra').annotate(
        total=Count('id_obrero')
    )
    
    if formato == 'csv':
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="reporte_obreros.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['ID', 'Nombre', 'Apellido', 'Cargo', 'Obra'])
        
        for obrero in obreros:
            writer.writerow([
                obrero.id_obrero,
                obrero.nombre_obrero,
                obrero.apellido_obrero,
                obrero.codigo_cargo.nombre_cargo if obrero.codigo_cargo else '',
                obrero.codigo_obra.nombre_obra if obrero.codigo_obra else ''
            ])
        
        return response
    
    context = {
        'obreros': obreros,
        'total_obreros': total_obreros,
        'por_cargo': por_cargo,
        'por_obra': por_obra,
        'fecha_generacion': timezone.now()
    }
    return render(request, 'reportes/reporte_obreros.html', context)


# ======== REPORTE DE MERMAS ========

@login_required
@user_passes_test(lambda u: u.is_supervisor() or u.is_admin())
def reporte_mermas(request):
    """Genera reporte de mermas en devoluciones"""
    formato = request.GET.get('formato', 'html')
    fecha_inicio = request.GET.get('fecha_inicio')
    fecha_fin = request.GET.get('fecha_fin')
    
    devoluciones = DevolucionMaterial.objects.select_related(
        'codigo_prestamo__codigo_material',
        'codigo_prestamo__id_obrero'
    ).filter(merma__gt=0)
    
    if fecha_inicio:
        devoluciones = devoluciones.filter(fecha_devolucion__gte=fecha_inicio)
    if fecha_fin:
        devoluciones = devoluciones.filter(fecha_devolucion__lte=fecha_fin)
    
    # Estadísticas
    total_merma = devoluciones.aggregate(Sum('merma'))['merma__sum'] or 0
    total_devoluciones = devoluciones.count()
    
    if formato == 'csv':
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="reporte_mermas.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['Código', 'Material', 'Obrero', 'Prestado', 'Devuelto', 'Merma', 'Fecha'])
        
        for dev in devoluciones:
            writer.writerow([
                dev.codigo_devolucion,
                dev.codigo_prestamo.codigo_material.nombre_material,
                str(dev.codigo_prestamo.id_obrero),
                dev.codigo_prestamo.cantidad_prestada,
                dev.cantidad_devuelta,
                dev.merma,
                dev.fecha_devolucion.strftime('%d/%m/%Y')
            ])
        
        return response
    
    context = {
        'devoluciones': devoluciones,
        'total_merma': total_merma,
        'total_devoluciones': total_devoluciones,
        'fecha_generacion': timezone.now(),
        'fecha_inicio': fecha_inicio,
        'fecha_fin': fecha_fin
    }
    return render(request, 'reportes/reporte_mermas.html', context)


# ======== REPORTE GENERAL/DASHBOARD ========

@login_required
@user_passes_test(lambda u: u.is_supervisor() or u.is_admin())
def reporte_general(request):
    """Genera reporte general del sistema"""
    
    # Estadísticas generales
    stats = {
        'obras': Obra.objects.count(),
        'obreros': Obrero.objects.count(),
        'materiales': Material.objects.count(),
        'herramientas': Herramienta.objects.count(),
        'bodegas': Bodega.objects.count(),
        'prestamos_materiales': PrestamoMaterial.objects.count(),
        'prestamos_herramientas': PrestamoHerramienta.objects.count(),
        'prestamos_pendientes': PrestamoMaterial.objects.filter(devuelto=False).count(),
        'valor_materiales': Material.objects.aggregate(Sum('precio_material'))['precio_material__sum'] or 0,
        'valor_herramientas': Herramienta.objects.aggregate(Sum('precio_herramienta'))['precio_herramienta__sum'] or 0,
    }
    
    # Préstamos recientes
    prestamos_recientes = PrestamoMaterial.objects.select_related(
        'id_obrero', 'codigo_material'
    ).order_by('-fecha_prestamo')[:10]
    
    # Devoluciones con merma
    mermas_recientes = DevolucionMaterial.objects.filter(
        merma__gt=0
    ).select_related(
        'codigo_prestamo__codigo_material'
    ).order_by('-fecha_devolucion')[:10]
    
    context = {
        'stats': stats,
        'prestamos_recientes': prestamos_recientes,
        'mermas_recientes': mermas_recientes,
        'fecha_generacion': timezone.now()
    }
    return render(request, 'reportes/reporte_general.html', context)


# ======== GESTIÓN DE INFORMES (SUPERVISOR) ========

class InformeListView(SupervisorRequiredMixin, ListView):
    model = Informe
    template_name = 'supervisor/informe_list.html'
    context_object_name = 'informes'
    paginate_by = 10
    
    def get_queryset(self):
        queryset = Informe.objects.select_related('id_supervisor').all()
        
        # Si es supervisor, solo ver sus propios informes
        if self.request.user.is_supervisor() and self.request.user.supervisor:
            queryset = queryset.filter(id_supervisor=self.request.user.supervisor)
        
        return queryset.order_by('-fecha_informe')


class InformeCreateView(SupervisorRequiredMixin, CreateView):
    model = Informe
    template_name = 'supervisor/informe_form.html'
    fields = ['titulo_informe',  'descripcion']
    success_url = reverse_lazy('informe_list')
    
    def form_valid(self, form):
        # Asignar el supervisor automáticamente
        if self.request.user.supervisor:
            form.instance.id_supervisor = self.request.user.supervisor
        else:
            messages.error(self.request, 'No tienes un perfil de supervisor asignado.')
            return self.form_invalid(form)
        
        messages.success(self.request, 'Informe creado exitosamente.')
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Crear Informe'
        context['button_text'] = 'Crear'
        return context


class InformeDetailView(SupervisorRequiredMixin, DetailView):
    model = Informe
    template_name = 'supervisor/informe_detail.html'
    context_object_name = 'informe'
    pk_url_kwarg = 'pk'


class InformeUpdateView(SupervisorRequiredMixin, UpdateView):
    model = Informe
    template_name = 'supervisor/informe_form.html'
    fields = ['titulo_informe', 'fecha_informe', 'descripcion']
    success_url = reverse_lazy('informe_list')
    pk_url_kwarg = 'pk'
    
    def form_valid(self, form):
        messages.success(self.request, 'Informe actualizado exitosamente.')
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Editar Informe'
        context['button_text'] = 'Actualizar'
        return context


class InformeDeleteView(SupervisorRequiredMixin, DeleteView):
    model = Informe
    template_name = 'supervisor/informe_confirm_delete.html'
    success_url = reverse_lazy('informe_list')
    pk_url_kwarg = 'pk'
    context_object_name = 'informe'
    
    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'Informe eliminado exitosamente.')
        return super().delete(request, *args, **kwargs)
    

# ======== FORMULARIOS ========

class CrearUsuarioForm(forms.ModelForm):
    """Formulario para que el admin cree usuarios"""
    password1 = forms.CharField(
        label='Contraseña',
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        help_text='Mínimo 8 caracteres'
    )
    password2 = forms.CharField(
        label='Confirmar Contraseña',
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        help_text='Ingrese la misma contraseña para verificación'
    )
    
    class Meta:
        model = Usuario
        fields = ['username', 'email', 'first_name', 'last_name', 'telefono', 'rut', 'rol', 'activo']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control'}),
            'rut': forms.TextInput(attrs={'class': 'form-control'}),
            'rol': forms.Select(attrs={'class': 'form-select'}),
            'activo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError('Las contraseñas no coinciden')
        if password1 and len(password1) < 8:
            raise forms.ValidationError('La contraseña debe tener al menos 8 caracteres')
        return password2
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password1'])
        if commit:
            user.save()
        return user


class EditarUsuarioForm(forms.ModelForm):
    """Formulario para que el admin edite usuarios (sin contraseña)"""
    
    class Meta:
        model = Usuario
        fields = ['username', 'email', 'first_name', 'last_name', 'telefono', 'rut', 'rol', 'activo']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control'}),
            'rut': forms.TextInput(attrs={'class': 'form-control'}),
            'rol': forms.Select(attrs={'class': 'form-select'}),
            'activo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class CambiarPasswordForm(forms.Form):
    """Formulario para que los usuarios cambien su propia contraseña"""
    password_actual = forms.CharField(
        label='Contraseña Actual',
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Contraseña actual'})
    )
    password_nueva = forms.CharField(
        label='Nueva Contraseña',
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Nueva contraseña'}),
        help_text='Mínimo 8 caracteres'
    )
    password_confirmacion = forms.CharField(
        label='Confirmar Nueva Contraseña',
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirmar contraseña'})
    )
    
    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)
    
    def clean_password_actual(self):
        password_actual = self.cleaned_data.get('password_actual')
        if not self.user.check_password(password_actual):
            raise forms.ValidationError('La contraseña actual es incorrecta')
        return password_actual
    
    def clean_password_confirmacion(self):
        password_nueva = self.cleaned_data.get('password_nueva')
        password_confirmacion = self.cleaned_data.get('password_confirmacion')
        
        if password_nueva and password_confirmacion:
            if password_nueva != password_confirmacion:
                raise forms.ValidationError('Las contraseñas no coinciden')
            if len(password_nueva) < 8:
                raise forms.ValidationError('La contraseña debe tener al menos 8 caracteres')
        
        return password_confirmacion
    
    def save(self):
        self.user.set_password(self.cleaned_data['password_nueva'])
        self.user.save()
        return self.user


# ======== VISTAS PARA ADMIN - CREAR USUARIO ========

class CrearUsuarioView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    """Vista para que el admin cree usuarios"""
    model = Usuario
    form_class = CrearUsuarioForm
    template_name = 'auth/crear_usuario.html'
    success_url = reverse_lazy('gestion_usuarios')
    
    def test_func(self):
        return self.request.user.is_admin()
    
    def handle_no_permission(self):
        messages.error(self.request, 'No tienes permisos para crear usuarios.')
        return redirect('dashboard')
    
    def form_valid(self, form):
        usuario = form.save()
        
        # Registrar actividad
        registrar_actividad(
            self.request,
            'CREATE',
            'Usuario',
            usuario.id,
            f'Usuario {usuario.username} creado por {self.request.user.username}'
        )
        
        messages.success(
            self.request,
            f'Usuario {usuario.get_full_name()} creado exitosamente con rol {usuario.get_rol_display()}'
        )
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Crear Nuevo Usuario'
        return context


class EditarUsuarioView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """Vista para que el admin edite usuarios"""
    model = Usuario
    form_class = EditarUsuarioForm
    template_name = 'auth/editar_usuario.html'
    success_url = reverse_lazy('gestion_usuarios')
    pk_url_kwarg = 'user_id'
    
    def test_func(self):
        return self.request.user.is_admin()
    
    def handle_no_permission(self):
        messages.error(self.request, 'No tienes permisos para editar usuarios.')
        return redirect('dashboard')
    
    def form_valid(self, form):
        usuario = form.save()
        
        # Registrar actividad
        registrar_actividad(
            self.request,
            'UPDATE',
            'Usuario',
            usuario.id,
            f'Usuario {usuario.username} actualizado por {self.request.user.username}'
        )
        
        messages.success(
            self.request,
            f'Usuario {usuario.get_full_name()} actualizado exitosamente'
        )
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Editar Usuario'
        context['usuario_editado'] = self.object
        return context


# ======== VISTAS PARA USUARIOS - CAMBIAR CONTRASEÑA ========

class CambiarPasswordView(LoginRequiredMixin, View):
    """Vista para que los usuarios cambien su propia contraseña"""
    template_name = 'auth/cambiar_password.html'
    
    def get(self, request):
        form = CambiarPasswordForm(user=request.user)
        return render(request, self.template_name, {'form': form})
    
    def post(self, request):
        form = CambiarPasswordForm(user=request.user, data=request.POST)
        
        if form.is_valid():
            form.save()
            
            # Mantener la sesión activa después del cambio de contraseña
            update_session_auth_hash(request, request.user)
            
            # Registrar actividad
            registrar_actividad(
                request,
                'UPDATE',
                'Usuario',
                request.user.id,
                f'Contraseña cambiada por {request.user.username}'
            )
            
            messages.success(request, 'Tu contraseña ha sido cambiada exitosamente.')
            return redirect('dashboard')
        
        return render(request, self.template_name, {'form': form})


# ======== ADMIN RESETEAR CONTRASEÑA DE USUARIO ========

@login_required
@user_passes_test(es_admin)
def resetear_password_usuario(request, user_id):
    """Permite al admin resetear la contraseña de un usuario"""
    usuario = get_object_or_404(Usuario, id=user_id)
    
    if request.method == 'POST':
        nueva_password = request.POST.get('nueva_password')
        confirmar_password = request.POST.get('confirmar_password')
        
        if nueva_password and confirmar_password:
            if nueva_password == confirmar_password:
                if len(nueva_password) >= 8:
                    usuario.set_password(nueva_password)
                    usuario.save()
                    
                    # Registrar actividad
                    registrar_actividad(
                        request,
                        'UPDATE',
                        'Usuario',
                        usuario.id,
                        f'Contraseña reseteada para {usuario.username} por {request.user.username}'
                    )
                    
                    messages.success(
                        request,
                        f'Contraseña de {usuario.get_full_name()} reseteada exitosamente.'
                    )
                    return redirect('gestion_usuarios')
                else:
                    messages.error(request, 'La contraseña debe tener al menos 8 caracteres.')
            else:
                messages.error(request, 'Las contraseñas no coinciden.')
        else:
            messages.error(request, 'Debe ingresar una contraseña.')
    
    context = {
        'usuario': usuario
    }
    return render(request, 'auth/resetear_password.html', context)


# ======== VISTA DE PERFIL DE USUARIO ========

class PerfilUsuarioView(LoginRequiredMixin, TemplateView):
    """Vista del perfil del usuario actual"""
    template_name = 'auth/perfil.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['usuario'] = self.request.user
        
        # Últimas actividades del usuario
        context['actividades_recientes'] = LogActividad.objects.filter(
            usuario=self.request.user
        ).order_by('-fecha')[:10]
        
        # Sesiones activas
        context['sesiones_recientes'] = SesionUsuario.objects.filter(
            usuario=self.request.user
        ).order_by('-fecha_inicio')[:5]
        
        return context