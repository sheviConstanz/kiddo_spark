# Base de demostración para la defensa

## Alcance y aceptación

La entrega incorpora datos relacionados mediante una migración Django, sin
cambiar pantallas ni funciones del portal. La base de trabajo anterior se
conserva. No se copian perfiles, datos de menores ni registros personales.

- Base independiente con 8 proveedores aprobados y 3 fichas en seguimiento,
  20 actividades publicadas, 30 familias, 60 reservas y 15 opiniones.
- Cuatro comunas piloto, disciplinas, edades 5–14, precios referenciales y
  Sparks variados. Un proveedor tiene cuatro talleres con diferente demanda.
- Sesiones futuras durante 35 días desde la preparación, renovables sin mover
  reservas ni reabrir horarios cancelados; disponibilidad nunca negativa.
- Historial distribuido entre meses, reservas futuras, asistencia, cancelación
  por familia y por centro, movimientos de Sparks y solicitudes B2B.
- Coincidencia entre los registros de familia, proveedor, administración y sus
  indicadores actuales. Opiniones solo de reservas con asistencia y etiqueta demo.
- Preparación repetible y restablecimiento creando otra base, sin borrar ni
  reemplazar archivos anteriores. Pruebas de migración, saldos, cupos, fechas,
  permisos, idempotencia y separación de la base normal.

## Límites acordes al alcance

Todos los datos y valores son ficticios. No hay cobros ni notificaciones externas.
Los Sparks no tienen conversión monetaria. Los perfiles de menores, intereses,
recomendaciones personalizadas y registro explícito de inasistencia no existen
en los modelos actuales. Se conserva la navegación existente y se preparan
favoritos, historial y próximas reservas de una cuenta adulta ficticia. Un
horario pasado sin asistencia registrada no se presenta como una falta confirmada.
No se agrega un módulo de incidencias ni nuevos KPI para aparentar esas funciones.

## Abrir y preparar en Windows

1. Haz doble clic en **Abrir demo defensa.cmd**. Prepara su propia base y abre
   `http://127.0.0.1:8002/`. Mantén abierta su ventana; para apagarla pulsa Ctrl+C.
2. Usa los accesos de la tabla siguiente para grabar los tres perfiles.
3. Cada vez que abras esta demo, se conservan las operaciones y se añaden los
   horarios que falten para cubrir los próximos 35 días. No se modifican fechas,
   cupos ni cancelaciones de sesiones existentes.

En [scripts/mantenimiento](../scripts/mantenimiento/README.md), **Preparar demo
defensa.cmd** renueva la agenda con el servidor apagado. **Restablecer demo
defensa.cmd** crea y selecciona otra base con el escenario inicial y conserva
la anterior. Cierra la ventana de defensa con **Ctrl+C** antes de ejecutar
cualquiera de estas herramientas. La demo habitual puede seguir funcionando
en el puerto 8000 con su propia base.

Repetir la preparación no duplica proveedores, familias, reservas ni opiniones.
Las altas y cambios que hagas durante la grabación sí cambian los totales. Usa
Restablecer para volver a los valores iniciales sin borrar el historial anterior.
No hay que copiar ni borrar la base normal, ni descargar paquetes nuevos si ya
estaba instalado Kiddo Spark.

## Accesos públicos ficticios

Todas estas cuentas usan la contraseña **`DemoAcademica2026!`**. Solo sirven
para esta base local de presentación y no deben reutilizarse en otros sistemas.

| Cuenta | Uso |
| --- | --- |
| `defensa_admin` | Estadísticas, solicitudes, proveedores y reservas de la plataforma |
| `defensa_superadmin` | Usuarios y permisos de la base de defensa |
| `defensa_proveedor_01` | Academia Horizonte: cuatro talleres, 28 reservas, asistencia, cancelaciones y opiniones |
| `defensa_proveedor_02` a `defensa_proveedor_08` | Otros siete centros aprobados de las comunas piloto |
| `defensa_proveedor_09` | Ficha recibida, sin publicar |
| `defensa_proveedor_10` | Ficha en revisión, sin publicar |
| `defensa_proveedor_11` | Ficha observada, puede corregir y reenviar |
| `defensa_familia_01` | Cuenta recomendada para el video: historial, próxima reserva, favoritos y Sparks |
| `defensa_familia_02` a `defensa_familia_30` | Otras familias adultas ficticias con reservas y saldo |

Los correos terminan en `defense.example.invalid`. No existen contactos reales
ni cuentas de menores. Las credenciales y operaciones anteriores de la demo
normal se mantienen en su archivo original.

## Inventario inicial y coherencia

| Registros | Cantidad |
| --- | ---: |
| Proveedores aprobados / fichas en seguimiento | 8 / 3 |
| Actividades publicadas | 20 |
| Familias adultas ficticias | 30 |
| Reservas totales | 60 |
| Reservas con asistencia registrada | 26 |
| Reservas futuras vigentes | 23 |
| Reservas pasadas sin asistencia registrada | 4 |
| Reservas canceladas | 7: cuatro por familia, tres por centro |
| Opiniones de demostración | 15, con notas de 3, 4 y 5 |
| Solicitudes B2B | 6: tres pendientes, una en revisión, una aprobada y una completada |
| Sesiones futuras | 300: quince por actividad, en días y horas variados |
| Sesiones históricas | 37 |

En el modelo existente, Reservado incluye las reservas con asistencia: son
53 Reservado y 7 Cancelado. No se suman las 26 asistencias una segunda vez.
Las cuatro pasadas sin registro no acreditan inasistencia. Las 15 opiniones
pertenecen exclusivamente a reservas realizadas y se muestran como Demostración.

