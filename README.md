# Kiddo Spark · Prototipo funcional académico

Plataforma de demostración para una tesis de Ingeniería Comercial: conecta
familias, actividades extracurriculares, academias, empresas/colegios y aliados
de apoyo en la Región de Valparaíso. Conserva colores, logo y lenguaje visual
de la propuesta original.

**No opera un negocio real.** Planes, Sparks, campañas, montos y retiros son
simulados. Cuentas, reservas, solicitudes y cambios sí se guardan en una base
local. Usa datos ficticios, nunca información real de menores ni cuentas bancarias.

## Qué necesitas

- Un computador Windows con Python 3.15 y el comando `python` disponible.
- Visual Studio Code para abrir el proyecto y, opcionalmente, compartirlo.
- Internet durante la instalación inicial de paquetes.

Verificado con Python 3.15.2 y Django 6.1.3. SQLite guarda los datos en un archivo;
no necesitas instalar un servidor de base de datos. La aplicación usa recursos
visuales locales; la referencia HTML antigua todavía descarga Tailwind de Internet.

## Primera instalación — una sola vez

1. Descarga el proyecto completo desde GitHub y descomprime el ZIP.
2. En VS Code elige **Archivo → Abrir carpeta** y abre donde está `manage.py`.
3. Selecciona **Terminal → Nueva terminal** y ejecuta los siguientes comandos,
   uno por uno, esperando a que cada uno termine:

```powershell
python --version
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe manage.py migrate
.\.venv\Scripts\python.exe manage.py seed_demo
.\.venv\Scripts\python.exe manage.py createsuperuser
```

- **Entorno virtual** (`.venv`): separa las herramientas de este proyecto de
  otros programas. Estos comandos no requieren activarlo.
- **Migraciones**: preparan y actualizan las tablas de la base de datos.
- `seed_demo`: carga actividades, planes y aliados del HTML y crea el grupo
  de permisos de administradores. Se puede repetir sin sobrescribir ediciones.
  Los horarios iniciales son fechas futuras ilustrativas; crea nuevos cuando expiren.
- `createsuperuser`: pide usuario, correo ficticio y una contraseña que elijas.
  La contraseña no muestra caracteres al escribir; es normal. No hay contraseñas
  predefinidas ni publicadas en el repositorio.

Si `python` no se encuentra, instala Python desde su sitio oficial o pide ayuda
al responsable informático. Conserva los mensajes de error si algo falla.
No es necesario cambiar la política de ejecución de PowerShell.

## Encender y apagar

En la terminal de VS Code, desde la carpeta del proyecto:

```powershell
.\.venv\Scripts\python.exe manage.py runserver 127.0.0.1:8000 --noreload
```

Abre **http://127.0.0.1:8000/**. Mantén la terminal abierta. Para apagar el servidor,
presiona **Ctrl+C** en esa terminal. Cerrar el navegador no lo apaga. Los registros
permanecen al reiniciar.

Como alternativa, `scripts/run-local.ps1` prepara tablas, catálogo y servidor.
Si tu equipo bloquea scripts, utiliza los comandos anteriores.

## Roles y permisos

| Rol | Qué puede hacer |
| --- | --- |
| Usuario común | Explorar, guardar favoritos, activar planes demo, reservar, cancelar, valorar experiencias completadas y seguir sus solicitudes. |
| Administrador | Gestionar módulos autorizados de sus organizaciones asignadas. No administra usuarios ni privilegios. |
| Superadministrador | Gestionar la plataforma, usuarios, permisos y aprobación/asignación de organizaciones. |

Para crear un administrador:

1. Ingresa como superadministrador y abre **Usuarios y permisos**.
2. Crea un usuario con correo ficticio y contraseña propia.
3. Edita ese usuario; marca **Activo** y **Estado de personal**, sin marcar
   **Estado de superusuario**.
4. Asigna el grupo **Administradores de organización** y guarda.
5. En **Organizaciones**, edita su centro y añade al usuario en **Administradores**.

El grupo concede módulos; la asignación limita registros. Para limitar módulos,
crea otro grupo con los permisos necesarios, sin asignar el grupo completo anterior.
Un administrador sin organización asignada no podrá gestionar centros ajenos.
Los convenios sin aliado destinatario los atiende el superadministrador.

El registro público siempre crea usuarios comunes. Registrar una academia no
concede privilegios: requiere aprobación y asignación del superadministrador.
Las contraseñas se guardan mediante hashes, no como texto legible.

## Recorrido sugerido de presentación

1. Crea una cuenta ficticia desde **Crear cuenta**.
2. En **Planes y Sparks**, activa un plan demo. Cada activación añade Sparks;
   repetirla añade otra recarga registrada. Una cuenta nueva empieza sin saldo.
   No hay cobro ni renovación mensual automática.
3. En **Explorar**, filtra, abre una actividad y reserva un horario.
4. Consulta **Reservas** y **Mis Sparks**. Se descuenta saldo y se añaden 50 puntos.
   Cancelar devuelve Sparks y revierte esos puntos una sola vez. Los puntos no
   tienen canje ni valor monetario.
5. Con un administrador del centro, valida asistencia. Con el usuario, deja
   una opinión. El centro puede responder desde **Reputación**.
6. Solicita un convenio en **Empresas y colegios**, o asesoría en **Aliados**.
   Consulta su historial en **Solicitudes**.
7. Con el administrador correspondiente, avanza el seguimiento: pendiente →
   en revisión → aprobada → completada. Puede rechazarse antes de aprobar.
8. Crea y edita actividades, horarios y campañas en **Mantenedores**.
   Desactivar conserva el historial; editar permite reactivar.
