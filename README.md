# Kiddo Spark · Prototipo funcional académico

Plataforma de demostración para una tesis de Ingeniería Comercial: conecta
familias, actividades extracurriculares, academias, empresas/colegios y aliados
de apoyo en la Región de Valparaíso. Conserva colores, logo y lenguaje visual
de la propuesta original.

**No opera un negocio real.** Planes, Sparks, campañas, montos y retiros son
simulados. Cuentas, reservas, solicitudes y cambios sí se guardan en una base
local. Usa datos ficticios, nunca información real de menores ni cuentas bancarias.

## Antes de empezar en Windows

Necesitas **Windows**, **Python 3.14 o 3.15**, un navegador e Internet para
la primera instalación. Puedes hacer todo desde el Explorador de archivos.
No necesitas Visual Studio Code.

Para comprobar Python, busca **Aplicaciones instaladas** en el menú
**Inicio** y escribe **Python** en la lista. Si aparece **Python 3.14** o
**Python 3.15**, sigue con la descarga. Si no lo encuentras, pide ayuda o
usa la [descarga oficial de Python](https://www.python.org/downloads/windows/).

<details>
<summary>Si solo aparece Python Install Manager o el instalador no encuentra Python</summary>

Abre **Inicio**, busca
**Símbolo del sistema** y escribe `python --version`. Pulsa **Enter**.
Si ves, por ejemplo, `Python 3.14.7`, puedes continuar. Si Windows no
reconoce el comando, abre Microsoft Store en vez de mostrar una versión
o muestra una versión distinta, pide ayuda a TI o usa la
[descarga oficial de Python para Windows](https://www.python.org/downloads/windows/).
Si el instalador ofrece **Add Python to PATH**, marca esa opción para que
Windows encuentre Python. Cierra y vuelve a abrir la ventana antes de repetir
la comprobación.

</details>

## Descargar y abrir Kiddo Spark

1. Abre la [página de Kiddo Spark](https://github.com/sheviConstanz/kiddo_spark),
   donde están guardados los archivos. Haz clic en el botón verde **Code**
   y luego en **Download ZIP**.
2. En **Descargas**, haz clic derecho en el ZIP y elige **Extraer todo**.
   Abre la carpeta que se acaba de crear.
3. Haz **doble clic** en **Abrir Kiddo Spark**. Puede verse como
   **Abrir Kiddo Spark.cmd** si Windows muestra el nombre completo.
4. Si pregunta si puede descargar lo que falta, responde **S** y pulsa
   **Enter**. Espera a que se abra el navegador. Si no se abre, entra a
   [Kiddo Spark local](http://127.0.0.1:8000/).

Puedes explorar de inmediato. Para probar reservas, el panel del centro o
la administración, usa las [cuentas de prueba](#roles-y-permisos).
La instalación las prepara automáticamente.

## Encender y apagar

Para encender, vuelve a hacer doble clic en **Abrir Kiddo Spark**. Si la
demo ya está encendida, el archivo abre la página otra vez. Para apagar,
vuelve a la ventana negra que quedó abierta y pulsa **Ctrl+C**. Si Windows
pregunta si quieres terminar, confirma. Cerrar el navegador deja la demo
encendida.

Si te pasan una versión nueva, apaga la demo antes de abrirla. Conserva la
carpeta donde la instalaste para mantener tus cuentas y reservas.

## Si Windows bloquea un archivo

El archivo **Abrir Kiddo Spark** no usa PowerShell. Si Windows también lo
bloquea, revisa el texto del aviso o usa los pasos del **Símbolo del sistema**
que aparecen más abajo.

### Si el aviso indica que el archivo se descargó de Internet

Si descargaste Kiddo Spark desde el enlace oficial de este README y confías
en el archivo, revisa si Windows ofrece desbloquear ese archivo concreto:

1. En el Explorador, haz clic derecho en el archivo que mostró el aviso
   (por ejemplo, **instalar_local** o **instalar_local.ps1**) y elige
   **Propiedades**.
2. En la pestaña **General**, baja hasta el final y busca **Desbloquear** en
   el apartado **Seguridad**. Si aparece, marca la casilla y pulsa **Aplicar**
   y **Aceptar**.
3. Vuelve a hacer clic derecho sobre el archivo y elige
   **Ejecutar con PowerShell**.

Esta opción quita la marca de descarga del archivo. Si no aparece o el aviso
sigue, fíjate en el mensaje exacto y revisa el apartado siguiente.
[Instrucciones de Microsoft](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.core/about/about_signing?view=powershell-7.4#run-unsigned-scripts-using-the-remotesigned-policy).

### Si el aviso es de Control inteligente de aplicaciones

Si aparece un aviso de **Control inteligente de aplicaciones** en Windows 11
que dice que el archivo podría no ser seguro, detente. Guarda una captura o
copia el mensaje completo y envíalo a TI junto con el nombre del archivo y el
enlace de descarga. Pide una versión firmada y aprobada para el equipo, o
usa un computador autorizado para la demo. Mantén activada la protección.
**Desbloquear** no crea una excepción en Control inteligente de aplicaciones.
Microsoft indica que esta protección no admite excepciones por archivo.
[Ayuda de Microsoft sobre Control inteligente de aplicaciones](https://support.microsoft.com/en-gb/windows/security/threat-malware-protection/smart-app-control-frequently-asked-questions).

### Si PowerShell dice que la ejecución de scripts está deshabilitada

Ese mensaje se refiere a la política de PowerShell. La casilla
**Desbloquear** quita la marca de descarga, pero no cambia esa política.
La opción más directa es hacer doble clic en **Abrir Kiddo Spark**.

<details>
<summary>Opción para quien prepara la demo en un computador personal</summary>

En un **PC personal que tú administras**, si prefieres usar los scripts,
abre la carpeta extraída, escribe `powershell` en la barra de direcciones
del Explorador y pulsa **Enter**. Ejecuta `Get-ExecutionPolicy -List`.
Si `MachinePolicy` y `UserPolicy` muestran `Undefined`, puedes permitir
scripts locales de confianza solo para esta ventana:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
.\instalar_local.ps1
.\iniciar_local.ps1
```

Ejecuta una línea a la vez en esa misma ventana. Si ya instalaste el
proyecto, omite la línea de instalación. La política de esta sesión
termina al cerrar PowerShell. Si el equipo está administrado o si el
aviso persiste, usa la alternativa de abajo o consulta a TI.
[Políticas de ejecución de PowerShell](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.core/about/about_execution_policies?view=powershell-7.5#execution-policy-scope-and-precedence).

</details>

### Abrir la demo sin scripts de PowerShell ni Visual Studio Code

<details>
<summary>Ver pasos para abrir la demo desde Símbolo del sistema</summary>

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

Cuando abras la demo local, usa las [cuentas de prueba](#roles-y-permisos).
El paso que prepara la base ya se encarga de crearlas.

</details>

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
datos ficticios. Las cuatro cuentas de prueba son exclusivas de la demo local.
Para mostrar un rol de administración con las cuentas
preparadas, usa la demo local y comparte pantalla. Un enlace temporal no es
un despliegue permanente.

## Roles y permisos

En [Kiddo Spark local](http://127.0.0.1:8000/), haz clic en **Ingresar**
y usa el nombre de usuario y la contraseña de la fila que quieras probar.
La primera vez que se prepara o actualiza la base, la migración crea las
cuentas que falten. El instalador no pide crearlas.

| Perfil | Usuario | Contraseña | Correo | Qué puede hacer |
| --- | --- | --- | --- | --- |
| Superadministrador | `superadmin` | `superadmin` | `correo@superadmin.cl` | Entra a **Superadministración**. Puede gestionar usuarios y permisos, revisar proveedores y asignar operadores. Usa **Ver sitio** para volver al panel operativo. |
| Administrador de plataforma | `admin` | `admin` | `admin@demo.example.invalid` | Entra a **Estadísticas**. En **Gestión operativa** puede trabajar con catálogo, horarios, categorías, comunas, planes, reservas y solicitudes. Usuarios, grupos, permisos, validación de proveedores, datos bancarios y retiros siguen reservados a superadministración. |
| Cliente | `usuario` | `usuario` | `usuario@demo.example.invalid` | Entra a su inicio con próximas reservas, favoritos, Sparks y catálogo. En **Solicitudes** puede consultar su historial. |
| Proveedor | `proveedor` | `proveedor` | `proveedor@demo.example.invalid` | Entra al **Seller Center** del **Centro Kiddo Spark Demo**. Gestiona publicaciones, horarios y reservas del centro asignado. |

Para probar la aprobación, entra como `usuario`, activa un plan de prueba en
**Planes y Sparks** y solicita **Taller de movimiento demo**. Luego entra
como `proveedor`, abre **Reservas → Ver pendientes por aprobar** y pulsa
**Confirmar reserva**. Si el horario ya venció, crea uno futuro en **Horarios
y cupos** antes de solicitarlo.

Estos datos son de una instalación nueva. Si ya existe una cuenta con el
mismo nombre o correo, se conserva con su contraseña y permisos. Las
credenciales de la tabla son públicas y están pensadas solo para esta demo
local con datos ficticios. No las reutilices en otro sistema.

Para dar acceso a otro operador de un centro:

1. Ingresa como superadministrador y abre **Usuarios y permisos**.
2. Crea un usuario con correo ficticio y contraseña propia.
3. Edita ese usuario; marca **Activo** y **Estado de personal**, sin marcar
   **Estado de superusuario**.
4. Asigna el grupo **Administradores de organización** y guarda.
5. En **Organizaciones**, edita su centro y añade al usuario en **Administradores**.

El grupo concede módulos; la asignación limita registros. Para limitar módulos,
crea otro grupo con los permisos necesarios, sin asignar el grupo completo anterior.
Un operador de proveedor sin centro asignado no podrá gestionar centros ajenos.
El administrador de plataforma y el superadministrador pueden gestionar los
convenios sin aliado destinatario.

**Crear cuenta** abre el registro de cliente. **Registrar un centro** abre el
registro de proveedor en incorporación. La cuenta puede presentar una ficha y
ver su revisión. Los permisos de gestión del centro se asignan por separado.

## Incorporar un centro

1. Desde la portada pública, abre **Incorporar mi centro → Registrar un
   centro**. Crea una cuenta de proveedor y envía una ficha con datos ficticios
   de una de las cuatro comunas piloto. Al volver a ingresar, verás **Mis fichas**.
2. Ingresa como superadministrador y abre **Ver sitio → Validación de proveedores**.
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
Al actualizar, apaga la demo y abre **Abrir Kiddo Spark** desde la carpeta
actualizada. La migración 0008 conserva las fichas y contraseñas existentes.

## Probar Alivios B2B

1. Abre **Alivios B2B** en el menú principal. También puedes
   entrar desde **Proveedores**.
2. Usa el **Diagnóstico rápido** o filtra el directorio por contabilidad,
   legal, mantención, seguros y prevención, o marketing y audiovisual.
3. Ingresa como `proveedor` y elige **Solicitar asesoría**, **Cotizar** o
   **Necesito ayuda para definir mi problema**. Puedes indicar una comuna,
   fecha, hora y canal preferidos.
4. Revisa el estado en **Mis solicitudes**. Con la cuenta `admin`, abre
   **Solicitudes** para registrar una actualización y luego mírala de nuevo
   con la cuenta del proveedor.

Las fichas son de ejemplo. La demo guarda tus solicitudes y preferencias,
pero no confirma citas, contacta aliados ni envía correos.

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
3. En **Explorar**, filtra, abre una actividad y pulsa **Solicitar reserva**.
   Se apartan el cupo y los Sparks. La reserva queda **Pendiente de aprobar**.
4. Entra como proveedor del centro y pulsa **Confirmar reserva** en
   **Reservas**. El cliente verá el estado **Confirmada** y podrá descargar el
   comprobante demo. Si cancela mientras está pendiente o confirmada, la demo
   devuelve el cupo y los Sparks una sola vez.
5. Con el proveedor, pulsa **Validar asistencia** en la reserva confirmada.
   Las nuevas reservas suman 50 puntos al completarse. El cliente puede dejar
   una opinión y el centro puede responder desde **Reputación**.
6. Solicita un convenio desde **Empresas y colegios** en la portada pública.
   Para mostrar una asesoría, ingresa como proveedor y abre **Alivios B2B**.
   Consulta el historial en **Solicitudes**.
7. Con el administrador correspondiente, avanza el seguimiento: pendiente →
   en revisión → aprobada → completada. Puede rechazarse antes de aprobar.
8. Crea y edita actividades, horarios y campañas en **Mantenedores**.
   Desactivar conserva el historial; editar permite reactivar.
9. En **Finanzas demo**, consulta montos referenciales de experiencias completadas
   y solicita un retiro ficticio. El superadministrador puede completar la
   simulación o rechazarla para liberar saldo. No hay conexión bancaria.
10. Ingresa como `admin` o `superadmin` y abre **Estadísticas** en **Mi panel**.
    El proveedor conserva el resumen de su centro.

Los nombres de centros proceden del material original y no acreditan convenios
reales. Cupos y fechas son demostrativos. Los precios identificables se tomaron
del HTML; los restantes empiezan en cero y pueden editarse. La liquidación demo
actual refleja el monto referencial completo. El modelo actualizado fija una
comisión del 10%, pendiente de implementar.
Las campañas guardan actividad, nombre, presupuesto y estado; no contratan anuncios
ni generan impresiones, clics o ROAS inventados.

Los [flujos B2C y B2B de Bizagi](docs/FLOWS-BIZAGI.md) detallan qué partes
de los diagramas se pueden demostrar y qué decisiones siguen pendientes.

## Navegación y estadísticas

El menú principal deja visibles todos los enlaces de tu perfil. La portada
pública incluye **Proveedores**, **Empresas y colegios**, **Alivios B2B** y
**Propuesta original**. El cliente ve **Explorar actividades** y **Planes y
Sparks**. En el teléfono los enlaces se ordenan en filas según el espacio.
Pulsa **Mi panel** para ver los accesos de tu cuenta. Al volver a una sección
pública se oculta el menú de cuenta.

En **Mi panel → Estadísticas**, usa **Últimos 7 días**, **Últimos 30 días**,
**Todo el historial** o selecciona fechas específicas. El período se aplica
a la fecha en que se creó cada reserva o solicitud e incluye ambos extremos.

- Las barras muestran reservas por día, por comuna y por estado, además de
  solicitudes por estado. La tendencia muestra hasta siete fechas con
  reservas. La tendencia y los rankings cuentan las confirmadas y completadas.
- La tasa de finalización divide las reservas completadas por todas las
  reservas del período, incluidas las canceladas. Las solicitudes abiertas
  son las pendientes y las que están en revisión.
- **Catálogo y próximos cupos** muestra las actividades publicadas, los
  centros habilitados y los horarios futuros activos de esas actividades.
  La ocupación se calcula restando los cupos disponibles a la capacidad
  total y dividiendo ese resultado por la capacidad total. Esta sección
  refleja el estado actual y queda fuera del filtro de fechas.

Para ver cómo cambian las cifras, crea una reserva o una solicitud de prueba
y vuelve al panel. Si no hay horarios futuros, el proveedor puede agregar uno
en **Mi panel → Horarios y cupos** para mostrar el gráfico de ocupación.
La vista muestra datos agrupados de la demo.

## Problemas frecuentes

| Situación | Qué revisar |
| --- | --- |
| Puerto ocupado | Si ya hay un servidor abierto por otro medio, apágalo desde donde se inició. El script solo detiene el servidor que reconoce como propio. |
| Faltan tablas | Cierra la demo y vuelve a ejecutar **iniciar_local.ps1**. |
| Catálogo vacío | Comprueba que los centros estén aprobados. Si faltan los datos iniciales, apaga la demo, ejecuta **instalar_local.ps1** y vuelve a iniciarla. |
| No hay horarios | Crea un horario futuro y habilitado. |
| No puedo reservar | Comprueba saldo, cupos y que no tengas ya una reserva pendiente o confirmada para ese horario. |
| No aparece «Confirmar reserva» | Entra como proveedor del centro asignado. El horario debe seguir vigente y la reserva debe estar pendiente. |
| Administrador sin registros | Comprueba grupo, estado de personal y organización asignada. |
| Contraseña olvidada | El superadministrador puede cambiarla desde usuarios; para su propia cuenta usa `manage.py changepassword nombre_usuario`. |

## Verificación técnica para quien mantiene el proyecto

```powershell
.\.venv\Scripts\python.exe manage.py test core
.\.venv\Scripts\python.exe manage.py check
.\.venv\Scripts\python.exe manage.py makemigrations --check --dry-run
.\.venv\Scripts\python.exe -m pip check
.\.venv\Scripts\python.exe -m unittest scripts.test_open_local
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
- `Abrir Kiddo Spark.cmd`: abre el programa desde el Explorador de Windows.
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
