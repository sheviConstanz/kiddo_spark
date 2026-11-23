# Incorporación de proveedores para el piloto

La especificación 1.0 del 17 de noviembre de 2026 fija los requisitos de este
incremento. Se conserva Django/SQLite y se reutilizan las cuentas, el catálogo
y la asignación de administradores por organización.

| Alcance | Resultado comprobable |
| --- | --- |
| RF-B01 a RF-B03 | El portal distingue un centro nuevo de uno registrado. Un adulto autenticado crea una ficha con los datos del centro, contacto ficticio y comuna piloto. |
| RF-B04, RF-B06 y RF-B08, RF-A01 | El titular ve su estado, los motivos y el historial. Administración y superadministración toman la revisión, observan, rechazan o aprueban. Solo el titular puede corregir una ficha observada y reenviarla. |
| RF-B05, RN-05, PA-01 y PA-02 | Hasta la aprobación, la oferta queda fuera del catálogo y las reservas. Las decisiones registran actor, motivo y fecha. Aprobar habilita al titular exclusivamente para su centro, con permisos de operador y sin permisos globales. |
| RF-B07 y RN-13 | Se identifica la demostración. Documentos requeridos y condiciones de membresía quedan por definir. |

La ficha utiliza el estado de aprobación existente para decidir si un centro
publica. Los eventos registran el resto de la revisión. Los centros históricos
conservan su aprobación original y no se genera un historial retroactivo.
Cada transición válida guarda su evento en la misma transacción. Una decisión
solo aplica al evento que estaba en pantalla al abrir el formulario. Esto evita
resolver una versión anterior después de una corrección o revisión paralela.

Verificación prevista mediante el cliente Django y una base temporal. Se
comprueban el recorrido, el aislamiento entre cuentas, las transiciones y la
visibilidad antes y después de aprobar. La revisión en navegador es una
comprobación independiente.

La corrección del 23 de noviembre integra la habilitación con el Seller Center,
actividades, sesiones, inventario, reservas automáticas, asistencia y cancelaciones.
La aprobación de la ficha y la publicación de una actividad son decisiones
distintas. No se exige una segunda revisión de actividades en esta demo.
El checkout con pasarela de pagos y la conciliación comercial no están implementados.
Ver [recorrido y datos de demostración](DEMO-ACADEMICA.md).
