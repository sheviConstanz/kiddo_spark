# Kiddo Spark · Prototipo funcional académico

Plataforma de demostración para una tesis de Ingeniería Comercial: conecta
familias, actividades extracurriculares, academias, empresas/colegios y aliados
de apoyo en la Región de Valparaíso. Conserva colores, logo y lenguaje visual
de la propuesta original.

**No opera un negocio real.** Planes, Sparks, campañas, montos y retiros son
simulados. Cuentas, reservas, solicitudes y cambios sí se guardan en una base
local. Usa datos ficticios, nunca información real de menores ni cuentas bancarias.

## Antes de empezar en Windows

Necesitas un computador con **Windows**, **Python 3.14 o 3.15**, un navegador
y conexión a Internet para descargar el proyecto y preparar la primera
instalación. Puedes hacer la instalación y abrir la demo desde el
**Explorador de archivos**. No hace falta instalar Visual Studio Code, Git
ni un programa de base de datos.

**Comprueba si tienes Python.** Abre **Inicio → Configuración →
Aplicaciones → Aplicaciones instaladas** y busca **Python**. Si ves
**Python 3.14** o **Python 3.15**, Windows lo tiene instalado. Una entrada
que solo diga **Python Install Manager** es el instalador de Python. Revisa
si también aparece una versión de Python. En Windows 10, la lista puede
llamarse **Aplicaciones y características**.

