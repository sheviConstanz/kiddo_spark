# Demostración B2B → B2C

## Preparar los datos desde Windows

1. Apaga Kiddo Spark antes de actualizar la carpeta.
2. En [scripts/mantenimiento](../scripts/mantenimiento/README.md), abre
   **Cargar datos demo.cmd** y espera el mensaje de resultado.
3. En esa misma carpeta, abre **Abrir Kiddo Spark.cmd**.

La carga conserva datos anteriores. Al repetirla, no duplica el escenario ni
restablece contraseñas, fechas o ediciones. Si un nombre de cuenta ya existe,
la carga del escenario se revierte con un mensaje; no reemplaza esa cuenta.
No borres la base para resolverlo: prepara otra copia local para la presentación.
El catálogo original y las operaciones del escenario son cargas separadas.

El comando equivalente es `python manage.py seed_demo --scenario`, después de
aplicar `python manage.py migrate`. Usa el Python y los paquetes preparados por
el instalador. La opción solo funciona con `KIDDO_ALLOW_DEMO_DATA=True` y
`KIDDO_SEED_DEMO_ACCOUNTS=True`; la configuración de túnel las deshabilita.
No se ejecuta automáticamente al abrir una página ni forma parte de un despliegue.

## Accesos ficticios del escenario

Las cuentas de esta tabla usan la contraseña **`DemoAcademica2026!`**.
Es pública, solo para esta demostración local. No reutilizarla en cuentas reales.

| Cuenta | Ficha o función |
| --- | --- |
| `kidsdemo` | Kids Demo, Viña del Mar: aprobada, con actividades y reservas |
| `robotica_demo` | Robótica Demo, Valparaíso: aprobada, con actividades y reservas |
| `deporte_demo` | Deporte Demo, Quilpué: solicitud recibida, sin acceso a publicar |
| `arte_demo` | Arte Demo, Villa Alemana: observada, puede corregir y reenviar |
| `familia_demo_001` a `familia_demo_004` | Adultos ficticios, movimientos de créditos y reservas |

Administración conserva sus accesos locales habituales: `admin` / `admin` y
`superadmin` / `superadmin`, si no fueron cambiados. No se restablecen.
Los correos terminan en `example.invalid`; no se envía correo ni se guardan
nombres, documentos o edades individuales de menores.

## Qué queda cargado

- Cuatro fichas en las cuatro comunas piloto: dos aprobadas, una recibida y
  otra observada. La revisión conserva responsable, motivo y fecha.
- Seis actividades propias de los dos proveedores aprobados: dos publicadas,
  dos borradores y dos pausadas. Solo las publicadas con cupos futuros se
  muestran en el catálogo de familias.
- Seis sesiones: cuatro futuras y dos históricas. Doce reservas unitarias:
  diez vigentes o realizadas, de las cuales cuatro tienen asistencia, y dos
  canceladas. Las cancelaciones devuelven sus Sparks y cupos.
- Cuatro recargas de 80 créditos simulados, movimientos de reserva/devolución
  y cuatro opiniones vinculadas a asistencia, rotuladas **Demostración**.

En una carga sin otras operaciones, los paneles de los dos proveedores suman
12 reservas, igual que administración. El GMV referencial vigente/realizado
es $250.000 y la estimación de comisión sobre asistencias es $10.000. Son el
resultado de estos registros ficticios, no ingresos ni las metas de la tesis.
Otros registros de la carpeta pueden aumentar el total de administración.

Las sesiones futuras se crean relativas al día de carga. Repetir no mueve las
fechas de reservas existentes. Si se vencen, agrega nuevas sesiones desde el
Seller Center; no se alteran citas históricas para mantener el catálogo lleno.

## Recorrido completo con una ficha nueva

1. Desde la portada, crea una cuenta de proveedor y registra un centro con
   datos ficticios. Aparece **Solicitud recibida**, todavía sin habilitación.
2. Ingresa como `admin`. En **Operación → Solicitudes de proveedores** abre
   esa misma ficha. Registra **En revisión** y luego **Aprobada**, con motivo.
   También puedes observar o rechazar; una ficha observada admite corrección
   y reenvío por su titular.
3. Vuelve a ingresar como el proveedor. La aprobación habilita automáticamente
   el Seller Center del centro. Una ficha aprobada por una versión anterior
   puede requerir **Habilitar acceso del titular** en su revisión administrativa.
4. En **Mis actividades → Nueva actividad**, crea «Matemáticas básicas»,
   edades 5–14, modalidad, lugar, valor referencial y Sparks simulados.
   Puedes adjuntar PNG/JPEG de hasta 3 MB. Guarda primero como **Borrador**.
5. Desde **Sesiones y cupos**, crea una sesión futura con capacidad 10. Puedes
   agregar más sesiones. Publica la actividad cuando esté lista. Pausarla
   retira nuevas reservas y conserva el historial.
6. Como familia, activa un plan demo si falta saldo, busca la actividad por
   comuna/edad y reserva. Anota el código **KS-ID**: quedan 9 de 10 cupos.
7. Como proveedor titular, abre **Reservas** y **Horarios y cupos**: verifica
   ese mismo código y disponibilidad. También recibe una notificación.
8. Como `admin`, filtra **Reservas** por centro y revisa el mismo código.
   Como otro proveedor, el registro, su CSV y comprobante deben quedar fuera
   de su acceso.
9. Como titular de la reserva, cancela: cambia a **Cancelado**, devuelve Sparks
   y libera el cupo sin borrar la operación. El proveedor puede registrar
   asistencia una vez o cancelar el horario completo con motivo y 48 horas
   de anticipación, según corresponda. La asistencia no es un tercer estado.

El comprobante identifica proveedor, sesión, titular adulto, fecha/hora en
America/Santiago, un cupo, estado y créditos simulados. No acredita pagos ni
constituye documento tributario. No hay pasarela de pago rechazado: el rechazo
por Sparks insuficientes revierte la operación y no deja un cupo consumido.

## Cápsulas de 30–60 segundos

- **Incorporación:** usa `deporte_demo`, cambia a administración y muestra
  cómo una decisión habilita a ese mismo titular, sin crear una actividad.
- **Oferta y reserva:** usa `kidsdemo`, enseña Matemáticas básicas y sus
  sesiones; cambia a `familia_demo_001`, reserva y muestra el código en ambos.
- **Supervisión:** como `admin`, selecciona el centro y un rango de fechas.
  Muestra cómo cambian tablas e indicadores calculados desde las reservas.

En los paneles, **Datos de demostración** distingue GMV referencial de comisión
estimada. La comisión mostrada es 10% del valor de asistencias; no descuenta
dinero ni modifica liquidaciones históricas. La membresía B2B $35.000 netos/mes,
ticket $25.000, metas M12 (8 proveedores, 150 familias) y 499 reservas año 1 se
presentan aparte como **Metas y proyección del modelo académico**. Las compras
de Sparks no se convierten en ingresos y no se define equivalencia Spark/CLP.
