
# Proyecto - Ingeniería de Software

## Índice
- [Descripción](#descripción)
- [Screenshots](#screenshots)
- [Requisitos de instalación](#requisitos-de-instalación)
- [Configuración](#configuración)
- [Estructura del Proyecto](#estructura-del-proyecto)

## Descripción
Aplicación web desarrollada con Django para la gestión de reservas 
de salas en el departamento de ciencias de la computación de la universidad
de Chile. El sistema permite a los usuarios registrarse, iniciar 
sesión, actualizar su información personal, modificar sus reservas, 
consultar la disponibilidad de salas y realizar nuevas reservas. 
Además, los administradores tienen la capacidad de gestionar tanto 
las salas como las reservas. Este proyecto se llevó a 
cabo por un equipo de estudiantes como parte de un curso de 
ingeniería de software.

## Screenshots



## Requisitos de instalación

Para ejecutar la aplicación, se debe contar con python y las librerias indicadas en el archivo *requirements.txt*

## Configuración

1. Configurar la base de datos de la aplicación: 

```bash
python manage.py makemigrations
python manage.py migrate
```

2. (Opcional) Para tener datos de ejemplo, desde la carpeta *project_web_app/scripts* se puede correr: 

```bash
python populate_rooms.py
python populate_students.py
python populate_bookings.py
```

3. (Opcional) Crear un Superusuario siguiendo las instrucciones para acceder al panel de administración.

```bash
python manage.py createsuperuser
```
4.  Para ejecutar el servidor se debe invocar el siguiente comando desde la carpeta *project*:

```bash
python manage.py runserver
```

5. Entrar a la aplicación:
   
   - Aplicación: [http://127.0.0.1:8000](http://127.0.0.1:8000)
   - Panel de administración con tu superusuario: [http://127.0.0.1:8000/admin](http://127.0.0.1:8000/admin)

## Estructura del Proyecto

```bash
2024-2-CC4401-grupo-5/
├── project/                          # Código y configuración del proyecto
│   ├── project/                      # Configuración principal del proyecto Django
│   ├── project_web_app/              # Aplicación web principal
│   │   ├── __pycache__/              # Archivos cacheados
│   │   ├── migrations/               # Migraciones de la base de datos
│   │   ├── scripts/                  # Scripts de población
│   │   │   ├── populate_bookings.py  # Script para popular reservas
│   │   │   ├── populate_rooms.py     # Script para popular salas
│   │   │   └── populate_students.py  # Script para popular estudiantes
│   │   ├── static/                   # Archivos estáticos (CSS, JS, imágenes)
│   │   │   └── css/                  # Archivos CSS del proyecto
│   │   │       ├── input.css         # Archivo CSS de entrada
│   │   │       └── output.css        # Archivo CSS generado por Tailwind
│   │   ├── templates/                # Plantillas HTML
│   │   │   └── project_web_app/      # Plantillas específicas de la app
│   │   │       ├── base.html         # Plantilla base del proyecto
│   │   │       ├── login.html        # Página de login
│   │   │       ├── profile.html      # Página del perfil de usuario
│   │   │       ├── search-by-date.html       # Página de búsqueda por fecha
│   │   │       ├── search-room-by-name.html  # Página de búsqueda por nombre 
│   │   │       ├── signup.html               # Página de registro
│   │   │       ├── staff-add-room.html       # Página para agregar salas (staff)
│   │   │       ├── staff-edit-booking.html   # Página para editar reservas (staff)
│   │   │       ├── staff-edit-room.html      # Página para editar salas (staff)
│   │   │       ├── staff-room-list.html      # Listado de salas (staff)
│   │   │       └── staff-view-reservations.html # Ver reservas (staff)
│   │   ├── __init__.py               # Inicialización de la aplicación
│   │   ├── admin.py                  # Configuración del panel de administración
│   │   ├── apps.py                   # Configuración de la aplicación
│   │   ├── forms.py                  # Formularios de la aplicación
│   │   ├── models.py                 # Definición de los modelos (base de datos)
│   │   ├── tests.py                  # Pruebas unitarias
│   │   ├── urls.py                   # Rutas de la aplicación
│   │   └── views.py                  # Vistas de la aplicación
│   ├── db.sqlite3                    # Base de datos SQLite
│   └── manage.py                     # Script de gestión de Django
├── venv/                             # Entorno virtual de Python
├── .gitignore                        # Archivos ignorados por Git
├── README.md                         # Documentación del proyecto
└── requirements.txt                  # Dependencias del proyecto
```