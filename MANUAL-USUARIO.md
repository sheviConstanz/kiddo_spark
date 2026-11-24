# Manual de usuario de Kiddo Spark para Ingeniería Comercial

Usa Kiddo Spark para recorrer la operación de una plataforma de actividades
infantiles desde tres perfiles. La familia busca y reserva, el centro gestiona
su oferta y la administración supervisa la operación. Las cuentas, los créditos
y los montos de esta demostración son ficticios.

- [Abrir la plataforma](#abrir-la-plataforma)
- [Familia](#familia)
- [Proveedor](#proveedor)
- [Administración](#administración)
- [Seguir una reserva con los tres perfiles](#seguir-una-reserva-con-los-tres-perfiles)
- [Leer los indicadores](#leer-los-indicadores)
- [Resolver problemas frecuentes](#resolver-problemas-frecuentes)

## Abrir la plataforma

Necesitas Windows y Python 3.14 o 3.15. Si el equipo aún no tiene Python, sigue
las [instrucciones de preparación](README.md#antes-de-empezar-en-windows).

1. Extrae el ZIP de Kiddo Spark y abre la carpeta resultante en el Explorador
   de Windows.
2. Haz doble clic en **Abrir demo defensa.cmd**. El acceso prepara los datos,
   añade los horarios que falten para los próximos 35 días y abre el navegador.
   Si pide permiso para instalar los componentes de la primera ejecución,
   escribe **S** y pulsa **Enter**.
3. Pulsa **Ingresar** y usa una cuenta de la tabla. Si el navegador no se abre,
   visita [la demo de defensa](http://127.0.0.1:8002/) desde el mismo computador.

| Perfil | Usuario | Primera pantalla |
| --- | --- | --- |
| Familia | `defensa_familia_01` | Inicio con próximas reservas, favoritos y saldo |
| Centro de actividades | `defensa_proveedor_01` | Seller Center de Academia Horizonte |
| Administración | `defensa_admin` | Estadísticas de la plataforma |
| Superadministración | `defensa_superadmin` | Panel de usuarios y permisos |
| Centro en incorporación | `defensa_proveedor_11` | Mis fichas, con una solicitud que requiere correcciones en la base inicial |

La contraseña pública de estas cuentas demo es `DemoAcademica2026!`.
Para cambiar de perfil, usa **Mi panel → Salir**. En administración, **Salir**
está en **Cuenta** del menú lateral. Para cerrar la plataforma, pulsa **Ctrl+C**
en la ventana que abrió la demo. Cerrar el navegador solo cierra la página.

La base inicial trae 8 centros aprobados, 20 actividades, 30 familias, 60
reservas y 15 opiniones. Las operaciones que hagas durante un ensayo se guardan
y pueden cambiar esas cifras. Usa únicamente datos ficticios en formularios.

## Familia

### Buscar y reservar una actividad

1. Abre **Explorar actividades**. Busca por nombre o filtra por comuna,
   categoría, edad, horario y máximo de Sparks. Usa **Solo con cupos** para
   limitar los resultados o selecciona una comuna en el mapa.
2. Abre **Ver horarios** en la actividad. Revisa el centro, las edades, el
   lugar, la fecha, la hora, los cupos y cuántos Sparks cuesta reservar.
   El corazón guarda la actividad en **Favoritos**.
3. Pulsa **Reservar** junto a una sesión y confirma. Cada reserva ocupa un
   cupo y descuenta los Sparks indicados. La campanita muestra el aviso.
4. Ve a **Mi panel → Reservas**. Ahí encontrarás el código **KS-…**, el
   estado **Reservado** y la opción **Comprobante demo**. El comprobante
   documenta la operación de prueba. Los Sparks son créditos simulados.

### Consultar el saldo, cancelar y valorar

- Abre **Mi panel** y pulsa el enlace que muestra tu saldo en **Sparks**.
  En **Mis Sparks** puedes revisar recargas, descuentos y devoluciones.
  Si te falta saldo, abre **Planes y Sparks** y activa un plan demo.
- En **Mis reservas**, abre **Cancelar** y confirma cuando la reserva requiera
  una anulación. El estado cambia a **Cancelado**, se libera el cupo y se
  devuelven los Sparks. La reserva queda visible en el historial.
- Una vez que el centro registre la asistencia, abre **Valorar** en la reserva.
  Selecciona una nota y escribe un comentario sobre la experiencia de prueba.
  Cada reserva admite una opinión.

## Proveedor

### Publicar una actividad con cupos

1. En el menú lateral del Seller Center, abre **Gestión de datos → Mis
   actividades → Nueva actividad**.
2. Completa nombre, centro, categoría, edades, modalidad, lugar, descripción
   y Sparks por reserva. Guarda la ficha como **Borrador** mientras preparas
   la agenda.
3. Desde la fila de la actividad, abre **Sesiones y cupos → Nueva sesión**.
   Indica fecha y hora futuras, define la capacidad y guarda la sesión.
4. Vuelve a editar la actividad y cambia su estado a **Publicada**. La familia
   la podrá encontrar cuando el centro esté aprobado y la actividad tenga
   una sesión futura con cupos.

**Pausar** retira la actividad del catálogo y conserva las reservas anteriores.
Si debes suspender una sesión específica, abre **Gestión de datos → Horarios y
cupos** y usa **Cancelar horario**. Esta opción requiere al menos 48 horas de
anticipación. Escribe el motivo para que el portal avise a las familias con
reservas vigentes y les devuelva sus Sparks.

### Gestionar reservas y revisar el desempeño

- En **Operación → Reservas**, busca por actividad, titular o estado. El
  listado reúne las reservas de los centros asignados a tu cuenta.
- Después de la sesión, selecciona **Validar asistencia** para las reservas
  de quienes participaron. La reserva mantiene su código y suma la marca
  **Asistencia registrada**. La familia puede valorarla a partir de ese momento.
- En **Operación → Resumen ejecutivo**, compara reservas, asistencia,
  cancelaciones y ocupación. Selecciona un taller para leer sus cifras y usa
  **Exportar CSV** en **Rendimiento por taller** para obtener la tabla filtrada.
- En **Desempeño → Reputación**, consulta las notas y comentarios de tus
  centros. Abre **Responder** para registrar una respuesta a una opinión.

### Dar de alta a un centro

Desde **Proveedores → Registrar un centro** puedes crear una cuenta de
proveedor y enviar la ficha con los datos ficticios del centro. En **Mi
panel → Mis fichas**, revisa el estado y las observaciones. Si piden
correcciones, abre la ficha, actualiza sus datos y reenvíala. Cuando
administración apruebe la ficha, el titular podrá operar el centro en el
Seller Center.

## Administración

### Consultar y exportar reservas

1. Abre **Operación → Reservas** para ver **Reservas de la plataforma**.
2. Filtra por centro, actividad, usuario, estado o rango de fechas. El rango
   se aplica al día en que se creó la reserva. Para localizar una fila, busca
   por actividad o titular y comprueba el código en la columna **Reserva**.
3. Abre **Comprobante demo** para revisar el detalle de una operación. Usa
   **Exportar CSV** para llevar a Excel las filas que coinciden con los filtros.

### Revisar fichas y solicitudes

| Si necesitas… | Entra a… | Qué hacer |
| --- | --- | --- |
| Revisar el alta de un centro | **Operación → Solicitudes de proveedores** | Abre **Revisar**, registra el inicio de la revisión y luego aprueba, rechaza o pide una corrección según corresponda. Escribe el motivo y guarda la decisión. |
| Dar seguimiento a una solicitud B2B | **Operación → Solicitudes** | Abre la solicitud, revisa su historial y registra el siguiente estado permitido junto con una nota. |
| Consultar el catálogo y los planes | **Gestión de datos** | Abre el listado de proveedores, actividades, horarios, categorías, comunas o planes según la tarea. |

Las cuentas de superadministración se usan para gestionar usuarios y permisos.
Para revisar reservas y estadísticas del día a día, usa `defensa_admin`.

## Seguir una reserva con los tres perfiles

| Paso | Qué hacer | Qué comprobar |
| --- | --- | --- |
| 1. Familia | Busca **Natación infantil · Demo** de Academia Horizonte, elige un horario futuro con cupos y reserva. | Anota el código **KS-…**, fecha, hora y Sparks descontados. |
| 2. Proveedor | Ingresa como `defensa_proveedor_01`. Abre **Operación → Reservas** y busca la actividad o el usuario `defensa_familia_01`. | El código y el horario coinciden. En **Horarios y cupos** ves el cupo ocupado en esa sesión. |
| 3. Administración | Ingresa como `defensa_admin` y filtra **Reservas** por Academia Horizonte y por la actividad elegida. | Aparece el mismo código con estado **Reservado**. |
| 4. Familia | Vuelve a **Mis reservas**, cancela esa reserva y confirma. | Aparece **Cancelado**. En **Mis Sparks** figura la devolución y la sesión recupera el cupo. |
| 5. Proveedor y administración | Consulta de nuevo el código con ambos perfiles. | El historial muestra el mismo estado **Cancelado**. |

Para mostrar asistencia y opiniones, usa una sesión histórica de la demo.
Así puedes enseñar ese flujo sin marcar como realizada una sesión futura.

## Leer los indicadores

En **Estadísticas**, comienza con **Todo el historial** para ver el escenario
completo. Luego prueba **7 días** o elige un centro. Para comparar resultados,
usa el mismo período y centro en las pantallas que estés mostrando.

| Indicador | Cómo interpretarlo |
| --- | --- |
| Reservas del período | El filtro toma la fecha de creación de la reserva. En una base recién creada hay 53 reservas en estado **Reservado** y 7 **Cancelado**, con 26 asistencias dentro de las 53. |
| Asistencia registrada | Cuenta las reservas que el centro marcó como realizadas. Una reserva pasada sin esa marca sigue pendiente de registro. |
| Ocupación de próximos horarios | Mide cuántos cupos están ocupados respecto de la capacidad de los horarios futuros habilitados. Cambia al reservar, cancelar o agregar horarios. |
| GMV referencial reservado | Suma en CLP los importes de prueba de las reservas vigentes y realizadas. La cifra refleja el valor simulado de las operaciones. |
| Comisión estimada del modelo | Equivale al 10 % del valor referencial de las reservas con asistencia registrada. Es una estimación del prototipo. |
| Sparks | Son créditos de la demo. **Mis Sparks** muestra el saldo individual. En **Estadísticas**, los movimientos muestran créditos recargados, usados y devueltos durante el período. |

## Resolver problemas frecuentes

| Si ocurre esto… | Qué hacer |
| --- | --- |
| No abre la página | Mantén abierta la ventana de **Abrir demo defensa.cmd**. Espera el mensaje de inicio y visita [la demo de defensa](http://127.0.0.1:8002/). Si aparece un error, comparte ese mensaje con quien preparó la demo. |
| Las cuentas de defensa no ingresan | Comprueba que el navegador esté en el puerto **8002**. La demo habitual del puerto **8000** tiene sus propias cuentas. |
| La actividad publicada no aparece | Revisa que el centro esté aprobado, que la publicación esté activa y que exista una sesión futura con cupos. Quita filtros del catálogo y vuelve a buscar. |
| No ves el menú del proveedor o de administración | Comprueba la cuenta con la que ingresaste y despliega el menú lateral. |
| Faltan filas o las cifras difieren entre vistas | Limpia filtros, usa **Todo el historial** y selecciona el mismo centro y período en las vistas comparables. Las operaciones de ensayo cambian el escenario inicial. |
| Quieres repetir una grabación desde el escenario inicial | Cierra la demo con **Ctrl+C**, ejecuta **Restablecer demo defensa.cmd** en `scripts/mantenimiento/` y vuelve a abrir **Abrir demo defensa.cmd**. Se crea una base nueva y la anterior se conserva. |

Para grabar cápsulas cortas, consulta la [guía de defensa](docs/DEFENSA-DATOS.md).
