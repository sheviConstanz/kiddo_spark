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
| **Familia** | Crear una cuenta, guardar favoritos y activar un plan de prueba para cargar **Sparks**, los créditos de la demo. Puede reservar un horario con cupo, consultar sus movimientos, descargar un comprobante de ejemplo y cancelar una reserva confirmada para recuperar los Sparks. Después de que el centro marque la reserva como completada, puede dejar una opinión. |
| **Proveedor que quiere incorporarse** | Registrar su centro, seguir el estado de su ficha y corregirla y reenviarla si recibe observaciones. Puede consultar si fue aprobada o rechazada y leer la decisión. |
| **Operador de un centro habilitado** | Entrar al **Seller Center**, el panel de trabajo del centro. Según sus permisos, puede crear, editar o desactivar publicaciones, administrar horarios y cupos, ver y exportar reservas, registrar asistencia y responder opiniones. El panel muestra reservas y actividades más solicitadas a partir de los registros de la demo. |
| **Equipo de Kiddo Spark** | Revisar, observar, aprobar o rechazar fichas, con un historial de las decisiones. Puede asignar permisos a operadores, administrar el catálogo y dar seguimiento a solicitudes. La aprobación del centro y la asignación del operador son pasos separados. |
| **Empresa, colegio o centro que busca apoyo** | Enviar una solicitud de convenio o demostración. Los centros también pueden consultar el directorio de aliados de ejemplo y solicitar asesoría o una cotización. Las solicitudes quedan guardadas y se puede revisar su avance. |

Para mostrar cómo se conectan los roles, hagan una reserva familiar en una
actividad con cupos. Abran la reserva desde la cuenta del centro, registren
la asistencia y vuelvan a la cuenta familiar para dejar una opinión. Las
reservas, cambios de cupos, opiniones y solicitudes quedan guardados al
cerrar el navegador.

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

- Si el computador aún no está preparado, ejecuten **instalar_local.ps1**.
- En el Explorador de archivos, hagan clic derecho en **iniciar_local.ps1** y
  elijan **Ejecutar con PowerShell**. Una vez que la demo indique que está
  lista, pueden cerrar esa ventana. Para apagarla, ejecuten el mismo archivo
  y confirmen. Comprueben que las cuentas ficticias estén listas.
- En el mismo computador, abran [Kiddo Spark local](http://127.0.0.1:8000/).
  Compartan la pantalla o conéctenla al proyector. Esa dirección corresponde
  al computador que ejecuta la demo.
- Antes de presentar, prueben el ingreso y elijan una actividad con horario
  futuro y cupos. Preparen una cuenta familiar, una cuenta con acceso al
  Seller Center y la cuenta de superadministración. Usen una ventana privada
  para la familia si quieren mantener superadministración abierta por separado.
- Si la página no abre, quien prepara la demo puede seguir la sección
  **Encender y apagar** del [README](README.md).

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
| 1 min | Portada, comunas y cifras del piloto. | «Esta es la propuesta de servicio. La encuesta mide interés declarado y las otras cifras orientan qué queremos evaluar». |
| 2 min | **Explorar actividades**. Seleccionen una comuna en el mapa, combinen filtros y abran una ficha con cupos. En una cuenta familiar, activen un plan demo si necesitan Sparks, hagan una reserva y ábranla en **Reservas**. | «El mapa orienta por comuna. Los horarios y cupos vienen de lo que registra el centro. La demo descuenta Sparks de prueba y guarda la reserva». |
| 2 min | **Proveedores**. Muestren una ficha en revisión y, con superadministración, la cola de **Validación de proveedores**. Con un operador habilitado, abran **Publicaciones** y **Horarios y cupos**. | «Primero incorporamos la oferta. El equipo revisa al proveedor y registra el motivo de su decisión. El centro habilitado mantiene sus propios horarios y cupos». |
| 1 min | **Empresas y colegios** en la portada. Muestren la propuesta de convenio y el panel ilustrativo. | «Los convenios exploran un beneficio extracurricular para comunidades. El panel ilustra cómo ver participación agregada». |
| 1 min | Cierre y conversación con jefatura. | «Queremos comentarios sobre el proceso y el valor para familias y centros, para definir qué mediríamos en un piloto». |

Si van a mostrar una aprobación, practiquen antes con una ficha ficticia. La
aprobación y la asignación del operador son pasos separados.

## Cómo explicarlo si preguntan por la tecnología

- **Navegador web.** La interfaz usa HTML para organizar el contenido, CSS
  para presentarlo y JavaScript para interacciones como el menú móvil.
- **Django y Python.** Reciben las acciones que hace cada persona, aplican
  reglas y permisos y muestran el resultado en pantalla.
- **SQLite.** Guarda las cuentas de prueba, las fichas, los horarios y las
  reservas en un archivo local. Los registros persisten al cerrar el navegador.
