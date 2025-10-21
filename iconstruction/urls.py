"""
URL configuration for iconstruction project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.urls import path
from appiconstruction.views import (
    MaterialListView,
    MaterialDetailView,
    MaterialCreateView,
    MaterialUpdateView,
    MaterialDeleteView,
    LoginView, 
    LogoutView, 
    RegistroView, 
    DashboardView,
    GestionUsuariosView, 
    activar_usuario, 
    desactivar_usuario,
    cambiar_rol_usuario,
     # Herramientas
    HerramientaListView, HerramientaDetailView, HerramientaCreateView,
    HerramientaUpdateView, HerramientaDeleteView,
    
    # Obreros
    ObreroListView, ObreroDetailView, ObreroCreateView,
    ObreroUpdateView, ObreroDeleteView,
    
    # Bodegas
    BodegaListView, BodegaDetailView, BodegaCreateView,
    BodegaUpdateView, BodegaDeleteView,
    
    # Bodegueros
    BodegueroListView, BodegueroDetailView, BodegueroCreateView,
    BodegueroUpdateView, BodegueroDeleteView,
    
    # Préstamos de Materiales
    PrestamoMaterialListView, PrestamoMaterialCreateView,
    PrestamoMaterialDetailView, DevolucionMaterialCreateView,
    
    # Préstamos de Herramientas
    PrestamoHerramientaListView, PrestamoHerramientaCreateView,
    PrestamoHerramientaDetailView, DevolucionHerramientaView,

     # Supervisor
    SupervisorDashboardView, InformeListView, InformeCreateView,
    InformeDetailView, InformeUpdateView, InformeDeleteView,
    
    # Reportes
    ReportesView, reporte_materiales, reporte_prestamos,
    reporte_obreros, reporte_mermas, reporte_general,
)


urlpatterns = [
    path('admin/', admin.site.urls),
    path('materiales/', MaterialListView.as_view(), name='material_list'),
    path('materiales/<int:pk>/', MaterialDetailView.as_view(), name='material_detail'),
    path('materiales/crear/', MaterialCreateView.as_view(), name='material_create'),
    path('materiales/<int:pk>/editar/', MaterialUpdateView.as_view(), name='material_update'),
    path('materiales/<int:pk>/eliminar/', MaterialDeleteView.as_view(), name='material_delete'),

    # ========== AUTENTICACIÓN ==========
    path('', LoginView.as_view(), name='login'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('registro/', RegistroView.as_view(), name='registro'),
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
    
    # ========== GESTIÓN DE USUARIOS (ADMIN) ==========
    path('usuarios/', GestionUsuariosView.as_view(), name='gestion_usuarios'),
    path('usuarios/<int:user_id>/activar/', activar_usuario, name='activar_usuario'),
    path('usuarios/<int:user_id>/desactivar/', desactivar_usuario, name='desactivar_usuario'),
    path('usuarios/<int:user_id>/cambiar-rol/', cambiar_rol_usuario, name='cambiar_rol_usuario'),


    # ========== MATERIALES ==========
    path('materiales/', MaterialListView.as_view(), name='material_list'),
    path('materiales/<int:pk>/', MaterialDetailView.as_view(), name='material_detail'),
    path('materiales/crear/', MaterialCreateView.as_view(), name='material_create'),
    path('materiales/<int:pk>/editar/', MaterialUpdateView.as_view(), name='material_update'),
    path('materiales/<int:pk>/eliminar/', MaterialDeleteView.as_view(), name='material_delete'),
    
    # ========== HERRAMIENTAS ==========
    path('herramientas/', HerramientaListView.as_view(), name='herramienta_list'),
    path('herramientas/<int:pk>/', HerramientaDetailView.as_view(), name='herramienta_detail'),
    path('herramientas/crear/', HerramientaCreateView.as_view(), name='herramienta_create'),
    path('herramientas/<int:pk>/editar/', HerramientaUpdateView.as_view(), name='herramienta_update'),
    path('herramientas/<int:pk>/eliminar/', HerramientaDeleteView.as_view(), name='herramienta_delete'),
    
    # ========== OBREROS ==========
    path('obreros/', ObreroListView.as_view(), name='obrero_list'),
    path('obreros/<int:pk>/', ObreroDetailView.as_view(), name='obrero_detail'),
    path('obreros/crear/', ObreroCreateView.as_view(), name='obrero_create'),
    path('obreros/<int:pk>/editar/', ObreroUpdateView.as_view(), name='obrero_update'),
    path('obreros/<int:pk>/eliminar/', ObreroDeleteView.as_view(), name='obrero_delete'),
    
    # ========== BODEGAS ==========
    path('bodegas/', BodegaListView.as_view(), name='bodega_list'),
    path('bodegas/<int:pk>/', BodegaDetailView.as_view(), name='bodega_detail'),
    path('bodegas/crear/', BodegaCreateView.as_view(), name='bodega_create'),
    path('bodegas/<int:pk>/editar/', BodegaUpdateView.as_view(), name='bodega_update'),
    path('bodegas/<int:pk>/eliminar/', BodegaDeleteView.as_view(), name='bodega_delete'),
    
    # ========== BODEGUEROS ==========
    path('bodegueros/', BodegueroListView.as_view(), name='bodeguero_list'),
    path('bodegueros/<int:pk>/', BodegueroDetailView.as_view(), name='bodeguero_detail'),
    path('bodegueros/crear/', BodegueroCreateView.as_view(), name='bodeguero_create'),
    path('bodegueros/<int:pk>/editar/', BodegueroUpdateView.as_view(), name='bodeguero_update'),
    path('bodegueros/<int:pk>/eliminar/', BodegueroDeleteView.as_view(), name='bodeguero_delete'),
    
    # ========== PRÉSTAMOS DE MATERIALES ==========
    path('prestamos-materiales/', PrestamoMaterialListView.as_view(), name='prestamo_material_list'),
    path('prestamos-materiales/crear/', PrestamoMaterialCreateView.as_view(), name='prestamo_material_create'),
    path('prestamos-materiales/<int:pk>/', PrestamoMaterialDetailView.as_view(), name='prestamo_material_detail'),
    path('prestamos-materiales/<int:prestamo_id>/devolver/', DevolucionMaterialCreateView.as_view(), name='devolucion_material_create'),
    
    # ========== PRÉSTAMOS DE HERRAMIENTAS ==========
    path('prestamos-herramientas/', PrestamoHerramientaListView.as_view(), name='prestamo_herramienta_list'),
    path('prestamos-herramientas/crear/', PrestamoHerramientaCreateView.as_view(), name='prestamo_herramienta_create'),
    path('prestamos-herramientas/<int:pk>/', PrestamoHerramientaDetailView.as_view(), name='prestamo_herramienta_detail'),
    path('prestamos-herramientas/<int:pk>/devolver/', DevolucionHerramientaView.as_view(), name='devolucion_herramienta_create'),

    # ========== SUPERVISOR ==========
    path('supervisor/dashboard/', SupervisorDashboardView.as_view(), name='supervisor_dashboard'),
    
    # ========== INFORMES ==========
    path('informes/', InformeListView.as_view(), name='informe_list'),
    path('informes/crear/', InformeCreateView.as_view(), name='informe_create'),
    path('informes/<int:pk>/', InformeDetailView.as_view(), name='informe_detail'),
    path('informes/<int:pk>/editar/', InformeUpdateView.as_view(), name='informe_update'),
    path('informes/<int:pk>/eliminar/', InformeDeleteView.as_view(), name='informe_delete'),
    
    # ========== REPORTES ==========
    path('reportes/', ReportesView.as_view(), name='reportes'),
    path('reportes/materiales/', reporte_materiales, name='reporte_materiales'),
    path('reportes/prestamos/', reporte_prestamos, name='reporte_prestamos'),
    path('reportes/obreros/', reporte_obreros, name='reporte_obreros'),
    path('reportes/mermas/', reporte_mermas, name='reporte_mermas'),
    path('reportes/general/', reporte_general, name='reporte_general'),
    
]
