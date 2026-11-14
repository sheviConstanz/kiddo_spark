# Historial de cambios

## 2026-11-14 — Plataforma académica con Django y SQLite

### Implementado
- Aplicación Django con migraciones, catálogo de referencia reproducible y recursos
  locales; HTML anterior conservado como referencia independiente.
- Registro, login/logout, perfil y cambio de contraseña; roles de usuario común,
  administrador y superadministrador, con permisos y organizaciones asignadas.
- CRUD con desactivación de actividades, horarios/cupos, centros, categorías,
  comunas, planes y campañas. Aprobación de centros y administración de usuarios.
- Planes demo, historial de Sparks/puntos, favoritos, reservas, cancelaciones,
  validación de asistencia, opiniones y respuestas de proveedores.
- Convenios, demos y asesorías con contacto, fecha/hora preferida e historial de estados.
- Liquidaciones y retiros simulados, cuentas ficticias y comprobantes/CSV.
- Dashboard con estadísticas derivadas de registros, filtros temporales y reputación.
- Interfaz adaptable, navegación móvil y guía de instalación/presentación para
  usuarios no informáticos. Dependencias fijadas en requirements.txt.

### Verificado
- 42 pruebas Django aprobadas, incluyendo permisos, recorridos integrados,
  transacciones, duplicados, CSRF, exportaciones y acceso a recursos visuales.
- Migraciones aplicadas sobre base nueva; sin cambios de modelo pendientes.
- Check Django sin errores, dependencias compatibles y JavaScript con sintaxis válida.
- Seis páginas públicas y cuatro recursos locales respondieron HTTP 200 con
  servidor real. Rutas de base de datos, código y documentos privados respondieron 404.
- Nueve comprobaciones locales de integridad aprobadas; la referencia anterior
  conserva su reconstrucción exacta del hash histórico.

### Límites y decisiones explícitas
- Revisión visual de escritorio/móvil y reenvío VS Code pendientes: navegador no disponible.
- Servidor de desarrollo local; el chequeo productivo señala cuatro advertencias
  relativas a HTTPS. No hay despliegue ni pruebas de carga.
- Sin cobros, transferencias, correo externo, recuperación por email o anuncios reales.
- Cuentas nuevas comienzan sin saldo; los planes añaden recargas demo registradas.
  Se revierte una sola vez el saldo y los puntos de una reserva cancelada.
- Se unificaron catálogo, reservas y publicaciones; ya no se cruzan por IDs entre
  listas independientes como en la maqueta. No se trasladaron estadísticas inventadas.
- Los montos sin correspondencia identificable en la referencia comienzan en cero;
  no se introdujeron tasas de comisión. Se conserva historial mediante desactivación.

## 2026-11-14 — Separación de la hoja de estilos principal

### Cambios
- El bloque CSS principal se trasladó sin alterar su contenido a
  `assets/css/styles.css`; el HTML ahora lo enlaza en la misma posición.
- Se añadió una guía en español para abrir, reenviar y preparar una futura
  presentación mediante un servidor local y el reenvío de puertos de VS Code.
- Se documentó el alcance académico y el carácter simulado de las operaciones.

### Verificación y límites
- La reconstrucción del bloque original permite comprobar su SHA-256 histórico
  y detectar cambios accidentales en cualquier otra parte del HTML.
- Los estilos incrustados en etiquetas y JavaScript permanecen en su lugar.
- Se conserva la dependencia de Tailwind por Internet.
- La comparación visual y las interacciones no están verificadas: el navegador
  integrado no estuvo disponible. El servidor y el reenvío tampoco se ejecutaron.
- Sin backend, base de datos, autenticación real ni integraciones comerciales.
