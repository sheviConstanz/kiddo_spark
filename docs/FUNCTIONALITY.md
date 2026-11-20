# Funciones del prototipo

Este documento distingue comportamiento implementado de afirmaciones comerciales
o ideas del material original. No se presupone un negocio operativo.

| Área | Implementación funcional | Límite de demostración |
| --- | --- | --- |
| Cuenta | Registro, login/logout, cambio de contraseña, edición de nombre | Sin envío de email; recuperación mediante responsable local |
| Permisos | Tres roles; grupos y asignación de organizaciones | No es una certificación de seguridad productiva |
| Exploración | Catálogo persistente, búsqueda, comuna, categoría, edad, Sparks y favoritos | Sin geolocalización ni mapa cartográfico real |
| Actividades | CRUD, rangos de edad, proveedor, categoría, valor y estado | Sin verificación externa de academias |
| Horarios | Fecha, capacidad, cupos y disponibilidad | Datos iniciales ilustrativos, renovados por administrador |
| Planes | CRUD y activaciones registradas | Recargas manuales demo; sin pagos ni renovación automática |
| Sparks | Libro de movimientos y saldo por usuario | No existe moneda ni valor económico real |
| Puntos | 50 por reserva y reversión al cancelar | Sin recompensas ni canjes acordados |
| Reservas | Control de cupos/saldo, cancelación una sola vez, comprobantes y CSV | No se envían avisos externos |
| Convenios | Solicitudes con organización, contacto y estimación de familias | Aprobación académica, sin firma contractual ni elegibilidad automática |
| Centros | Alta en comunas piloto, revisión, corrección, aprobación o rechazo e historial | Aprobación académica. Permisos asignados por separado. Documentos de validación por definir |
| Aliados | Directorio, asesorías/cotizaciones y seguimiento | No agenda llamadas en un calendario externo |
| Seller Center | CRUD, órdenes, validación, finanzas y reputación del centro asignado | No se conserva la duplicidad de listas e IDs de la maqueta |
| Opiniones | Una por reserva completada y respuesta del centro | No se importan reseñas o estrellas ficticias como reales |
| Liquidaciones | Monto referencial de reservas completadas | Comisión del 10% del modelo pendiente de implementar. Sin documento tributario |
| Retiros | Solicitud, reserva de saldo, rechazo o finalización simulada | No se mueve dinero |
| Campañas | Nombre, actividad, presupuesto y estado persistentes | Sin difusión, gasto, impresiones ni ROAS externos |
| Dashboard | Reservas por fecha, agregaciones, popularidad y estado de solicitudes | No inventa visitas, conversiones ni ingresos |
| Móvil | Menú, rejillas y formularios adaptables; tablas desplazables | Revisión visual pendiente por navegador no disponible |

## Flujos y decisiones
- Alta pública siempre como usuario común. Los administradores se conceden desde
  superadministración con permisos y centro asignado.
- Solicitudes corporativas generales: superadministración. Solicitudes a aliados:
  administradores asignados al aliado y superadministración. El solicitante sigue su historial.
- Los administradores no acceden a objetos de otros centros mediante URLs directas.
- Cambios de saldo, reserva y cupo se ejecutan juntos o se revierten juntos.
- Una reserva completada no se cancela desde el portal; conserva su historial
  y habilita una opinión y una liquidación de demostración.
- Desactivar elimina el registro del uso futuro sin borrar sus operaciones anteriores.
- El HTML original reorganizado anteriormente permanece disponible como referencia
  explícitamente simulada; sus botones no escriben en la base de la plataforma.

## Verificación pendiente
La generación de páginas y recursos se probó por HTTP y mediante el cliente de
pruebas Django. La navegación visual, comparación de diseño y usabilidad móvil
necesitan revisión humana; no se declaran aprobadas por comprobar solo el HTML.
El túnel de VS Code debe probarse con el dominio concreto de la presentación.
