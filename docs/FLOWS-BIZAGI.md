# Flujos B2C y B2B de Kiddo Spark

Revisión de los modelos **Ingreso B2C** e **Ingreso B2B first** del equipo.
El B2C sigue al adulto responsable, la plataforma y el proveedor de la
actividad. El B2B sigue al proveedor como comprador de apoyo para su negocio,
la plataforma y el aliado que entrega el servicio.

## B2C · Desde buscar una actividad hasta evaluarla

| Paso del modelo | Qué cubre la demo y qué queda por acordar |
| --- | --- |
| Ingreso, cuenta, perfil del niño, consentimiento y preferencias | Registro de cliente y catálogo con filtros. Quedan por definir los datos mínimos, el consentimiento y las preferencias persistentes antes de implementar recomendaciones. Para la demo se usan datos ficticios. |
| Selección, disponibilidad, alternativas y recarga | Se pueden consultar horarios y cupos, buscar otra actividad y activar un plan de prueba. Las alternativas se buscan en el catálogo. |
| Descuento y confirmación | Bizagi ubica la confirmación en el carril del adulto responsable. En la demo, ese paso corresponde a **Solicitar reserva**, que aparta un cupo y descuenta Sparks. El requisito del equipo añade la aprobación posterior del proveedor. Solo un operador habilitado del centro puede confirmar antes del horario. |
| Continuar, cancelar o cambiar la búsqueda | El titular puede cancelar una reserva pendiente o confirmada. La demo devuelve cupo y Sparks una vez. Quedan pendientes la encuesta de cancelación, la política de rechazo y un plazo de aprobación o liberación automática. |
| Ubicación u enlace, realización y cierre | La ficha y la reserva muestran horario y centro. Quedan pendientes las instrucciones de asistencia presencial o virtual y el tratamiento de inasistencias. El centro puede registrar la asistencia de una reserva confirmada. |
| Puntos, opinión y recomendaciones | Las nuevas reservas suman 50 puntos al completarse, una sola vez. El cliente puede dejar una opinión. Quedan pendientes los tokens, las insignias y el uso de opiniones para recomendaciones. |

La migración 0009 conserva los estados de las reservas anteriores. Si una
reserva anterior ya generó puntos, completarla conserva ese saldo. Cancelarla
revierte los puntos que había generado.

## B2B · Desde una necesidad del proveedor hasta evaluar el apoyo

| Paso del modelo | Qué cubre la demo y qué queda por acordar |
| --- | --- |
| Crear cuenta y completar el perfil del negocio | Alta del proveedor, ficha, revisión y asignación de acceso al Seller Center. Queda por definir el consentimiento para el perfil de negocio. |
| Indicar necesidad y encontrar soluciones | El diagnóstico de Alivios B2B sugiere áreas según las respuestas. El directorio permite filtrar aliados. Para recomendaciones personalizadas faltan reglas sobre datos utilizados, compatibilidad y cobertura. |
| Elegir entre una herramienta y un servicio | El Seller Center ya reúne herramientas de operación. La activación según una necesidad y la configuración inicial de herramientas son pasos pendientes. |
| Cotizar, decidir y contratar | La demo registra orientación, asesoría o una solicitud de cotización con seguimiento. Quedan por definir vigencia, oferta formal, aceptación, asignación del especialista y la relación entre orden, contrato y pago. |
| Agendar, prestar el servicio y evaluarlo | Las preferencias de fecha y modalidad sirven para iniciar la conversación. Bizagi asigna la agenda a la plataforma y el cierre con informe al aliado. Quedan pendientes ambas etapas, además de las incidencias, métricas y evaluación del servicio. |

Para continuar con B2B conviene confirmar quién puede emitir una cotización,
qué información la vuelve aceptable y cuándo se considera confirmado el
servicio. Las reservas de actividades y las contrataciones de apoyo tienen
actores y estados distintos.
