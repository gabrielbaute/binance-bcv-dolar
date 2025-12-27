# Assets / Static Files

Este directorio contiene todos los recursos estáticos necesarios para la aplicación web.

## 📁 Estructura de Archivos Requeridos

### Iconos de la Aplicación (PWA)
Los siguientes iconos son necesarios para que la aplicación funcione como Progressive Web App:

- `icon-72.png` - 72x72px
- `icon-96.png` - 96x96px
- `icon-128.png` - 128x128px
- `icon-144.png` - 144x144px
- `icon-152.png` - 152x152px
- `icon-192.png` - 192x192px (maskable)
- `icon-384.png` - 384x384px
- `icon-512.png` - 512x512px (maskable)

### Favicons
- `favicon-16x16.png` - 16x16px
- `favicon-32x32.png` - 32x32px
- `apple-touch-icon.png` - 180x180px

### Imágenes para Redes Sociales
Para que las previsualizaciones en redes sociales se vean correctamente:

- `og-image.png` - 1200x630px (Open Graph/Facebook)
- `twitter-image.png` - 1200x675px (Twitter Card)

### Screenshots (PWA)
Para la instalación de la PWA:

- `screenshot-wide.png` - 1280x720px (desktop)
- `screenshot-mobile.png` - 750x1334px (mobile)
- `screenshot.png` - General screenshot

### Iconos de Shortcuts
- `calculator-icon.png` - 96x96px
- `chart-icon.png` - 96x96px

## 🎨 Guía de Diseño

### Colores del Proyecto
- **Primario**: `#667eea` (Azul/Púrpura)
- **Secundario**: `#764ba2` (Púrpura oscuro)
- **Acento**: `#f093fb` (Rosa)
- **Fondo**: Gradiente de `#667eea` a `#764ba2`

### Elementos del Logo/Icono
- Incluir símbolo de intercambio/cambio
- Iconos relacionados con finanzas (gráficos, monedas)
- Mantener diseño simple y reconocible en tamaños pequeños

## 🛠️ Herramientas Recomendadas

### Para generar los iconos en todos los tamaños:
```bash
# Usando ImageMagick (desde un icono base de 512x512)
convert icon-512.png -resize 72x72 icon-72.png
convert icon-512.png -resize 96x96 icon-96.png
convert icon-512.png -resize 128x128 icon-128.png
convert icon-512.png -resize 144x144 icon-144.png
convert icon-512.png -resize 152x152 icon-152.png
convert icon-512.png -resize 192x192 icon-192.png
convert icon-512.png -resize 384x384 icon-384.png

# Para favicons
convert icon-512.png -resize 16x16 favicon-16x16.png
convert icon-512.png -resize 32x32 favicon-32x32.png
convert icon-512.png -resize 180x180 apple-touch-icon.png
```

### Generadores Online
- [Favicon Generator](https://realfavicongenerator.net/)
- [PWA Icon Generator](https://www.pwabuilder.com/)
- [Open Graph Image Generator](https://www.opengraph.xyz/)

## 📝 Notas Importantes

1. **Maskable Icons**: Los iconos marcados como "maskable" (192px y 512px) deben tener una zona segura del 80% del tamaño total para adaptarse a diferentes formas de íconos en Android.

2. **Open Graph Images**: Asegúrate de que el texto sea legible y los elementos importantes estén centrados, ya que algunas plataformas recortan las imágenes.

3. **Optimización**: Comprime todas las imágenes PNG usando herramientas como:
   - TinyPNG
   - ImageOptim
   - Squoosh

4. **Actualización de URLs**: No olvides actualizar las URLs en `index.html` reemplazando `https://tudominio.com/` con tu dominio real.

## 🎯 Plantilla para Open Graph Image

Incluye en la imagen de 1200x630px:
- Logo o icono de la app
- Título: "Tasas de Cambio P2P Venezuela"
- Subtítulo: "Binance P2P | BCV Oficial | Calculadora USD/VES"
- Elementos visuales: gráficos, símbolos de moneda
- Colores del gradiente del proyecto