# Guía para presentar Kiddo Spark

Kiddo Spark es un prototipo académico que reúne actividades extracurriculares
para niñas y niños de 5 a 14 años. Permite mostrar, en un solo computador, cómo
una familia encuentra una actividad, cómo una academia administra su oferta y
cómo el equipo de Kiddo Spark revisa la incorporación de proveedores.

## Qué contar al comienzo

> Hoy una familia puede tener que buscar por separado talleres, horarios y
> cupos. Kiddo Spark propone un catálogo común para comparar opciones y
> reservar. Academias, talleres y clubes publican la oferta y realizan la
> actividad, mientras Kiddo Spark facilita la búsqueda y el seguimiento.

El piloto considera Viña del Mar, Valparaíso, Quilpué y Villa Alemana. En la
encuesta, 192 de 327 respuestas elegibles mostraron alta intención de uso
(58,72 %). Es una señal de interés declarado. La vigencia del catálogo y el
tiempo para comparar alternativas son objetivos para evaluar en un piloto.

## Qué se puede hacer hoy en la plataforma

| Quién la usa | Qué puede hacer en la demo |
| --- | --- |
| **Visitante** | Explorar el mapa referencial de las cuatro comunas piloto o buscar en el listado. Puede combinar filtros de comuna, categoría, edad, franja horaria, Sparks y cupos, y consultar el próximo horario disponible. |
| **Cliente (familia)** | Tras ingresar ve sus próximas reservas, favoritos, saldo de **Sparks** y actividades. Puede activar un plan de prueba, reservar, descargar un comprobante demo, cancelar y dejar una opinión tras asistir. En Solicitudes puede revisar su historial. |
| **Proveedor que quiere incorporarse** | Desde **Incorporar mi centro** abre su registro y envía una ficha. Al volver a ingresar, llega a **Mis fichas**, donde puede consultar la decisión y corregir datos si recibe observaciones. |
| **Operador de un centro habilitado** | Entrar al **Seller Center**, el panel de trabajo del centro. Según sus permisos, puede administrar publicaciones, horarios y cupos, cancelar un horario con al menos 48 horas de aviso, registrar asistencia y responder opiniones. |
| **Equipo de Kiddo Spark** | El administrador entra a **Estadísticas**. En **Operación → Solicitudes de proveedores** revisa fichas y habilita a su titular al aprobar. **Gestión de datos** reúne las tablas del catálogo. **Operación → Reservas** permite consultar, filtrar y exportar las reservas. Superadministración mantiene usuarios, operadores adicionales y permisos generales. |
| **Empresa, colegio o centro que busca apoyo** | Desde la portada pública se puede iniciar una solicitud de convenio. Los perfiles habilitados pueden pedir una demostración corporativa. En **Alivios B2B**, un proveedor puede pedir orientación, asesoría o una cotización. |

Para mostrar cómo se conectan los roles, hagan una reserva como cliente y
muestren **Reservado** y la campanita. Cambien a la cuenta del proveedor,
abran **Horarios y cupos** y cancelen ese horario indicando un motivo.
Preparen un horario con más de 48 horas de anticipación para esta parte.
Vuelvan a la cuenta de cliente para mostrar **Cancelado**, el aviso con el
motivo y la devolución de Sparks. Con otra reserva pueden mostrar cómo la
asistencia acredita puntos y habilita una opinión.

Antes de cancelar, abran la campanita del proveedor para mostrar **Nueva
reserva en tu centro**. Luego entren al Seller Center y elijan un taller.
El mapa de calor muestra cuándo se concentran las reservas y las tarjetas
resumen ocupación, asistencia y opiniones. Con `admin`, elijan el mismo
centro desde **Estadísticas** para ver el mismo resumen.
El gráfico de evolución usa los registros de la demo. Pueden abrir
**Ver datos del gráfico** para consultar las cantidades exactas. En
**Gestión de datos → Proveedores** pueden mostrar las fichas y cambiar de
tabla desde el mismo menú lateral.

**Qué se simula.** Los Sparks sirven para probar reservas y cancelaciones
sin dinero real. Los comprobantes son ilustrativos. El Seller Center permite
revisar liquidaciones de ejemplo, simular solicitudes de retiro y configurar
campañas sin difundir anuncios. El panel de convenios muestra cifras de
ejemplo; el envío y seguimiento de solicitudes sí funciona.

**Qué falta para operar.** La versión actual no procesa pagos ni transferencias
bancarias, no emite documentos tributarios ni pone en marcha convenios reales.
Todavía deben definirse el medio de pago, las condiciones comerciales, la
validación documental de centros y el alojamiento. Usen identidades ficticias
y eviten datos de menores, medios de pago o cuentas bancarias reales.

## Preparar el computador

Para grabar los videos de defensa, basta abrir **Abrir demo defensa.cmd** en
la carpeta principal y seguir la [guía de cuentas y recorridos](docs/DEFENSA-DATOS.md).
Para practicar cada perfil, consulta el [manual de usuario](MANUAL-USUARIO.md).
Los pasos siguientes usan la demo habitual para la presentación de siete minutos.

