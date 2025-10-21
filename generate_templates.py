"""
Script para generar automáticamente todos los templates del sistema
Ejecutar: python generate_templates.py
"""

import os

# Configuración de módulos
MODULES = {
    'herramienta': {
        'icon': 'tools',
        'title': 'Herramienta',
        'title_plural': 'Herramientas',
        'fields_display': ['nombre_herramienta', 'precio_herramienta', 'dimensiones'],
        'pk_field': 'codigo_herramienta'
    },
    'obrero': {
        'icon': 'people',
        'title': 'Obrero',
        'title_plural': 'Obreros',
        'fields_display': ['nombre_obrero', 'apellido_obrero'],
        'pk_field': 'id_obrero'
    },
    'bodega': {
        'icon': 'shop',
        'title': 'Bodega',
        'title_plural': 'Bodegas',
        'fields_display': ['nombre_bodega', 'direccion_bodega', 'capacidad'],
        'pk_field': 'codigo_bodega'
    },
    'bodeguero': {
        'icon': 'person-badge',
        'title': 'Bodeguero',
        'title_plural': 'Bodegueros',
        'fields_display': ['nombre_bodeguero', 'apellido_bodeguero', 'sueldo'],
        'pk_field': 'id_bodeguero'
    }
}

def create_list_template(module, config):
    return f"""{{% extends 'base.html' %}}

{{% block title %}}{config['title_plural']} - Sistema de Gestión{{% endblock %}}

{{% block content %}}
<div class="row mb-4">
    <div class="col">
        <h1 class="h2">
            <i class="bi bi-{config['icon']}"></i> Gestión de {config['title_plural']}
        </h1>
    </div>
    <div class="col-auto">
        <a href="{{% url '{module}_create' %}}" class="btn btn-primary">
            <i class="bi bi-plus-circle"></i> Nuevo {config['title']}
        </a>
    </div>
</div>

<div class="card">
    <div class="card-body">
        {{% if {module}s %}}
        <div class="table-responsive">
            <table class="table table-hover align-middle">
                <thead class="table-light">
                    <tr>
                        <th>ID</th>
                        <th>Información</th>
                        <th class="text-center">Acciones</th>
                    </tr>
                </thead>
                <tbody>
                    {{% for item in {module}s %}}
                    <tr>
                        <td><span class="badge bg-secondary">{{{{ item.{config['pk_field']} }}}}</span></td>
                        <td><strong>{{{{ item }}}}</strong></td>
                        <td class="text-center">
                            <div class="btn-group" role="group">
                                <a href="{{% url '{module}_detail' item.{config['pk_field']} %}}" class="btn btn-sm btn-outline-info">
                                    <i class="bi bi-eye"></i>
                                </a>
                                <a href="{{% url '{module}_update' item.{config['pk_field']} %}}" class="btn btn-sm btn-outline-warning">
                                    <i class="bi bi-pencil"></i>
                                </a>
                                <a href="{{% url '{module}_delete' item.{config['pk_field']} %}}" class="btn btn-sm btn-outline-danger">
                                    <i class="bi bi-trash"></i>
                                </a>
                            </div>
                        </td>
                    </tr>
                    {{% endfor %}}
                </tbody>
            </table>
        </div>
        {{% else %}}
        <div class="text-center py-5">
            <i class="bi bi-inbox" style="font-size: 4rem; color: #dee2e6;"></i>
            <p class="text-muted mt-3">No hay {config['title_plural'].lower()} registrados.</p>
            <a href="{{% url '{module}_create' %}}" class="btn btn-primary mt-2">
                <i class="bi bi-plus-circle"></i> Crear primero
            </a>
        </div>
        {{% endif %}}
    </div>
</div>
{{% endblock %}}
"""

def create_detail_template(module, config):
    return f"""{{% extends 'base.html' %}}

{{% block title %}}{{{{ {module} }}}} - Detalle{{% endblock %}}

{{% block content %}}
<div class="row mb-4">
    <div class="col">
        <nav aria-label="breadcrumb">
            <ol class="breadcrumb">
                <li class="breadcrumb-item">
                    <a href="{{% url '{module}_list' %}}">{config['title_plural']}</a>
                </li>
                <li class="breadcrumb-item active">{{{{ {module} }}}}</li>
            </ol>
        </nav>
    </div>
</div>

<div class="row">
    <div class="col-lg-8">
        <div class="card">
            <div class="card-header bg-primary text-white">
                <h5 class="mb-0">
                    <i class="bi bi-{config['icon']}"></i> Información del {config['title']}
                </h5>
            </div>
            <div class="card-body">
                <dl class="row">
                    <dt class="col-sm-4">ID:</dt>
                    <dd class="col-sm-8">
                        <span class="badge bg-secondary">{{{{ {module}.{config['pk_field']} }}}}</span>
                    </dd>
                </dl>
            </div>
        </div>
    </div>

    <div class="col-lg-4">
        <div class="card">
            <div class="card-header bg-secondary text-white">
                <h5 class="mb-0"><i class="bi bi-gear"></i> Acciones</h5>
            </div>
            <div class="card-body">
                <div class="d-grid gap-2">
                    <a href="{{% url '{module}_update' {module}.{config['pk_field']} %}}" class="btn btn-warning">
                        <i class="bi bi-pencil"></i> Editar
                    </a>
                    <a href="{{% url '{module}_delete' {module}.{config['pk_field']} %}}" class="btn btn-danger">
                        <i class="bi bi-trash"></i> Eliminar
                    </a>
                    <hr>
                    <a href="{{% url '{module}_list' %}}" class="btn btn-outline-secondary">
                        <i class="bi bi-arrow-left"></i> Volver
                    </a>
                </div>
            </div>
        </div>
    </div>
</div>
{{% endblock %}}
"""

