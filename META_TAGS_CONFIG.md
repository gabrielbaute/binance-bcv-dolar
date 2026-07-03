# Configuración de Meta Tags y URLs

Este archivo contiene las instrucciones para personalizar las URLs y configuraciones del proyecto antes de deployar.

## 🔧 Archivos a Modificar

### 1. `app/ui/index.html`

Reemplaza todas las ocurrencias de `https://tudominio.com/` con tu URL real:

```html
<!-- Open Graph / Facebook -->
<meta property="og:url" content="https://TU-DOMINIO-REAL.com/">

<!-- Twitter -->
<meta property="twitter:url" content="https://TU-DOMINIO-REAL.com/">

<!-- Canonical URL -->
<link rel="canonical" href="https://TU-DOMINIO-REAL.com/">

<!-- JSON-LD -->
"url": "https://TU-DOMINIO-REAL.com/"
```

También actualiza:
```html
<meta property="twitter:creator" content="@TU_USUARIO_TWITTER">
```

### 2. `app/ui/static/robots.txt`

```txt
Sitemap: https://TU-DOMINIO-REAL.com/sitemap.xml
```

### 3. `app/ui/static/sitemap.xml`

Reemplaza todas las ocurrencias de `https://tudominio.com/` con tu URL real:

```xml
<loc>https://TU-DOMINIO-REAL.com/</loc>
<image:loc>https://TU-DOMINIO-REAL.com/static/assets/og-image.png</image:loc>
<!-- ... etc -->
```

## 📝 Personalización del Contenido

### Meta Tags Personalizables

En `index.html`, puedes personalizar:

1. **Título y Descripción**: Ya están en español y optimizados para SEO
2. **Keywords**: Agrega más keywords relevantes si es necesario
3. **Autor**: Actualiza con tu información
4. **Redes Sociales**: Imágenes y handles de Twitter

### JSON-LD Schema

Actualiza el rating y contador si tienes datos reales:
```json
"aggregateRating": {
  "@type": "AggregateRating",
  "ratingValue": "4.8",
  "ratingCount": "100"
}
```

## 🖼️ Imágenes para Redes Sociales

Asegúrate de crear y colocar en `/static/assets/`:

1. **og-image.png** (1200x630px)
   - Para Facebook, LinkedIn, WhatsApp
   - Incluye: Logo, título, descripción visual
   
2. **twitter-image.png** (1200x675px)
   - Específica para Twitter
   - Puede ser la misma que og-image

3. **screenshot.png** (cualquier tamaño representativo)
   - Para JSON-LD schema
   - Captura de pantalla de la app en uso

## 🔍 Verificación

Después de hacer los cambios, verifica con estas herramientas:

1. **Facebook Sharing Debugger**
   - https://developers.facebook.com/tools/debug/

2. **Twitter Card Validator**
   - https://cards-dev.twitter.com/validator

3. **LinkedIn Post Inspector**
   - https://www.linkedin.com/post-inspector/

4. **Google Rich Results Test**
   - https://search.google.com/test/rich-results

## ✅ Checklist de Deployment

- [ ] Reemplazar `https://tudominio.com/` con URL real en `index.html`
- [ ] Actualizar `@tuusuario` con handle de Twitter real
- [ ] Actualizar URLs en `robots.txt`
- [ ] Actualizar URLs en `sitemap.xml`
- [ ] Crear todas las imágenes necesarias (ver `assets/README.md`)
- [ ] Subir imágenes a `/static/assets/`
- [ ] Verificar meta tags con herramientas de validación
- [ ] Actualizar `lastmod` en sitemap.xml con fecha de deployment
- [ ] Probar compartir en diferentes redes sociales
- [ ] Verificar que robots.txt sea accesible en `/robots.txt`
- [ ] Verificar que sitemap.xml sea accesible en `/sitemap.xml`

## 🚀 Después del Deployment

1. Enviar sitemap a Google Search Console
2. Verificar propiedad del sitio en diferentes plataformas
3. Configurar Google Analytics (opcional)
4. Configurar herramientas de monitoreo SEO