Si quieres confirmar que el equipo reconoce Python, abre **Inicio**, busca
**Símbolo del sistema** y escribe `python --version`. Pulsa **Enter**.
Si ves, por ejemplo, `Python 3.14.7`, puedes continuar. Si Windows no
reconoce el comando, abre Microsoft Store en vez de mostrar una versión
o muestra una versión distinta, pide ayuda a TI o usa la
[descarga oficial de Python para Windows](https://www.python.org/downloads/windows/).
Si el instalador ofrece **Add Python to PATH**, marca esa opción para que
Windows encuentre Python. Cierra y vuelve a abrir la ventana antes de repetir
la comprobación.

## Descargar e instalar Kiddo Spark

1. Abre la [página de descarga de Kiddo Spark en GitHub](https://github.com/sheviConstanz/kiddo_spark).
   GitHub es el sitio donde están guardados los archivos del proyecto. En esa
   página, haz clic en **Code** (el botón verde) y luego en **Download ZIP**.
2. En **Descargas**, haz clic derecho sobre el archivo ZIP y selecciona
   **Extraer todo**. Abre la carpeta extraída hasta ver el archivo
   **instalar_local** o **instalar_local.ps1**. Ejecuta el archivo desde esa
   carpeta, fuera del ZIP.
3. Haz clic derecho en **instalar_local** o **instalar_local.ps1** y elige
   **Ejecutar con PowerShell**. En Windows 11, esa opción puede aparecer
   debajo de **Mostrar más opciones**.
4. Si el instalador pide permiso para descargar los componentes que faltan,
   responde **S** y pulsa **Enter**. El programa prepara la base y el catálogo.
   Si ofrece crear una cuenta de superadministración, puedes omitir ese paso
   para explorar o probar una reserva. Créala con datos ficticios si vas a
   probar la gestión de proveedores.

**Por qué a veces no ves `.ps1`.** Windows puede ocultar la parte final del
nombre del archivo. **instalar_local** e **instalar_local.ps1** son el mismo
archivo. Lo mismo pasa con **iniciar_local** y **compartir_local**. Si quieres
ver los nombres completos, activa **Ver → Mostrar → Extensiones de nombre
de archivo** en el Explorador de Windows 11.
[Ayuda de Microsoft sobre extensiones](https://support.microsoft.com/es-es/windows/experience/storage-filemanagement/common-file-name-extensions-in-windows).

Vuelve a instalar solo si instalas en otro equipo, falta el entorno o cambió
`requirements.txt`. Conserva la carpeta del proyecto y tus registros locales.

## Encender y apagar

1. Haz clic derecho en **iniciar_local** o **iniciar_local.ps1** y elige
   **Ejecutar con PowerShell**.
   Cuando indique que está listo, abre [Kiddo Spark local](http://127.0.0.1:8000/).
   Puedes cerrar la ventana de PowerShell después del aviso.
2. Para apagarlo, ejecuta el mismo archivo otra vez y confirma con **S**.

Si cambian el código, apaga y enciende la demo. Al iniciar, el script aplica
las actualizaciones de la base que vengan con el código. Si solo cambian
estilos o imágenes, puede bastar con recargar el navegador con **Ctrl+F5**.
Para presentar la demo, comparte la pantalla o usa un proyector.

## Si Windows bloquea un archivo

Si aparece un aviso de **Control inteligente de aplicaciones** en Windows 11
que dice que el archivo podría no ser seguro, detente. Guarda una captura o
copia el mensaje completo y envíalo a TI junto con el nombre del archivo y el
enlace de descarga. Pide una versión firmada y aprobada para el equipo, o
usa un computador autorizado para la demo. Mantén activada la protección.
Microsoft indica que este control puede bloquear archivos en los que no puede
confiar y que no permite excepciones por archivo.
[Ayuda de Microsoft sobre Control inteligente de aplicaciones](https://support.microsoft.com/en-gb/windows/security/threat-malware-protection/smart-app-control-frequently-asked-questions).

Si el mensaje dice que **la ejecución de scripts está deshabilitada**,
comunícalo a TI tal como aparece. Ese aviso se refiere a la política de
PowerShell. Si tienen una reunión antes de resolverlo, pueden presentar la
demo compartiendo pantalla desde otro equipo autorizado.

### Abrir la demo sin scripts de PowerShell ni Visual Studio Code

Si Python ya funciona en tu computador, puedes usar esta alternativa con las
protecciones de Windows activadas. En el Explorador, entra a la carpeta
extraída donde está `manage.py`. Haz clic en la barra de direcciones, escribe
`cmd` y pulsa **Enter**. Se abrirá el **Símbolo del sistema** en esa carpeta.

**La primera vez**, escribe estas líneas de a una y pulsa **Enter** al final
de cada una. La segunda descarga los componentes del proyecto. Si una línea
da error, detente y comparte el mensaje con quien te entregó la demo.

```bat
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install --no-deps -r requirements.txt
.\.venv\Scripts\python.exe manage.py migrate --noinput
.\.venv\Scripts\python.exe manage.py seed_demo
```

**Para abrir la demo**, ejecuta estas dos líneas. Si ya la instalaste con
`instalar_local.ps1` y conservas la misma carpeta, empieza en este paso.

```bat
.\.venv\Scripts\python.exe manage.py migrate --noinput
.\.venv\Scripts\python.exe manage.py runserver 127.0.0.1:8000 --noreload
```

Abre [Kiddo Spark local](http://127.0.0.1:8000/) en el navegador. Deja abierta
esa ventana del Símbolo del sistema. Para apagar la demo, vuelve a la ventana
y pulsa **Ctrl+C**. Si Windows también bloquea Python, usa otro computador
autorizado o pide ayuda a quien te entregó el proyecto.

Para explorar o reservar, crea tu cuenta en la portada. Si vas a probar
**Validación de proveedores** y aún no tienes cuenta de superadministración,
ejecuta `.\.venv\Scripts\python.exe manage.py createsuperuser` antes de
arrancar y sigue las preguntas de la pantalla.

## Compartir una demo remota con acceso privado

Este paso es opcional y queda separado de la instalación y el inicio local.
La demo remota inicia una copia con catálogo ficticio y su propia base,
`var/kiddo_tunnel.sqlite3`. No usa las cuentas ni los datos de la demo local.

1. Ejecuta **instalar_local** o **instalar_local.ps1** si el proyecto aún no
   está preparado.
2. Instala [Microsoft Dev Tunnels CLI](https://learn.microsoft.com/en-us/azure/developer/dev-tunnels/get-started)
   en Windows. Abre PowerShell y ejecuta `devtunnel user login`. Completa el acceso
   con la cuenta aprobada para la demostración.
3. En el Explorador, haz clic derecho en **compartir_local** o
   **compartir_local.ps1** y elige **Ejecutar con PowerShell**. Confirma
   con **S** y espera el enlace HTTPS privado. La copia usa el puerto local
   **8001**. Puedes dejar la demo normal en **8000**.
4. Abre el enlace con la misma cuenta usada en el paso anterior. Un enlace
   privado por defecto funciona para quien abrió el túnel. Para mostrarlo a
   jefatura, comparte pantalla. Si otras cuentas requieren acceso directo,
   acuerda antes el acceso con TI y consulta la
   [configuración de acceso de Microsoft](https://learn.microsoft.com/en-us/azure/developer/dev-tunnels/cli-commands#advanced-manage-dev-tunnel-access).
5. Para terminar, pulsa **Enter** en la ventana del script. Mantén la
   ventana y el equipo encendidos mientras dure la presentación.

La copia remota permite explorar el catálogo y crear cuentas familiares con
datos ficticios. Para mostrar un rol de administración con las cuentas
preparadas, usa la demo local y comparte pantalla. Un enlace temporal no es
un despliegue permanente.

## Roles y permisos

En una instalación limpia, puedes explorar de inmediato sin iniciar sesión.
Para probar una reserva, usa **Crear cuenta** en la portada y activa un plan
demo en **Exploraciones → Planes y Sparks**. Para probar el panel de operador,
primero crea el superadministrador cuando el instalador lo ofrezca y configura
la cuenta del centro con los pasos de esta sección.

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

El registro público siempre crea usuarios comunes. Las contraseñas se guardan
mediante hashes.

## Incorporar un centro

1. Entra a **Proveedores → Registrar un centro**. Crea una cuenta si es
   necesario y envía una ficha con datos ficticios de una de las cuatro comunas
   piloto. Puedes seguir el trámite en **Proveedores → Ver mis fichas**.
2. Ingresa como superadministrador y abre **Validación de proveedores**.
   Selecciona la ficha, registra el inicio de revisión y luego apruébala,
   obsérvala o recházala. Cada decisión guarda el motivo, la fecha y el responsable.
3. Si la ficha requiere corrección, vuelve a ella con la cuenta que la creó.
   Corrige los datos y reenvíala. El historial conserva la observación.
4. Tras aprobar, usa **Usuarios y permisos** para asignar un administrador al
   centro. Las actividades activas del centro pueden aparecer en el catálogo
   y el administrador asignado puede gestionar su oferta.

La lista de documentos y las condiciones de contratación están por definir.
La membresía de $35.000 CLP netos al mes es un supuesto del modelo para
proveedores pagadores. El flujo académico no activa membresías ni cobros.
El script de inicio aplica las actualizaciones de la base local al arrancar.

## Recorrido sugerido de presentación

Para una presentación no técnica, ve la [guía para presentar Kiddo Spark a
jefatura](GUIA-PRESENTACION.md). Incluye funciones por rol, preparación y un
recorrido de siete minutos para el equipo de Ingeniería Comercial.

En **Explorar actividades**, combina búsqueda, comuna, categoría, tramo de
edad, horario, Sparks y cupos. Los marcadores del mapa filtran por comuna y
cuentan las actividades que cumplen los filtros. El mapa es referencial.
Los cupos y el próximo horario de las tarjetas se calculan desde las
sesiones guardadas. En instalaciones existentes, el catálogo mantiene los
horarios anteriores. Para demostrar otra franja, crea un horario en
**Horarios y cupos**.

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
del HTML; los restantes empiezan en cero y pueden editarse. La liquidación demo
actual refleja el monto referencial completo. El modelo actualizado fija una
comisión del 10%, pendiente de implementar.
Las campañas guardan actividad, nombre, presupuesto y estado; no contratan anuncios
ni generan impresiones, clics o ROAS inventados.

## Problemas frecuentes

| Situación | Qué revisar |
| --- | --- |
| Puerto ocupado | Si ya hay un servidor abierto por otro medio, apágalo desde donde se inició. El script solo detiene el servidor que reconoce como propio. |
| Faltan tablas | Cierra la demo y vuelve a ejecutar **iniciar_local.ps1**. |
| Catálogo vacío | Comprueba que los centros estén aprobados. Si faltan los datos iniciales, apaga la demo, ejecuta **instalar_local.ps1** y vuelve a iniciarla. |
| No hay horarios | Crea un horario futuro y habilitado. |
| No puedo reservar | Comprueba saldo, cupos y que no tengas ya una reserva confirmada allí. |
| Administrador sin registros | Comprueba grupo, estado de personal y organización asignada. |
| Contraseña olvidada | El superadministrador puede cambiarla desde usuarios; para su propia cuenta usa `manage.py changepassword nombre_usuario`. |

## Verificación técnica para quien mantiene el proyecto

```powershell
.\.venv\Scripts\python.exe manage.py test core
.\.venv\Scripts\python.exe manage.py check
.\.venv\Scripts\python.exe manage.py makemigrations --check --dry-run
.\.venv\Scripts\python.exe -m pip check
node --check static/portal.js
```

Las pruebas usan una base temporal, separada de la demo. La actualización visual
se revisó en Chrome a 1440 y 390 píxeles. Se comprobaron la portada, el menú
móvil, el filtro del catálogo, proveedores y el acceso a validación desde
superadministración. La revisión en otros navegadores y el reenvío de VS Code
quedan pendientes.

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