9. En **Finanzas demo**, consulta montos referenciales de experiencias completadas
   y solicita un retiro ficticio. El superadministrador puede completar la
   simulación o rechazarla para liberar saldo. No hay conexión bancaria.
10. Revisa **Mi panel**: filtros por fecha y estadísticas calculadas desde registros.

Los nombres de centros proceden del material original y no acreditan convenios
reales. Cupos y fechas son demostrativos. Los precios identificables se tomaron
del HTML; los restantes empiezan en cero y pueden editarse. No hay una comisión
acordada: la liquidación demo refleja el monto referencial completo.
Las campañas guardan actividad, nombre, presupuesto y estado; no contratan anuncios
ni generan impresiones, clics o ROAS inventados.

## Compartir temporalmente mediante VS Code

El **reenvío de puertos** crea una dirección de Internet que conduce al servidor
local. Este flujo está documentado, pero no se ha probado en esta entrega.

1. Con la aplicación encendida, abre la paleta de comandos y busca
   **Ports: Focus on Ports View**.
2. Selecciona **Forward a Port**, escribe `8000` e inicia sesión con GitHub si se pide.
3. Copia la dirección HTTPS generada, por ejemplo `https://tu-direccion.devtunnels.ms`.
4. Detén el servidor con **Ctrl+C** y configura la dirección exacta en PowerShell.
   Reemplaza ambos ejemplos por el dominio que VS Code te entregó:

```powershell
$env:DJANGO_ALLOWED_HOSTS = 'tu-direccion.devtunnels.ms'
$env:DJANGO_CSRF_TRUSTED_ORIGINS = 'https://tu-direccion.devtunnels.ms'
.\.venv\Scripts\python.exe manage.py runserver 127.0.0.1:8000 --noreload
```

5. Elige visibilidad privada si los evaluadores pueden autenticarse. Si eliges
   pública, quienes accedan al enlace podrán alcanzar la aplicación y su registro.
   Usa exclusivamente datos y contraseñas ficticias.
6. Prueba el enlace desde otro equipo, incluyendo login y envío de formularios.
7. Mantén encendidos computador, VS Code, servidor e Internet durante la demo.
8. Al terminar, detén el reenvío en **Ports** y apaga el servidor con **Ctrl+C**.

No uses `*` como dominio permitido. Si cambia el enlace, actualiza ambas variables.
Las variables afectan solo la terminal donde se configuraron. El servidor es de
desarrollo, no un alojamiento permanente.
[Guía oficial](https://code.visualstudio.com/docs/debugtest/port-forwarding).

## Problemas frecuentes

| Situación | Qué revisar |
| --- | --- |
| Puerto ocupado | Detén el otro servidor o usa `127.0.0.1:8001` y reenvía ese puerto. |
| Faltan tablas | Ejecuta `manage.py migrate` con el Python del entorno virtual. |
| Catálogo vacío | Ejecuta `manage.py seed_demo` y comprueba que los centros estén aprobados. |
| No hay horarios | Crea un horario futuro y habilitado. |
| No puedo reservar | Comprueba saldo, cupos y que no tengas ya una reserva confirmada allí. |
| Administrador sin registros | Comprueba grupo, estado de personal y organización asignada. |
| Error 400 al compartir | Configura el dominio exacto en `DJANGO_ALLOWED_HOSTS` y reinicia. |
| Error 403 en formularios | Configura el origen HTTPS en `DJANGO_CSRF_TRUSTED_ORIGINS` y recarga. |
| Contraseña olvidada | El superadministrador puede cambiarla desde usuarios; para su propia cuenta usa `manage.py changepassword nombre_usuario`. |

## Verificación técnica

```powershell
.\.venv\Scripts\python.exe manage.py test core
.\.venv\Scripts\python.exe manage.py check
.\.venv\Scripts\python.exe manage.py makemigrations --check --dry-run
.\.venv\Scripts\python.exe -m pip check
node --check static/portal.js
```

Las pruebas usan una base temporal, separada de la demo. La revisión visual de
escritorio/móvil queda pendiente porque el navegador de desarrollo no estuvo
disponible. Se incluyeron estilos adaptables, menú móvil y tablas desplazables.
El reenvío de VS Code tampoco se da por verificado.

`check --deploy` advierte de cuatro ajustes de HTTPS no activados para HTTP local:
HSTS, redirección HTTPS y cookies exclusivas de HTTPS para sesiones y CSRF.
No se afirma seguridad productiva: no hay despliegue, correo externo, recuperación
de contraseña por email ni pruebas de carga. SQLite es para una demo de baja concurrencia.

## Archivos y distribución

- `core/`: datos, reglas, formularios, permisos, pruebas y migraciones.
- `kiddo/`: configuración y rutas.
- `templates/`, `static/`, `assets/`: pantallas y recursos visuales.
- `var/kiddo.sqlite3`: datos locales, excluidos de GitHub.
- `docs/`: arquitectura y alcance; `CHANGELOG.md`: historial.
- `Kiddo Spark B2B2C.html`: referencia conservada. Puede abrirse junto con `assets/`
  o desde **Ver propuesta original** en el pie de página.

Reenvía una descarga de GitHub con el código, no un ZIP de la carpeta de trabajo.
No distribuyas `.venv`, bases de datos, sesiones, credenciales ni archivos privados
de asistencia al desarrollo. Cada computador prepara su entorno y base local.
Para respaldar una demo, apaga primero el servidor y guarda una copia privada de
`var/kiddo.sqlite3`. No la publiques ni la adjuntes a la entrega de código.
