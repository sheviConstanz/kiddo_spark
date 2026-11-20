# Indicadores de administración y proveedores

El archivo **Métricas.xlsx** contiene las hojas **Admin**, **Proveedores**,
**Copia de Supuestos** y **Métricas horizonte**. Los escenarios y cifras por
año describen metas y proyecciones. El dashboard calcula sus cifras con los
registros de la demo. Los importes son valores referenciales de las reservas.

## Qué puede medir la demo hoy

| Código del Excel | Vista de la demo | Cálculo y alcance |
| --- | --- | --- |
| PROV_CANCEL, ATT_CANCEL_RATE | Cancelaciones del período y por origen | Reservas canceladas / total de reservas. La alerta usa el umbral general del 5%. El aviso de cancelación identifica las anuladas por el centro y su motivo. Las demás incluyen cancelaciones sin origen histórico registrado. |
| PROV_HEAT | Mapa de reservas por día y hora | Reservas vigentes y realizadas por día de semana y bloque de tres horas del horario reservado. |
| PROV_BUYERS | Familias que reservan una vez o vuelven a reservar | Cuenta familias con una o más reservas vigentes o realizadas dentro del período. La recurrencia es la proporción con dos o más reservas en ese período. |
| PROV_LISTING | Rendimiento por taller | Hasta 12 talleres con movimientos. Reservas vigentes o realizadas, cancelaciones, asistencias y suma de importes referenciales. El CSV exporta todos los talleres que cumplen los filtros. |
| PROV_CAP_OCC, SELLABLE_UTIL | Ocupación de próximos horarios | Cupos ocupados / capacidad futura publicada. Este cálculo usa los cupos reales de la demo. La capacidad física declarada y las órdenes pagadas del modelo se requieren para medir los indicadores del Excel con sus fórmulas originales. |
| SAT_CLASS_CSAT | Calificación media y distribución | Promedio de las opiniones de las reservas del período, en escala de 1 a 5. |
| COST_GROSS | Valor referencial de asistencias | Suma del importe reservado de actividades con asistencia registrada. Es la aproximación disponible para operación de la demo. |
| PROV_GMV, PROV_ORDERS, PROV_ASP, PROV_UNITS | Reservas, valor total y valor medio referencial | Suma y promedio del importe de las reservas vigentes y realizadas. La demo cuenta una reserva por cupo y no registra órdenes pagadas ni cuántas sesiones incluye un pack. |
| ATT_SLA_RESP | Confirmación automática | La reserva se confirma al tomar el cupo. El tiempo de respuesta manual del proveedor deja de ser un indicador del flujo actual. |
| BIZ_CREDITS_RED | Movimientos de Sparks | Recargas, descuentos y devoluciones por fecha de movimiento. Falta registrar canje de recompensas para calcular la tasa solicitada. |
| BIZ_AUDIT_PROV | Vista por centro en Administración | El selector **Centro** en **Estadísticas** abre los mismos gráficos del Seller Center. Las consultas de un proveedor se limitan a los centros asignados. |

Las fechas del dashboard corresponden a la creación de la reserva. Con
ambos límites, el resumen compara las reservas con el período anterior de
igual duración. Los atajos cubren 7, 30 y 90 días, el mes actual y
el año actual. El gráfico de evolución muestra hasta 12 fechas con
reservas vigentes o realizadas y sus asistencias. La ocupación muestra la
capacidad futura disponible al consultar.
En la vista general de administración se suman reservas por comuna y
categoría, solicitudes por estado y el estado actual de las fichas de proveedor.

## Fuentes pendientes para las demás métricas

| Indicadores | Datos que faltan |
| --- | --- |
| PROS_REG, B2B_CHURN, B2B_CONV_ACT | Prospectos contactados, ejecutivo, región y fecha de contacto. Es necesario registrar altas, bajas y cartera al inicio para medir conversión y pérdida de proveedores. Hoy se puede observar el estado de las fichas. |
| SAAS_NEW, SAAS_RENEW, USE_NEW, USE_RENEW | Plan del proveedor, fechas de alta y renovación e historial de modalidad. |
| CPL_ELIGIBLE, LEADS_REF, CONV_B2C, ACT_FAM, RET_FAM, ORD_FREQ | Canal y elegibilidad del registro, atribución QR, inversión, primera compra pagada y reglas de cohortes y familias activas. |
| CAP_SESS_MONTH, SELLABLE | Capacidad física declarada de cada centro y proporción ofrecida en Kiddo por período. |
| FIN_NET_REV, COST_NET_PAY, COST_UNIT_MARGIN | Pagos y liquidaciones, comisiones aplicadas, costos y caja registrados. Las proyecciones del Excel se mantienen como referencia. |
| PROV_VIEWS, PROV_CONV, COMP_CAT_GROWTH, COMP_OPP_CATS | Visitas, sesiones de navegación, compras atribuibles, búsquedas sin resultados y políticas para agregados de competencia. |
| ATT_CLAIMS_RATE, SAT_PROV_NPS | Registro de reclamos y encuestas de recomendación de 0 a 10. La nota de 1 a 5 de la actividad es otro indicador. |