- Si el computador aún no está preparado, sigan la
  [guía para Windows](README.md#antes-de-empezar-en-windows).
- En `scripts/mantenimiento/`, hagan doble clic en **Abrir Kiddo Spark.cmd**.
  Mantengan abierta su ventana durante
  la demostración. Para apagarla, vuelvan a esa ventana y pulsen **Ctrl+C**.
- En el mismo computador, abran [Kiddo Spark local](http://127.0.0.1:8000/).
  Compartan la pantalla o conéctenla al proyector. Esa dirección corresponde
  al computador que ejecuta la demo.
- Antes de presentar, prueben el ingreso y elijan **Taller de movimiento
  demo** u otra actividad con horario futuro y cupos. Usen una ventana privada
  para la familia si quieren mantener superadministración abierta por separado.
- Si la página no abre, quien prepara la demo puede seguir la sección
  **Encender y apagar** del [README](README.md).

### Cuentas para mostrar los cuatro perfiles

Las cuentas se crean al preparar la demo local. En la portada, pulsen
**Ingresar**. Usen el mismo texto como nombre de usuario y contraseña.
Si ya tenían una cuenta con ese nombre, sigan usando sus datos actuales.

| Para mostrar | Usuario y contraseña |
| --- | --- |
| Cliente que busca y reserva para su familia | `usuario` |
| Centro que gestiona horarios y asistencia | `proveedor` |
| Equipo que administra catálogo y solicitudes | `admin` |
| Revisión de proveedores | `admin` o `superadmin` |
| Gestión de usuarios y permisos generales | `superadmin` |

Son cuentas ficticias del computador local. Los correos y permisos están
en el [README](README.md#roles-y-permisos).

## Recorrido sugerido de siete minutos

Si la reunión es remota, lo más sencillo es compartir la pantalla de quien
ejecuta la demo local. También existe la opción de abrir una copia de la demo
con un enlace temporal por Internet. Quien prepara el computador puede seguir
**Compartir una demo remota con acceso privado** en el [README](README.md).
Esa copia parte con su propio catálogo de ejemplo y cuentas separadas. El
enlace privado solo abre con la cuenta que lo generó. Para mostrar reservas
guardadas o la revisión de proveedores con las cuentas preparadas, compartan
la pantalla de la demo local.

| Tiempo | Qué mostrar | Qué decir |
| --- | --- | --- |
| 1 min | Abran la portada pública. Muestren los accesos por disciplina junto a la escena ilustrativa de robótica. Desplácense hasta las comunas y las cifras del piloto. | «Esta es la propuesta de servicio. La encuesta mide interés declarado y las otras cifras orientan qué queremos evaluar». |
| 2 min | **Explorar actividades**. Seleccionen una comuna y abran una ficha con cupos. Reserven con la cuenta de cliente y muestren la campanita. | «Cuando hay cupo, la reserva queda lista en el momento. La familia recibe un aviso dentro del portal». |
| 2 min | Desde **Horarios y cupos**, cambien a la cuenta del proveedor y cancelen un horario con al menos 48 horas de anticipación. Muestren el aviso y el saldo del cliente. | «El centro indica el motivo. Cada familia afectada recibe el aviso y recupera sus Sparks». |
| 1 min | **Empresas y colegios** en la portada. Muestren la propuesta de convenio y el panel ilustrativo. | «Los convenios exploran un beneficio extracurricular para comunidades. El panel ilustra cómo ver participación agregada». |
| 1 min | Cierre y conversación con jefatura. | «Queremos comentarios sobre el proceso y el valor para familias y centros, para definir qué mediríamos en un piloto». |

Para mostrar cómo se seguiría el piloto, entren como `admin`. El ingreso lleva
directamente a **Estadísticas**. Seleccionen **7 días** o el período en
que hicieron las pruebas. Muestren qué comunas concentraron más reservas,
cuántas reservas se completaron y cuántas solicitudes quedan pendientes o
en revisión. Luego abran **Catálogo y próximos cupos** para mostrar cuántos
centros están habilitados, cuántas actividades se publicaron y qué proporción de sus próximos
cupos está ocupada. Esa sección muestra la oferta actual, aunque cambien las
fechas arriba. Pueden decir «Estas cifras se actualizan según lo que hacemos
en la demo. En un piloto podríamos usar la misma vista para seguir la
demanda y decidir dónde necesitamos más horarios».

El menú principal queda visible en el teléfono y en el computador. En la
cuenta de administración, arriba están **Actividades**, **Alivios B2B** y
la campanita de avisos. El lateral agrupa **Operación**, **Gestión de datos**
y **Cuenta**. Pulsen el nombre de un grupo para abrirlo o plegarlo. Para
cliente o proveedor, **Mi panel** abre **Configuración de perfil**, donde
se pueden editar los datos y cambiar la contraseña desde **Seguridad de
la cuenta**.

Si van a mostrar una aprobación, practiquen antes con una ficha ficticia.
Aprobar habilita al titular para su centro. Publicar una actividad y crear sus
sesiones son pasos posteriores del proveedor.

Para cargar el escenario pequeño de la demo habitual, usa **Cargar datos demo.cmd**
en `scripts/mantenimiento/` y sigue la [guía B2B → B2C](docs/DEMO-ACADEMICA.md). Las cuentas `kidsdemo` y
`robotica_demo` tienen actividades y reservas; `deporte_demo` y `arte_demo`
permiten mostrar revisión y correcciones. Los paneles distinguen registros
simulados de las metas y proyecciones financieras.

Si quieren mostrar **Alivios B2B**, usen el minuto de convenios para abrir
**Alivios B2B** desde el menú principal. Marquen un tema en el diagnóstico, elijan un
aliado de ejemplo y guarden una cotización. Muestren el estado en **Mis
solicitudes**. Pueden decir: «El centro encuentra apoyo y puede seguir su
solicitud. La fecha que elige es una preferencia para conversar».

## Cómo explicarlo si preguntan por la tecnología

- **Navegador web.** La interfaz usa HTML para organizar el contenido, CSS
  para presentarlo y JavaScript para interacciones como la calculadora de Sparks.
- **Django y Python.** Reciben las acciones que hace cada persona, aplican
  reglas y permisos y muestran el resultado en pantalla.
- **SQLite.** Guarda las cuentas de prueba, las fichas, los horarios y las
  reservas en un archivo local. Los registros persisten al cerrar el navegador.
