# Funciones del prototipo

Este documento distingue comportamiento implementado de afirmaciones comerciales
o ideas del material original. No se presupone un negocio operativo.

| Área | Implementación funcional | Límite de demostración |
| --- | --- | --- |
| Cuenta | Registro de cliente y alta de proveedor separados, ingreso por perfil, cierre de sesión, cambio de contraseña, edición de nombre | Sin envío de email; recuperación mediante responsable local |
| Permisos | Superadministración, administrador de plataforma, proveedor, proveedor en incorporación y cliente | La migración crea cuatro cuentas ficticias para uso local. El administrador de plataforma no accede a usuarios, permisos, validación de proveedores ni finanzas |
| Exploración | Mapa referencial por comuna, búsqueda, categoría, edad, horario, Sparks, cupos y favoritos persistentes | El mapa agrupa por comuna. No muestra coordenadas ni direcciones de los centros |
| Actividades | CRUD, rangos de edad, proveedor, categoría, valor y estado | Sin verificación externa de academias |
| Horarios | Fecha, capacidad, cupos y disponibilidad | Datos iniciales ilustrativos, renovados por administrador |
| Planes | CRUD y activaciones registradas | Recargas manuales demo; sin pagos ni renovación automática |
| Sparks | Libro de movimientos y saldo por usuario | No existe moneda ni valor económico real |
| Puntos | 50 al completar una reserva nueva, una vez | La migración conserva puntos ya acreditados. Los puntos no tienen canje |
| Reservas | Confirmación automática con cupo, estados Reservado y Cancelado, asistencia por separado, comprobantes demo y CSV | Un proveedor asignado puede cancelar su horario con motivo y al menos 48 horas de anticipación |
| Notificaciones | Avisos privados al cliente por reserva y cancelación, y al proveedor asignado por una nueva reserva | Se consultan en la campanita del portal |
| Confirmaciones y avisos | Cuadros con la acción y su efecto, avisos en página para el resultado y confirmación por teclado | En el portal |
| Convenios | Solicitudes con organización, contacto y estimación de familias | Aprobación académica, sin firma contractual ni elegibilidad automática |
| Centros | Alta en comunas piloto, revisión, corrección, aprobación o rechazo e historial | Aprobación académica. Permisos asignados por separado. Documentos de validación por definir |
| Alivios B2B | Diagnóstico, filtros por área, fichas de aliados, orientación, asesorías, cotizaciones y seguimiento | Aliados de ejemplo. La fecha y el canal son preferencias y no confirman una cita |
| Seller Center | Gestiona su oferta y reservas. Muestra horarios con mayor demanda, asistencia, ocupación, cancelaciones, recurrencia, opiniones y rendimiento por taller | Cada proveedor accede a sus centros. Los montos de la demo son referenciales |
| Opiniones | Una por reserva completada y respuesta del centro | No se importan reseñas o estrellas ficticias como reales |
| Liquidaciones | Monto referencial de reservas completadas | Comisión del 10% del modelo pendiente de implementar. Sin documento tributario |
| Retiros | Solicitud, reserva de saldo, rechazo o finalización simulada | No se mueve dinero |
| Campañas | Nombre, actividad, presupuesto y estado persistentes | Sin difusión, gasto, impresiones ni ROAS externos |
| Dashboard | Reservas por fecha, agregaciones, popularidad y estado de solicitudes | No inventa visitas, conversiones ni ingresos |
| Estadísticas de plataforma | Reservas por día, comuna y categoría, solicitudes, incorporación, Sparks y vista de indicadores por centro | Para administración de plataforma y superadministración. Ver las [definiciones de métricas](METRICAS.md) |
| Gestión operativa | Abre la tabla de proveedores y da acceso a las tablas de publicaciones, horarios, categorías, comunas y planes. Lista global de reservas con filtros y CSV | Administración consulta el catálogo, administra sus datos y visualiza reservas. La validación y habilitación de proveedores y la asignación de operadores corresponden a superadministración |
| Navegación | Administración consulta **Actividades** y **Alivios B2B** desde la barra superior y abre **Notificaciones** en la campanita. El lateral reúne **Estadísticas**, **Reservas**, **Solicitudes**, tablas y cuenta en grupos plegables | Alivios B2B es de consulta para administración. El lateral filtra módulos por permisos, abre el grupo de la pantalla actual y recuerda si se plegó por completo |
| Móvil | Menú principal en varias filas, rejillas y formularios adaptables y tablas desplazables | Navegación y Estadísticas verificadas en Chrome |

## Flujos y decisiones
- El alta pública crea un cliente o un proveedor en incorporación. La segunda
  modalidad permite presentar y consultar fichas. Los operadores de proveedor
  requieren permisos y centro asignado. Las cuentas ficticias preconfiguradas
  se reservan a la demo local.
- El cliente conserva su historial de solicitudes y puede enviar convenios
  desde el recorrido público. Las demostraciones corporativas y solicitudes
  de Alivios B2B tienen controles de acceso en el servidor.
- Las solicitudes se guardan con estado e historial. Las gestionan superadministración
  y el administrador de plataforma. Los operadores autorizados pueden tramitar
  las solicitudes dirigidas a sus organizaciones asignadas. El solicitante
  ve sus propios trámites.
- Los administradores no acceden a objetos de otros centros mediante URLs directas.
- Cambios de saldo, reserva y cupo se ejecutan juntos o se revierten juntos.
- Una reserva completada no se cancela desde el portal; conserva su historial
  y habilita una opinión y una liquidación de demostración.
- Desactivar elimina el registro del uso futuro sin borrar sus operaciones anteriores.
- El HTML original reorganizado anteriormente permanece disponible como referencia
  explícitamente simulada; sus botones no escriben en la base de la plataforma.
- En Estadísticas, el filtro usa fechas inclusivas de creación. El total y la
  distribución incluyen todos los estados. El gráfico diario y los rankings
  cuentan las reservas vigentes y realizadas. La ocupación considera horarios
  activos y futuros de actividades publicadas de centros activos y aprobados.

## Verificación pendiente
La generación de páginas y recursos se probó por HTTP y mediante el cliente de
pruebas Django. La navegación visual, comparación de diseño y usabilidad móvil
necesitan revisión humana; no se declaran aprobadas por comprobar solo el HTML.
El túnel de VS Code debe probarse con el dominio concreto de la presentación.
