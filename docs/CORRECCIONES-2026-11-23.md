# Correcciones de incorporación y demostración — 23 de noviembre de 2026

## Alcance autorizado

Implementar las seis observaciones de Entrega 01 sobre el prototipo Django
existente. Conservar el HTML y CSS de referencia. El usuario autorizó completar,
probar, documentar, crear commit y hacer push; no se autoriza un despliegue ni
operaciones comerciales. Los documentos privados de continuidad no se publican.

## Plan y aceptación

1. **Incorporación:** administración y superadministración revisan la misma
   ficha y registran motivo, responsable y fecha. Aprobar habilita al solicitante
   como operador exclusivamente de su centro, sin permisos globales. Pendientes,
   observados y rechazados no publican. Repetir una decisión no duplica eventos.
2. **Oferta:** el proveedor crea, edita y pausa actividades propias con estados
   explícitos, edades 5–14, modalidad, lugar y una imagen opcional. Puede crear
   varias sesiones futuras con capacidad positiva y disponibilidad calculada.
   El catálogo familiar exige publicación y una sesión futura con cupos.
3. **Reservas y privacidad:** el mismo KS-ID une familia, sesión, actividad,
   proveedor y administración; una reserva unitaria ocupa un cupo y descuenta
   créditos simulados. Duplicados, saldo insuficiente y sobreventa no dejan
   efectos parciales. Comprobante con proveedor, fecha, estado y aclaración demo.
   Se conserva la cancelación con devolución, asistencia y auditoría.
4. **Datos demo:** carga optativa, idempotente, protegida por configuración demo,
   con centros y fichas en las cuatro comunas, familias ficticias, actividades en
   distintos estados, sesiones, reservas, movimientos y opiniones identificadas.
   No reemplaza registros humanos ni carga datos al abrir una página.
5. **Indicadores:** valores derivados de los mismos registros y filtros; GMV
   referencial y estimación de comisión separados. Membresía B2B de $35.000 netos,
   comisión 10%, ticket $25.000, metas M12 (8 proveedores, 150 familias) y 499
   reservas año 1 se identifican como supuestos/proyecciones, nunca ingresos,
   pagadores o reservas efectivas. No se define conversión Spark/CLP.
6. **Verificación:** pruebas de alta → revisión → publicación → búsqueda →
   reserva → consulta en tres perfiles → cancelación, con segundo proveedor
   excluido; idempotencia de semilla, filtros, auditoría, migración e integridad.

## Decisiones de implementación

- Administración de plataforma puede resolver altas; usuarios, roles generales
  y acceso a superadministración siguen reservados a superadministración.
- Se conserva la etapa «En revisión» antes de resolver. No se agrega una segunda
  revisión de actividades, que el documento plantea como opcional.
- La aprobación habilita la operación del centro; el proveedor decide publicar
  sus actividades. Una ficha aprobada no crea actividades automáticamente.
- Una reserva sigue teniendo los estados Reservado/Cancelado y asistencia aparte;
  «completada» en la demo significa asistencia registrada.
- No se implementa pasarela bancaria: falta de Sparks simula un rechazo sin
  consumir cupo; activación de planes es una recarga ficticia.
- Los saldos e historial anteriores se conservan. Los datos de presentación
  permanecen fuera de Git y se crean solo mediante una acción explícita.

## Riesgos y límites

Las cuentas locales son ficticias y la aplicación no está certificada para
producción. Una revisión estática no demuestra el estado de las capturas o de
la base de otro equipo. La comprobación visual y móvil se registra por separado
de las pruebas del servidor. Las fuentes comerciales del modelo se toman del
documento suministrado, sin afirmar validación de la tesis.

## Resultados

| Observación | Resultado de esta entrega |
| --- | --- |
| INC-01 | Cola para administración y superadministración, recibidas/en revisión juntas por defecto, decisiones e historial, estados de cuenta/ficha/operación separados. |
| INC-02 | Aprobación habilita al titular, recuperación de aprobadas anteriores, oferta propia con estados, modalidad, lugar, imagen, varias sesiones y catálogo condicionado a cupos. |
| INC-03 | Persistencia entre sesiones, privacidad, comprobante completo y rechazo sin efectos parciales. Sparks y valores claramente simulados. |
| INC-04 | Reservas, cupos, avisos y asistencia del centro asignado; otro proveedor queda excluido, incluso por URL y CSV. |
| INC-05 | Consulta administrativa conservada; se comprueba el mismo código de operación entre los tres perfiles. |
| INC-06 | Semilla transaccional, optativa e idempotente, reseñas identificadas, indicadores relacionados y proyecciones financieras separadas. |

Comprobaciones ejecutadas el 23 de noviembre de 2026:

- **PASS 100/100 pruebas Django**, incluidos registro de proveedor nuevo, revisión,
  publicación, dos sesiones, reserva, reingreso, consulta en tres perfiles,
  aislamiento, cancelación, carga demo y migración 0011 → 0012 con datos históricos.
- **PASS 6/6 pruebas de iniciadores** y **9/9 verificaciones del harness**, incluida
  reconstrucción exacta del SHA-256 histórico del HTML de referencia.
- **PASS** `check`, `makemigrations --check --dry-run`, `pip check`, sintaxis
  JavaScript y revisión de espacios del diff. Sin nuevas dependencias.
- **PASS Chrome sobre HTTP local aislado**, con aprobación de ficha, creación de
  actividad con imagen, sesión, reserva y consulta del mismo KS-ID en familia,
  proveedor y administración; exclusión de otro proveedor y cancelación con
  cupos 10 → 9 → 10. Se usó un perfil Chrome temporal, sin perfiles personales.
- **PASS** dimensiones y recursos en cola, decisión de ficha, formulario de
  actividad, detalle, reservas familiares, Seller Center y Estadísticas a
  **1366, 390 y 320 px**. Se inspeccionaron capturas representativas. Se corrigió
  un desbordamiento móvil de la etiqueta accesible en la cola.
- **PASS concurrencia SQLite en archivo temporal:** dos clientes simultáneos
  para un cupo; una reserva, un movimiento de descuento y ningún sobrecupo.
- **PASS preparación local real** mediante `scripts/load_demo.py`: migración
  0012, catálogo conservado y escenario cargado. Servidor de esta carpeta
  reiniciado; login y páginas de administrador, Kids Demo y familia, y CSS,
  comprobados por HTTP en `127.0.0.1:8000`.

Otros navegadores, dispositivos físicos, túnel y despliegue: **NOT RUN**.
No se implementaron cobros, facturación ni una conversión Spark/CLP; el documento
no define esa regla y los importes se presentan como simulación y proyección.
No se modificaron el HTML ni el CSS de referencia. Capturas, bases, archivos
subidos y documentos locales de continuidad permanecen fuera de Git.
