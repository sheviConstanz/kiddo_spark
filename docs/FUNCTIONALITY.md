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
| Reservas | Solicitud con cupo y Sparks apartados, confirmación del proveedor asignado, cancelación una vez, comprobantes demo y CSV | El estado se consulta en el portal. Quedan pendientes los avisos externos y la liberación automática |
| Convenios | Solicitudes con organización, contacto y estimación de familias | Aprobación académica, sin firma contractual ni elegibilidad automática |
| Centros | Alta en comunas piloto, revisión, corrección, aprobación o rechazo e historial | Aprobación académica. Permisos asignados por separado. Documentos de validación por definir |
| Alivios B2B | Diagnóstico, filtros por área, fichas de aliados, orientación, asesorías, cotizaciones y seguimiento | Aliados de ejemplo. La fecha y el canal son preferencias y no confirman una cita |
| Seller Center | CRUD, órdenes, validación, finanzas y reputación del centro asignado | No se conserva la duplicidad de listas e IDs de la maqueta |
| Opiniones | Una por reserva completada y respuesta del centro | No se importan reseñas o estrellas ficticias como reales |
| Liquidaciones | Monto referencial de reservas completadas | Comisión del 10% del modelo pendiente de implementar. Sin documento tributario |
| Retiros | Solicitud, reserva de saldo, rechazo o finalización simulada | No se mueve dinero |
| Campañas | Nombre, actividad, presupuesto y estado persistentes | Sin difusión, gasto, impresiones ni ROAS externos |
| Dashboard | Reservas por fecha, agregaciones, popularidad y estado de solicitudes | No inventa visitas, conversiones ni ingresos |
| Estadísticas de plataforma | Reservas y solicitudes por período, gráficos de estados, reservas por día y comuna, actividades más reservadas y ocupación futura | Para administración de plataforma y superadministración. Las cifras son agrupadas. El catálogo y sus próximos cupos reflejan el estado actual |
| Navegación | Portada pública, inicio de cliente con próximas reservas, Seller Center de proveedor, Estadísticas para administración y panel de superadministración | La propuesta original se abre como una página independiente |
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
  cuentan las confirmadas y completadas. La ocupación incluye los cupos
  apartados por solicitudes pendientes y considera horarios
  activos y futuros de actividades publicadas de centros activos y aprobados.

## Verificación pendiente
La generación de páginas y recursos se probó por HTTP y mediante el cliente de
pruebas Django. La navegación visual, comparación de diseño y usabilidad móvil
necesitan revisión humana; no se declaran aprobadas por comprobar solo el HTML.
El túnel de VS Code debe probarse con el dominio concreto de la presentación.