def create_form_template(module, config):
    return f"""{{% extends 'base.html' %}}

{{% block title %}}{{{{ title }}}} - {config['title']}{{% endblock %}}

{{% block content %}}
<div class="row mb-4">
    <div class="col">
        <nav aria-label="breadcrumb">
            <ol class="breadcrumb">
                <li class="breadcrumb-item">
                    <a href="{{% url '{module}_list' %}}">{config['title_plural']}</a>
                </li>
                <li class="breadcrumb-item active">{{{{ title }}}}</li>
            </ol>
        </nav>
    </div>
</div>

<div class="row justify-content-center">
    <div class="col-lg-8">
        <div class="card shadow-sm">
            <div class="card-header bg-primary text-white">
                <h4 class="mb-0">
                    <i class="bi bi-{config['icon']}"></i> {{{{ title }}}}
                </h4>
            </div>
            <div class="card-body">
                <form method="post" novalidate>
                    {{% csrf_token %}}
                    {{{{ form.as_p }}}}
                    
                    <hr class="my-4">
                    
                    <div class="d-flex justify-content-between">
                        <a href="{{% url '{module}_list' %}}" class="btn btn-outline-secondary">
                            <i class="bi bi-x-circle"></i> Cancelar
                        </a>
                        <button type="submit" class="btn btn-primary">
                            <i class="bi bi-check-circle"></i> {{{{ button_text }}}}
                        </button>
                    </div>
                </form>
            </div>
        </div>
    </div>
</div>
{{% endblock %}}
"""

def create_delete_template(module, config):
    return f"""{{% extends 'base.html' %}}

{{% block title %}}Eliminar {config['title']} - {{{{ {module} }}}}{{% endblock %}}

{{% block content %}}
<div class="row justify-content-center">
    <div class="col-lg-8">
        <div class="alert alert-danger d-flex align-items-center" role="alert">
            <i class="bi bi-exclamation-triangle-fill me-3" style="font-size: 2rem;"></i>
            <div>
                <h5 class="alert-heading mb-1">¡Atención! Acción Irreversible</h5>
                <p class="mb-0">Está a punto de eliminar este {config['title'].lower()} permanentemente.</p>
            </div>
        </div>

        <div class="card shadow-sm">
            <div class="card-header bg-danger text-white">
                <h4 class="mb-0">
                    <i class="bi bi-trash"></i> Confirmar Eliminación
                </h4>
            </div>
            <div class="card-body">
                <h5 class="mb-4">¿Está seguro que desea eliminar el siguiente {config['title'].lower()}?</h5>
                
                <div class="bg-light p-4 rounded mb-4">
                    <p class="fs-5"><strong>{{{{ {module} }}}}</strong></p>
                </div>

                <form method="post">
                    {{% csrf_token %}}
                    
                    <div class="d-flex justify-content-between align-items-center pt-3">
                        <a href="{{% url '{module}_detail' {module}.{config['pk_field']} %}}" class="btn btn-outline-secondary btn-lg">
                            <i class="bi bi-arrow-left"></i> Cancelar
                        </a>
                        <button type="submit" class="btn btn-danger btn-lg">
                            <i class="bi bi-trash"></i> Sí, Eliminar
                        </button>
                    </div>
                </form>
            </div>
        </div>
    </div>
</div>
{{% endblock %}}
"""

def generate_all_templates():
    base_dir = 'templates'
    
    for module, config in MODULES.items():
        module_dir = os.path.join(base_dir, f'{module}s')
        os.makedirs(module_dir, exist_ok=True)
        
        # Generar templates
        templates = {
            f'{module}_list.html': create_list_template(module, config),
            f'{module}_detail.html': create_detail_template(module, config),
            f'{module}_form.html': create_form_template(module, config),
            f'{module}_confirm_delete.html': create_delete_template(module, config)
        }
        
        for filename, content in templates.items():
            filepath = os.path.join(module_dir, filename)
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f'✓ Creado: {filepath}')

if __name__ == '__main__':
    print('Generando templates...')
    generate_all_templates()
    print('\n¡Templates generados exitosamente!')




