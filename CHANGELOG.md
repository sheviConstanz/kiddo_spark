# Historial de cambios

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