Cada familia recibe una recarga inicial de 100 créditos simulados. Los descuentos
y devoluciones corresponden a sus reservas; el saldo coincide con la suma de
movimientos. Los puntos se asignan solo a asistencias. Las liquidaciones conservan
el importe referencial de esas mismas reservas, conforme al comportamiento actual.

El primer proveedor tiene cuatro talleres con 12, 8, 5 y 3 reservas. Los otros
dieciséis talleres tienen dos cada uno. La suma por proveedor es 60. Las reservas
históricas tienen fechas de creación, sesión, cancelación, asistencia y opinión
en orden, repartidas en varios meses. Los filtros cambian los gráficos y totales
desde esos registros; no se insertan números en las tarjetas.

La agenda tiene capacidad real disponible para la demostración; la ocupación
resultante puede ser baja al ofrecer un mes entero con solo 60 reservas. No se
rellena ese indicador con porcentajes inventados. Precios CLP y Sparks son
referencias independientes, no una tasa de cambio ni cobros comerciales.

En la preparación del 23/11/2026, los horarios con cupos llegan hasta el
**28/12/2026**. Las preparaciones posteriores extienden ese límite hasta 35 días
desde la nueva fecha, sin mover los horarios de las reservas anteriores.

## Videos de 30–60 segundos

- **Administración:** entra como `defensa_admin`, muestra Estadísticas, las
  reservas por comuna y las solicitudes. Compara un filtro de 7 días con todo
  el historial; selecciona Academia Horizonte para ver sus mismos registros.
- **Proveedor:** entra como `defensa_proveedor_01`, muestra evolución, mapa de
  demanda y comparación de los cuatro talleres. Abre Reservas y Reputación
  para enseñar operaciones, asistencia y notas de familias distintas.
- **Familia:** entra como `defensa_familia_01`, muestra próximas reservas,
  favoritos y movimientos de Sparks. Explora catálogo/mapa y reserva un horario
  libre. Anota su KS-ID para comprobarlo también en proveedor y administración.

Para mostrar niveles de demanda distintos, filtra el Seller Center por taller.
La oferta se distribuye entre las cuatro comunas: seis actividades en Viña del
Mar, cinco en Valparaíso, cinco en Quilpué y cuatro en Villa Alemana.

## Implementación y límites técnicos

La migración **0013_defense_demo_data** usa modelos históricos y un generador
versionado en `core/migrations/_defense_seed_v1.py`. Solo carga con las opciones
de `kiddo.defense_settings`. En configuración normal o de túnel, aplicar 0013
registra la migración sin introducir estos datos. No modifica migraciones previas.
La reversión de 0013 conserva las operaciones ficticias; para empezar de cero se
crea otra base, sin borrado automático.

Los archivos viven en `var/defense_data/`, fuera de Git. `current.json` selecciona
el archivo; las bases nuevas tienen nombres únicos. La base normal sigue siendo
`var/kiddo.sqlite3`. Los iniciadores no importan el catálogo antiguo ni el escenario
pequeño, para conservar los totales propios de esta entrega. El esquema y las
pantallas existentes no cambian. Las colisiones de cuenta abortan la migración
completa, sin reemplazar cuentas ni dejar una carga parcial.

Comandos equivalentes, usando el Python y paquetes preparados por los iniciadores:

```text
python -E -B scripts/defense_demo.py --prepare-only
python -E -B scripts/defense_demo.py
python -E -B scripts/defense_demo.py --fresh --prepare-only
```

El comando Django `refresh_defense_demo --settings=kiddo.defense_settings`
renueva la agenda después de aplicar `migrate` con esa misma configuración.
Está bloqueado en la configuración normal. No borra ni reactiva sesiones.

## Verificación ejecutada

- **110/110 pruebas Django PASS**, incluidas migración real 0012 → 0013,
  desactivación de la carga en la configuración normal, cuentas preservadas,
  rechazo de colisiones, saldos, cupos, cronología, opiniones y renovación de
  agenda simulando una preparación 40 días después.
- **9/9 pruebas de iniciadores PASS**, incluidas las tres nuevas de selección
  de base, conservación del archivo anterior y preparación fallida sin cambiar
  la base seleccionada. **9/9 verificaciones de integridad PASS**, con el hash
  histórico del HTML de referencia conservado.
- `check` para la configuración de defensa y `makemigrations --check --dry-run`
  sin incidencias ni cambios de esquema pendientes. Sin nuevas dependencias.
- Preparación real de la base de defensa, restablecimiento a otro archivo y
  repetición de la preparación: **PASS**. Permanecen dos archivos independientes;
  la base normal no se ha sustituido ni cargado con estos datos.
- Auditoría de la base preparada: 20 actividades, 30 familias, 60 reservas,
  26 asistencias, 23 reservas futuras, cuatro pasadas sin asistencia, siete
  cancelaciones, 15 opiniones, 300 sesiones futuras y 37 históricas. La suma
  de saldos es **2774 Sparks**, igual al saldo neto de movimientos.
- **Chrome por HTTP local aislado PASS:** administración y proveedor con
  gráficos poblados, reputación, inicio familiar, catálogo y mapa; comprobados
  a 1366, 390 y 320 px (reputación a 1366 y 390). Sin desbordamiento general ni
  imágenes rotas. Se inspeccionaron capturas representativas.
- Recorrido Chrome de reserva nueva en la base poblada, mismo KS-ID en tres
  perfiles, proveedor ajeno excluido y cancelación con devolución de cupo:
  **PASS**. Esa prueba usa una base temporal y no suma reservas a la entrega.

Otros navegadores, dispositivos físicos, túnel y despliegue: **NOT RUN**.
La aceptación de los videos corresponde al equipo académico. Las bases,
capturas y registros de prueba están fuera de Git.
