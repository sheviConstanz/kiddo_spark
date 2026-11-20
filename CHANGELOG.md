# Historial de cambios

## 2026-11-20 — Navegación y gráficos de operación

- Los enlaces principales quedan a la vista en todos los tamaños. El menú de
  cuenta aparece al entrar a **Mi panel** y sus secciones.
- **Estadísticas** incluye gráficos de reservas por fecha, comuna y estado,
  solicitudes por estado, ocupación de próximos cupos y actividades más
  reservadas. Añade filtros rápidos de 7 y 30 días.
- El README y la guía de presentación explican cómo mostrar e interpretar
  cada indicador.

## 2026-11-20 — Estadísticas para administración de plataforma

- Acceso a **Estadísticas** para `admin` y `superadmin`, con cifras
  agrupadas del catálogo, reservas y solicitudes y filtro por fecha.

## 2026-11-20 — Alivios B2B para proveedores

- Página dedicada con diagnóstico, cinco áreas de apoyo y fichas de los ocho
  aliados de ejemplo de la referencia, con filtros por área.
- Solicitudes de orientación, asesoría y cotización con preferencias de fecha,
  hora, comuna y canal, más seguimiento desde el apartado.
- Migración que completa las fichas de ejemplo existentes sin alterar solicitudes
  previas. El README y la guía comercial incluyen el recorrido.

## 2026-11-20 — Cuatro cuentas listas para la demo local

- Migración de datos para superadministración, administración de plataforma,
  familia y proveedor. Preserva las cuentas existentes y excluye la demo remota.
- El administrador de plataforma puede editar el catálogo y gestionar solicitudes
  y reservas. Usuarios, permisos, validación de proveedores y finanzas quedan
  fuera de ese rol.
- Instalación sin preguntas de creación de usuario. Credenciales de prueba y
  recorrido por perfil documentados para el equipo.

## 2026-11-19 — Arranque local con doble clic

- **Abrir Kiddo Spark.cmd** prepara una instalación nueva y abre la demo en
  el navegador sin ejecutar scripts de PowerShell.
- README y guía comercial actualizados con el recorrido desde el Explorador.

## 2026-11-19 — Mapa y filtros del catálogo

- Mapa referencial de las comunas piloto conectado con el listado y sus filtros.
- Filtros por rango de edad, franja horaria y disponibilidad. Las tarjetas
  muestran cupos, próximo horario con cupos y acceso a favoritos.
- El catálogo inicial de una instalación nueva incluye horarios de ejemplo en
  las tres franjas. Los horarios guardados conservan su configuración.

## 2026-11-19 — Demo remota privada y opcional

- `compartir_local.ps1` prepara un enlace temporal de Microsoft Dev Tunnels
  para una copia de la demo con una base independiente y puerto local 8001.
- README técnico y guía comercial explican instalación, acceso y cierre.

- Los scripts de instalación y arranque ahora se llaman `instalar_local.ps1` e
  `iniciar_local.ps1`, con guion bajo para ejecutarlos desde PowerShell.

## 2026-11-19 — Instalación separada del encendido local

- `instalar local.ps1` prepara el equipo y carga el catálogo inicial.
- `iniciar local.ps1` aplica las migraciones al encender y ofrece apagar el
  servidor local desde el mismo archivo.

## 2026-11-19 — Inicio local desde un solo archivo

- `iniciar local.ps1` prepara la base y el catálogo y arranca la demo en el
  equipo. En la primera ejecución solicita permiso para descargar dependencias
  si faltan y ofrece crear la cuenta de superadministración.

## 2026-11-19 — Portada, navegación y presentación a jefatura

- Portada con oferta piloto, recorridos por público, encuesta y objetivos, y
  vista previa de convenios identificada como simulación.
- Navegación, catálogo y paneles de familias y proveedores reorganizados con
  iconos locales y acceso directo a sus tareas principales.
- Guía no técnica para presentar y probar el prototipo en un solo computador.

## 2026-11-19 — Incorporación y validación de proveedores

- Portal de proveedores con alta de centros en las cuatro comunas piloto,
  seguimiento privado de la ficha y reenvío tras observaciones.
- Cola de superadministración con inicio de revisión, observación, rechazo y
  aprobación. Cada decisión registra actor, fecha y motivo.
- El catálogo y la reserva dependen de la habilitación del centro. La asignación
  de permisos de operación se realiza por separado.
- Inicio con acceso directo al catálogo y al portal de proveedores. Los nuevos
  formularios y estados usan la identidad del proyecto y una distribución adaptable.

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
