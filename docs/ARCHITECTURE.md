# Prototipo académico: alcance y aceptación

## Decisión aprobada
Django, SQLite, plantillas renderizadas en el servidor y recursos locales.
Se conserva el HTML de referencia. No se incorporan pagos, correo externo,
transferencias bancarias, publicidad externa ni datos reales de menores.

## Incrementos autorizados
1. Base: aplicación ejecutable, migraciones y portada móvil.
2. Acceso: registro, login/logout y cambio de contraseña persistentes.
3. Permisos: superadministrador, administrador de plataforma, operador de
   proveedor y cliente. Comprobar permisos en las rutas, además de la interfaz.
4. Catálogo: CRUD y filtros sobre actividades, centros, categorías y horarios.
5. Sparks: planes, membresías y libro de movimientos sin cobros reales.
6. Reservas: cupos/saldo consistentes; cancelación idempotente y validación.
7. Convenios: solicitudes y seguimiento con historial.
8. Centros y aliados: aprobación y asesorías con seguimiento.
9. Proveedores: panel propio, reputación y respuestas.
10. Finanzas/campañas: procesos persistentes explícitamente demostrativos.
11. Dashboard: agregaciones verificables y exportaciones con permisos.
12. Entrega: pruebas integrales, responsive e instrucciones reproducibles.

## Reglas y límites de demostración
- Un cliente solo consulta sus propias reservas, solicitudes y movimientos.
- El administrador de plataforma tiene acceso global al catálogo, las reservas
  y las solicitudes. Quedan reservados usuarios, permisos, asignación de
  operadores, validación de proveedores y finanzas sensibles.
- Los operadores gestionan las organizaciones asignadas y los módulos autorizados.
- Superadministradores gestionan todos los registros y permisos.
- Una migración de datos prepara los cuatro perfiles ficticios locales. Respeta
  cuentas existentes por usuario o correo. La configuración del túnel excluye
  esta carga y utiliza otra base SQLite.
- Los registros públicos de cliente y proveedor tienen rutas separadas. La
  marca de incorporación permite seguir las fichas propias, sin otorgar
  estado de personal ni permisos. La migración 0008 recupera ese acceso para
  los titulares de fichas anteriores y conserva sus credenciales.
- Saldo y cupos se actualizan dentro de una transacción y con escrituras
  condicionales para impedir saldo negativo y reservas por encima de la capacidad.
- La restricción de unicidad cubre reservas pendientes y confirmadas del mismo
  cliente y horario. El proveedor asignado confirma en un horario vigente.
  Confirmar conserva la retención original. La cancelación libera Sparks y cupo
  una vez. Solo una reserva confirmada puede pasar a completada y generar puntos.
- La migración 0009 conserva estados y reconoce los puntos de las reservas
  históricas con un débito registrado. La síntesis de los diagramas está en
  [Flujos Bizagi](FLOWS-BIZAGI.md).
- Se protege el historial mediante desactivación y relaciones protegidas.
- Los planes son activaciones académicas sin pasarela de pago.
- Impresiones/clics/ROAS no se inventan como resultados reales.
- SQLite es para una demostración local de baja concurrencia; no se declara
  aptitud productiva ni aislamiento de un servicio comercial multiempresa.

## Comprobación
Pruebas Django de formularios, permisos, operaciones y agregaciones, migraciones
sobre base vacía, comprobaciones del framework y revisión visual si el navegador
está disponible. Registrar las verificaciones no ejecutadas sin darlas por aprobadas.
