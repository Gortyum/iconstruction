## Manual de Usuario — iConstruction

Última actualización: 25-10-2025

Este manual explica cómo usar la aplicación iConstruction desde la perspectiva de los dos roles principales: Administrador (ADMIN) y Bodeguero (BODEGUERO). Incluye instrucciones de instalación básicas, flujo de trabajo diario, tareas administrativas, solución de problemas y buenas prácticas.

---

## 1. Resumen de la aplicación

iConstruction es un sistema sencillo para gestionar bodegas, materiales, herramientas, obreros y préstamos. Está diseñado para equipos de obra y bodegas que necesitan controlar inventarios y préstamos.

Roles principales:
- ADMIN: gestión completa del sistema (usuarios, activaciones, configuraciones, logs, backups).
- BODEGUERO: gestión operativa de materiales, herramientas, préstamos y devoluciones.

---

## 2. Requisitos y preparación (breve)

Requisitos principales:
- Python 3.11+ (el proyecto se probó con 3.13 en este entorno)
- Virtualenv (recomendado)
- MariaDB / MySQL (base de datos), en este repo se configuró en puerto 3307
- Paquetes Python del proyecto instalados en `.venv`

Variables sensibles: el proyecto usa variables de entorno (ver `.env`). Asegúrate de configurar:
- DB_HOST, DB_USER, DB_PASSWORD, DB_NAME, DB_PORT
- SECRET_KEY (en producción no usar DEBUG=True)

Instalación rápida (PowerShell):

```powershell
# crear y activar virtualenv
python -m venv .venv
& .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt

# Crear .env según plantilla (o exportar variables)
# Ejecutar migraciones
& .\.venv\Scripts\python.exe manage.py migrate

# Crear usuario administrador (opcional)
& .\.venv\Scripts\python.exe manage.py createsuperuser

# Iniciar servidor de desarrollo
& .\.venv\Scripts\python.exe manage.py runserver
```

Nota: la ruta exacta a Python en Windows puede variar; usa la del entorno virtual del proyecto.

---

## 3. Acceso y navegación básica

- URL base del dev server: http://127.0.0.1:8000/
- Pantalla de login: `/login/` (o simplemente la root que redirija al login)
- Tras iniciar sesión se redirige al `dashboard` según rol.

Credenciales de ejemplo (si fueron creadas en un script):
- Admin: `admin` / `admin123` (si fue creado así)
- Bodeguero: `bodeguero1` / `bodeguero123`

---

## 4. Funciones para el Administrador (ADMIN)

El rol Admin tiene capacidades completas. Tareas comunes:

4.1. Gestión de usuarios
- Ver la lista de usuarios: `Gestion Usuarios`.
- Activar / desactivar cuentas: seleccionar un usuario y usar los botones correspondientes.
- Cambiar rol de un usuario (ADMIN ↔ BODEGUERO) desde la interfaz de Gestión de Usuarios.

4.2. Auditoría y logs
- El sistema registra sesiones y actividades en `LogActividad` y `SesionUsuario`.
- Consultar registros desde el Dashboard (actividades recientes) o desde las tablas correspondientes.

4.3. Gestión de maestros y catálogos
- Crear/editar/eliminar: `Bodegas`, `Materiales`, `Herramientas`, `Obreros`, `Bodegueros`.
- Notar que algunos modelos relativos a categorías/estados/ tipos fueron simplificados en esta versión (ej. `Herramienta` sin `codigo_tipo` si fue remodeleada).

4.4. Migraciones y mantenimiento
- Ejecutar migraciones cuando se actualice el código:

```powershell
& .\.venv\Scripts\python.exe manage.py makemigrations
& .\.venv\Scripts\python.exe manage.py migrate
```

4.5. Backups
- Hacer dump de la base de datos regularmente con `mysqldump` o herramientas equivalentes.

---

## 5. Funciones para el Bodeguero (BODEGUERO)

El bodeguero se encarga de las operaciones diarias de inventario y préstamos.

5.1. Materiales
- Crear nuevo material: `Materiales → Nuevo`.
- Nota: en esta versión el formulario de creación puede haber sido simplificado (los campos `codigo_tipo` y `codigo_marca` pueden estar ausentes). Si la interfaz exige un tipo/marca y no hay catálogos, pedir al admin que los cree o ajustar el formulario.

5.2. Herramientas
- Crear, editar y eliminar herramientas.
- Registrar stock y dimensiones.

