# Funciones del prototipo

Este documento distingue comportamiento implementado de afirmaciones comerciales
o ideas del material original. No se presupone un negocio operativo.

| Área | Implementación funcional | Límite de demostración |
| --- | --- | --- |
| Cuenta | Registro, login/logout, cambio de contraseña, edición de nombre | Sin envío de email; recuperación mediante responsable local |
| Permisos | Superadministración, administrador de plataforma, operador de proveedor y cuenta familiar | La migración crea cuatro cuentas ficticias para uso local. El administrador de plataforma no accede a usuarios, permisos, validación de proveedores ni finanzas |
| Exploración | Mapa referencial por comuna, búsqueda, categoría, edad, horario, Sparks, cupos y favoritos persistentes | El mapa agrupa por comuna. No muestra coordenadas ni direcciones de los centros |
| Actividades | CRUD, rangos de edad, proveedor, categoría, valor y estado | Sin verificación externa de academias |
| Horarios | Fecha, capacidad, cupos y disponibilidad | Datos iniciales ilustrativos, renovados por administrador |
| Planes | CRUD y activaciones registradas | Recargas manuales demo; sin pagos ni renovación automática |
| Sparks | Libro de movimientos y saldo por usuario | No existe moneda ni valor económico real |
| Puntos | 50 por reserva y reversión al cancelar | Sin recompensas ni canjes acordados |
| Reservas | Control de cupos/saldo, cancelación una sola vez, comprobantes y CSV | No se envían avisos externos |
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
| Navegación | Menú público siempre visible, enlaces de cuenta dentro de Mi panel | La propuesta original se abre como una página independiente |
| Móvil | Menú principal en varias filas, rejillas y formularios adaptables y tablas desplazables | Navegación y Estadísticas verificadas en Chrome |

## Flujos y decisiones
- Alta pública siempre como usuario común. Los administradores se conceden desde
  superadministración. Los operadores de proveedor requieren permisos y centro
  asignado. Las cuentas ficticias preconfiguradas se reservan a la demo local.
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
- En Estadísticas, el filtro usa fechas inclusivas de creación. Las reservas
  canceladas se incluyen en el total y en la distribución por estado, y se
  excluyen del gráfico diario y los rankings. La ocupación considera horarios
  activos y futuros de actividades publicadas de centros activos y aprobados.

## Verificación pendiente
La generación de páginas y recursos se probó por HTTP y mediante el cliente de
pruebas Django. La navegación visual, comparación de diseño y usabilidad móvil
necesitan revisión humana; no se declaran aprobadas por comprobar solo el HTML.
El túnel de VS Code debe probarse con el dominio concreto de la presentación.
