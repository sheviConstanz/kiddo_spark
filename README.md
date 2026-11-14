# Kiddo Spark — prototipo académico

Kiddo Spark presenta una propuesta de actividades extracurriculares infantiles
que conecta familias, academias y servicios de apoyo en la Región de Valparaíso.
Es un prototipo para una tesis de Ingeniería Comercial. No opera un negocio real.

## Qué puedes hacer hoy

Explorar actividades, aplicar filtros y recorrer demostraciones de reservas,
planes Sparks, registro de centros y panel de proveedores. Las descargas son
documentos de demostración. El acceso no comprueba contraseñas; los cambios se
pierden al recargar o cerrar la página. No hay base de datos ni cobros reales.
Usa exclusivamente información ficticia.

## Abrirlo en tu computador

1. Descarga y descomprime la entrega completa en una carpeta.
2. Conserva juntos `Kiddo Spark B2B2C.html` y la carpeta `assets`.
3. Abre `Kiddo Spark B2B2C.html` con un navegador actualizado.
4. Mantén acceso a Internet: la página conserva una dependencia visual de
   Tailwind que descarga desde `https://cdn.tailwindcss.com`.

No necesitas una base de datos ni instalar un framework para esta versión.
No se garantiza funcionamiento sin Internet. Esta entrega se verificó mediante
comprobaciones de archivos; la revisión visual en navegador queda pendiente.

## Archivos de la entrega

- `Kiddo Spark B2B2C.html`: contenido, interacciones y estilos incrustados pendientes.
- `assets/css/styles.css`: hoja de estilos principal extraída del HTML.
- `README.md`: instrucciones de uso.
- `CHANGELOG.md`: historial de cambios y limitaciones comprobadas.

Para reenviar esta versión, incluye esos cuatro elementos conservando sus carpetas.
Enviar únicamente el HTML ya no conserva la hoja de estilos principal.
No comprimas toda la carpeta de trabajo: selecciona solo los elementos de la entrega.

## Compartir temporalmente desde Visual Studio Code

Esta sección explica una preparación futura. No se ha iniciado ni probado un
servidor o un enlace compartido en este incremento.

Un servidor local es un programa que muestra los archivos del prototipo desde
tu computador. Un puerto es el número que identifica ese servicio, por ejemplo
8000. El reenvío crea una dirección para acceder a ese servicio por Internet.

Si tienes Python 3 instalado, puedes usarlo sin paquetes adicionales:

1. Prepara una carpeta de presentación que contenga únicamente los cuatro
   elementos de la entrega indicados arriba. No sirvas la carpeta de desarrollo.
2. Abre esa carpeta en VS Code mediante **Archivo → Abrir carpeta**.
3. Abre **Terminal → Nueva terminal**. Ejecuta `python --version` para comprobar
   Python. Si no está instalado, pide ayuda a quien mantiene el prototipo.
4. Ejecuta `python -m http.server 8000 --bind 127.0.0.1`.
5. Abre en el navegador
   `http://127.0.0.1:8000/Kiddo%20Spark%20B2B2C.html`.
6. Comprueba que se ve correctamente antes de compartirlo.
7. En VS Code abre la paleta de comandos y busca **Ports: Focus on Ports View**.
   Selecciona **Forward a Port** e introduce `8000`. VS Code puede solicitar
   iniciar sesión con GitHub.
8. Copia la dirección reenviada y añade `/Kiddo%20Spark%20B2B2C.html` al final.
   La visibilidad privada limita el acceso; si los evaluadores necesitan entrar
   sin tu cuenta, revisa la opción de visibilidad pública antes de compartir.
   Un enlace público da acceso a los archivos servidos a quien lo tenga.
9. Mantén encendidos el computador, Internet, VS Code y la terminal durante
   la presentación. Pide a otra persona que pruebe el enlace.
10. Al terminar, detén el reenvío en **Ports** y presiona **Ctrl+C** en la terminal.

Si el puerto está ocupado, elige otro número y úsalo tanto en el comando como
en VS Code. Si falta el formato, revisa la carpeta `assets` y la conexión a Internet.
Si el enlace no responde, comprueba que el servidor y el reenvío siguen activos.
Este procedimiento sirve para una demostración temporal, no para alojamiento permanente.

Referencia: [reenvío de puertos en VS Code](https://code.visualstudio.com/docs/debugtest/port-forwarding).

## Desarrollo pendiente

Separar los estilos restantes y el JavaScript, acordar la arquitectura y añadir
persistencia, migraciones y acceso real por roles. Cada etapa requiere revisión.
No hay framework elegido. Los módulos comerciales seguirán siendo académicos;
no se presuponen pagos, transferencias ni campañas publicitarias reales.