5.3. Bodegas
- Agregar bodegas, editar información y ver detalle.

5.4. Prestamos y Devoluciones
- Registrar préstamos (materiales o herramientas) desde las vistas de `Préstamos`.
- Registrar devoluciones: usar la vista de devolución asociada al préstamo.
- Validaciones: para materiales, la suma (devuelto + merma) no debe exceder la cantidad prestada.

5.5. Flujo típico de préstamo
1. Buscar/seleccionar obrero
2. Elegir material/herramienta y cantidad / fecha esperada
3. Guardar el préstamo
4. Registrar la devolución cuando corresponda

---

## 6. Guía paso a paso: crear Material (si se elimina tipo/marca)

1. Ir a `Materiales → Nuevo`.
2. Rellenar `Nombre del Material` y `Precio`.
3. Si el formulario no solicita `Tipo` ni `Marca`, esos atributos están deshabilitados — el material se crea con los datos mínimos.
4. Guardar. Si aparece un error de validación indicando que `codigo_tipo` o `codigo_marca` son requeridos, contactar al administrador para:
   - Crear entradas en `TipoMaterial` y `MarcaMaterial`.
   - O ajustar la vista para eliminar la validación.

---

## 7. Solución de problemas comunes

7.1. FieldError: Invalid field name(s) given in select_related
- Causa: la vista usa `select_related('codigo_x')` pero el campo fue eliminado del modelo.
- Solución: actualizar la vista para no llamar a `select_related` con campos inexistentes. Ejemplo: en `appiconstruction.views.HerramientaListView.get_queryset()` quitar esos nombres.

7.2. Error al ejecutar `manage.py` desde una carpeta incorrecta
- Asegúrate de ejecutar los comandos desde el directorio que contiene `manage.py` (en este repositorio: `iconstruction-main/iconstruction-main/manage.py`).

7.3. Errores de migraciones tras modificar modelos
- Ejecuta:

```powershell
& .\.venv\Scripts\python.exe manage.py makemigrations
& .\.venv\Scripts\python.exe manage.py migrate
```

- Si hay modelos que cambiaron de forma incompatible con la base de datos, revisa los archivos en `appiconstruction/migrations/` y asegúrate de que el historial corresponde a los cambios realizados.

7.4. Campos de formulario marcados como "This field is required."
- Puede indicar que el formulario espera un `ForeignKey` que fue eliminado del modelo o no tiene datos (catálogo vacío). Para arreglar:
  - Crear entradas en el catálogo (ej. `TipoMaterial`) o
  - Ajustar la vista/templates para no mostrar el campo cuando no exista.

---

## 8. Buenas prácticas operativas
- Mantén copias periódicas de la base de datos.
- Antes de aplicar migraciones en producción, hacer un backup y probar en staging.
- Mantén `DEBUG=False` en producción y configura `ALLOWED_HOSTS`.
- Revisa el `LogActividad` para auditoría de acciones importantes.

---

## 9. Extender o personalizar
- Para añadir campos o relaciones: modificar `appiconstruction/models.py`, crear migraciones y migrar.
- Para modificar formularios presentados en UI: editar las vistas en `appiconstruction/views.py` y las plantillas en `appiconstruction/templates/`.

---

## 10. Referencias técnicas rápidas
- Proyecto Django root del código: `iconstruction-main/iconstruction-main/`
- Aplicación principal: `appiconstruction`
- Entradas relevantes:
  - Modelos: `appiconstruction/models.py`
  - Vistas: `appiconstruction/views.py`
  - Templates: `appiconstruction/templates/`
  - Migrations: `appiconstruction/migrations/`

---

## 11. Contacto / Responsables
- Añade aquí los responsables del proyecto: nombre, email y teléfono del administrador del sistema.

---

## 12. FAQ rápida
Q: ¿Puedo eliminar un campo del modelo directamente? A: Sí, pero recuerda crear y aplicar migraciones. Revisa las vistas y templates que referencien dicho campo.

Q: No veo el botón para crear X. ¿Por qué? A: Verifica permisos de usuario (rol) y que el template actual no esté ocultando la funcionalidad.

---

Si quieres, puedo:
- Añadir capturas de pantalla para secciones concretas (si las proporcionas)
- Traducir el manual al inglés
- Generar una versión en PDF
- Añadir un archivo `docs/QUICK_START.md` con solo los pasos mínimos

