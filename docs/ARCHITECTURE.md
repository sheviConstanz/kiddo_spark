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
- El administrador de plataforma tiene acceso global al catálogo, reservas,
  solicitudes y revisión de proveedores. Aprobar asigna exclusivamente al titular
  a su centro y le concede permisos de operador. Usuarios, permisos generales,
  operadores adicionales y finanzas sensibles quedan en superadministración.
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
- La reserva toma el cupo y descuenta Sparks en la misma transacción. El
  identificador del cliente y del horario es único entre reservas vigentes
  con asistencia pendiente. Registrar asistencia acredita los puntos por separado.
- La cancelación del horario toma el mismo registro, valida el permiso y un
  mínimo de 48 horas, y guarda el motivo. Devoluciones y notificaciones se
  confirman en la misma transacción. Las notificaciones se filtran por la cuenta
  que las recibe y se marcan como leídas por POST.
- La migración 0010 sustituye la aprobación manual y conserva la asistencia
  histórica y los movimientos. La síntesis de los diagramas está en
  [Flujos Bizagi](FLOWS-BIZAGI.md).
- Se protege el historial mediante desactivación y relaciones protegidas.
- Los planes son activaciones académicas sin pasarela de pago.
- La migración 0012 agrega estados explícitos de publicación, modalidad, lugar,
  imagen y marcadores de demostración; convierte actividades inactivas a Pausada
  y conserva saldos e historial. Los nuevos formularios limitan edades a 5–14.
- El catálogo exige publicación y disponibilidad futura. Las imágenes se sirven
  por ID de actividad, respetando publicación o gestión del centro. No se publica
  el directorio de archivos subidos. Se aceptan PNG/JPEG de hasta 3 MB.
- La semilla de escenario es optativa, transaccional e idempotente. Su marcador
  evita duplicar o reemplazar operaciones humanas; las colisiones de cuenta
  abortan la carga. La configuración de túnel impide esta carga con contraseñas.
- El GMV referencial y una comisión estimada se agregan desde reservas con los
  mismos filtros. Los supuestos financieros y metas se presentan por separado;
  no se introducen cobros, membresías B2B facturadas ni conversión Spark/CLP.
- Impresiones/clics/ROAS no se inventan como resultados reales.
- SQLite es para una demostración local de baja concurrencia; no se declara
  aptitud productiva ni aislamiento de un servicio comercial multiempresa.

## Comprobación
Pruebas Django de formularios, permisos, operaciones y agregaciones, migraciones
sobre base vacía, comprobaciones del framework y revisión visual si el navegador
está disponible. Registrar las verificaciones no ejecutadas sin darlas por aprobadas.
