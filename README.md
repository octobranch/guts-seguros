# GUTS Seguros — sitio estático para GitHub Pages

Sitio en español e inglés con home y cinco páginas de servicio por idioma. Incluye logo y colores originales, imágenes locales optimizadas, CSS/JS compartidos, dos comparativas por página, guías, listas, pasos, preguntas frecuentes, schema, enlaces internos, sitemap y 404.

## Publicar en GitHub Pages

1. Descomprime este ZIP y sube **su contenido a la raíz del repositorio**, incluido `.github/workflows/pages.yml`. No subas el ZIP como un único archivo.
2. Usa la rama `main` o `master`.
3. En **Settings → Pages → Build and deployment → Source**, elige **GitHub Actions**.
4. Abre **Actions → Publish GUTS static website** y ejecuta **Run workflow**; los siguientes pushes también publican.
5. Al terminar, abre la URL que devuelve el despliegue en Settings → Pages.

No necesitas PHP, servidor de aplicaciones, npm ni una clave de API. Un paso de preparación en Python estándar ajusta las URLs y crea el artefacto; lo publicado es HTML/CSS/JS estático.

### URLs correctas incluso dentro de un repositorio

Con `"site_url": ""` en `site.config.json`, el workflow obtiene la dirección real de GitHub Pages, incluida la subcarpeta del repositorio. Reescribe canonical, hreflang, metadatos sociales, schema y sitemap con esa base. Los enlaces y recursos internos son relativos.

Los HTML fuente traen `https://www.guts.mx/` como referencia para la previsualización y la futura migración. **Publica mediante el workflow incluido**, que sustituye esa base por la URL real de Pages; no selecciones publicación directa desde una rama sin preparar las URLs.

Si más adelante conectas un dominio propio, configúralo y verifica HTTPS en Pages. Después deja que `configure-pages` detecte la URL o establece el dominio completo en `site.config.json`, por ejemplo `"site_url": "https://www.guts.mx/"`. No incluyo un `CNAME` activo para evitar cambiar tu dominio actual.

## Archivos principales

- `index.html`: home en español.
- `seguro-gastos-medicos-mayores-cancun.html`
- `seguro-de-vida-cancun.html`
- `seguro-educativo-cancun.html`
- `seguro-de-ahorro-cancun.html`
- `seguro-persona-clave-cancun.html`
- `en/`: home y cinco páginas equivalentes en inglés.
- `assets/css/styles.css`: identidad, diseño, responsive y estilos de impresión.
- `assets/js/main.js`: menú, orientación por objetivo y consulta por correo.
- `assets/images/`: logo SVG original y fotografías WebP locales.
- `scripts/prepare_pages.py`: configuración de URLs y artefacto estático.
- `scripts/validate_site.py`: verificaciones de enlaces, contenido y SEO.
- `scripts/site-manifest.json`: rutas, idiomas, palabras principales y secundarias.
- `docs/`: mapa SEO, fuentes y comprobaciones de entrega.

## Contacto y WhatsApp

Se conserva el teléfono publicado por GUTS: **+52 241 112 3580**, y el correo **contacto@guts.mx**.

WhatsApp utiliza ese teléfono como destino. **Confirma que esté habilitado en WhatsApp antes de publicar**. Si usas otro número para ese canal, reemplaza `https://wa.me/522411123580` en los HTML. Los enlaces ya incluyen mensajes en el idioma y contexto del servicio.

El formulario prepara un mensaje revisable y abre la aplicación de correo del visitante. No envía consultas a un servidor ni confirma una solicitud recibida. No se publican formularios con expedientes médicos o datos de pago. Para recibir leads directamente en un CRM se necesita integrar posteriormente un endpoint o un proveedor de formularios.

## SEO y AEO incluidos

- Palabra principal en `<title>`, descripción y H1 de cada página.
- Contenido completo disponible sin JavaScript.
- Idiomas en URLs diferentes, con canonical propia y hreflang recíproco `es-MX`, `en` y `x-default`.
- `InsuranceAgency`, `WebSite`, `WebPage`, `Service` y `FAQPage`; `BreadcrumbList` en servicios.
- Preguntas visibles iguales a las del schema.
- Tablas con encabezados y caption; listas, pasos y enlaces descriptivos.
- CSS y JS sin CDN, imágenes con dimensiones y carga diferida cuando corresponde.
- Sin ratings, cifras, certificaciones, precios ni garantías comerciales no verificados.

No hay una etiqueta que garantice aparecer en Google o en respuestas de IA. La publicación debe poder rastrearse e indexarse; la competencia, el contenido, las señales del negocio y el trabajo posterior también influyen. Consulta `docs/MAPA-SEO.md`.

### Si esta publicación solo será una vista previa

Para evitar que la copia temporal se indexe, cambia `"indexable": false` en `site.config.json` y vuelve a desplegar. El artefacto usará `noindex,follow` y un sitemap vacío. Si quieres que la publicación temporal compita en búsqueda, conserva `true` y planifica después la migración al dominio final.

En sitios de proyecto como `usuario.github.io/repositorio/`, el `robots.txt` dentro de la subcarpeta no controla el origen completo de GitHub. Envía la URL exacta del sitemap en Search Console y verifica la propiedad correspondiente. El `robots.txt` incluido sí sirve como archivo raíz al usar un dominio propio.

## Editar y comprobar

Puedes editar los HTML directamente y conservar los enlaces y atributos de accesibilidad. Si cambias una respuesta de FAQ, actualiza también su texto en JSON-LD. Si cambias una ruta, actualiza enlaces, manifest y equivalencias de idioma.

```bash
python3 scripts/validate_site.py .
python3 scripts/prepare_pages.py --base-url https://usuario.github.io/repositorio/ --output _site
python3 scripts/validate_site.py _site
```

Usa una carpeta de salida vacía. Para una revisión visual local, abre `index.html` en un navegador o sirve la carpeta con el servidor estático que prefieras. La entrega no necesita instalar dependencias.

## Después de publicar

1. Revisa que los enlaces, imágenes y cambio de idioma funcionen en móvil y computadora.
2. Comprueba el destino de WhatsApp y realiza una consulta de prueba por correo.
3. Revisa las URLs reales en canonical, schema y sitemap.
4. Envía el sitemap a Search Console e inspecciona las páginas importantes.
5. Verifica la información comercial y las condiciones de los productos antes de mantenerlas publicadas.

Referencias oficiales: [GitHub Pages con workflows](https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages), [SEO de Google](https://developers.google.com/search/docs/fundamentals/seo-starter-guide), [versiones de idioma](https://developers.google.com/search/docs/specialty/international/localized-versions), [búsqueda con IA](https://developers.google.com/search/docs/fundamentals/ai-optimization-guide).
