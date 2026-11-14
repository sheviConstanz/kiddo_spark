# Prototipo académico: alcance y aceptación

## Decisión aprobada
Django, SQLite, plantillas renderizadas en el servidor y recursos locales.
Se conserva el HTML de referencia. No se incorporan pagos, correo externo,
transferencias bancarias, publicidad externa ni datos reales de menores.

## Incrementos autorizados
1. Base: aplicación ejecutable, migraciones y portada móvil.
2. Acceso: registro, login/logout y cambio de contraseña persistentes.
3. Permisos: superadministrador, administradores asignados y usuario común;
   comprobar prohibiciones por URL, no solamente ocultar botones.
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
- Un usuario común solo consulta sus reservas, solicitudes y movimientos.
- Administradores gestionan organizaciones asignadas y módulos autorizados.
- Superadministradores gestionan todos los registros y permisos.
- Registro público siempre crea usuarios comunes; nunca concede privilegios.
- Saldo y cupos se actualizan dentro de una transacción y con escrituras
  condicionales para impedir saldo negativo y reservas por encima de la capacidad.
- Cancelar devuelve Sparks y cupos solo una vez; conserva historial.
- Se protege el historial mediante desactivación y relaciones protegidas.
- Los planes son activaciones académicas sin pasarela de pago.
- Impresiones/clics/ROAS no se inventan como resultados reales.
- SQLite es para una demostración local de baja concurrencia; no se declara
  aptitud productiva ni aislamiento de un servicio comercial multiempresa.

## Comprobación
Pruebas Django de formularios, permisos, operaciones y agregaciones, migraciones
sobre base vacía, comprobaciones del framework y revisión visual si el navegador
está disponible. Registrar las verificaciones no ejecutadas sin darlas por aprobadas.
