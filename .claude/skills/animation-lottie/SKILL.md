---
name: animation-lottie
description: "Lottie rendering of After Effects animations for web and React. Use when implementing Lottie, lottie-web, lottie-react, dotLottie or bodymovin JSON exports, animated icons, micro-interactions or loading animations. Complements GSAP ScrollTrigger and Framer Motion."
---

# Lottie Animations

## Overview

Lottie is a library for rendering After Effects animations in real-time on web, iOS, Android, and React Native. Created by Airbnb, it allows designers to ship animations as easily as shipping static assets. Animations are exported from After Effects as JSON files using the Bodymovin plugin, then rendered natively with minimal performance overhead.

**When to use Lottie:**
- Designer-created animations that need pixel-perfect fidelity
- Complex animated icons and micro-interactions
- Loading animations and progress indicators
- Onboarding sequences and tutorial animations
- Marketing animations and promotional content
- Alternative to GIF/video with smaller file sizes and scalability

**Key advantages:**
- Vector-based (scalable without quality loss)
- Significantly smaller file sizes than GIF or video
- Editable at runtime (colors, speed, segments)
- Full designer control via After Effects
- Cross-platform rendering consistency
- Interactive controls (play, pause, seek, loop)

## Fichiers de référence

- [references/common_patterns.md](references/common_patterns.md) : sept recettes (page HTML avec dotLottie-web, composant React avec contrôles, écouteurs d'événements, animation pilotée par le scroll avec lottie-react, segment joué au survol, plusieurs animations et thèmes, rendu dans un web worker). À ouvrir pour poser une animation dans une page.
- [references/integration_patterns.md](references/integration_patterns.md) : couplage avec GSAP ScrollTrigger et Framer Motion, intégrations Vue 3 et Svelte. À ouvrir seulement dans l'un de ces environnements.
- [references/api_reference.md](references/api_reference.md) : API de dotlottie-web, DotLottieWorker, dotlottie-react, lottie-web et lottie-react, hooks `useLottie` et `useLottieInteractivity`. À ouvrir pour une option, une méthode ou un événement précis.
- [references/after_effects_export.md](references/after_effects_export.md) : export depuis After Effects avec Bodymovin (installation, réglages, fonctions prises en charge, optimisation, problèmes d'export, test, dépannage). À ouvrir pour préparer ou corriger un fichier exporté.
- [references/performance_guide.md](references/performance_guide.md) : objectifs chiffrés, poids des fichiers, rendu, mémoire, réseau, mobile, suivi des performances, problèmes courants. À ouvrir quand une animation saccade, pèse trop ou ralentit la page.

## Core Concepts

### Lottie Format Types

**1. JSON Lottie (.json)**
- Original Lottie format
- Exported from After Effects via Bodymovin plugin
- Human-readable JSON structure
- Larger file sizes (not compressed)
- Widely supported across all platforms

**2. dotLottie (.lottie)**
- Modern compressed format
- ZIP archive containing JSON + assets
- Supports multiple animations and themes in one file
- Smaller file sizes (up to 90% reduction)
- Recommended for production use

### Library Options

**lottie-web** (original library):
```javascript
import lottie from 'lottie-web';

lottie.loadAnimation({
  container: document.getElementById('lottie-container'),
  renderer: 'svg', // or 'canvas', 'html'
  loop: true,
  autoplay: true,
  path: 'animation.json' // or animationData: jsonData
});
```

**@lottiefiles/dotlottie-web** (modern, recommended):
```javascript
import { DotLottie } from '@lottiefiles/dotlottie-web';

new DotLottie({
  canvas: document.getElementById('canvas'),
  src: 'animation.lottie',
  autoplay: true,
  loop: true
});
```

**@lottiefiles/dotlottie-react** (React integration):
```jsx
import { DotLottieReact } from '@lottiefiles/dotlottie-react';

<DotLottieReact
  src="animation.lottie"
  loop
  autoplay
  style={{ height: 300 }}
/>
```

**lottie-react** (alternative React wrapper):
```jsx
import Lottie from 'lottie-react';
import animationData from './animation.json';

<Lottie animationData={animationData} loop={true} />
```

### Animation Data Sources

**1. LottieFiles** (lottie.host)
- 100,000+ free animations
- Direct URL embedding
- CDN hosting

**2. Local JSON/dotLottie files**
- Bundled with application
- Better performance (no network request)
- Version control friendly

**3. After Effects export**
- Custom designer animations
- Bodymovin plugin required
- Export settings critical for file size

## Common Patterns

Sept recettes, de la page HTML avec dotLottie-web au rendu dans un web worker : [references/common_patterns.md](references/common_patterns.md). À ouvrir pour poser une animation dans une page.

## Integration Patterns

GSAP ScrollTrigger, Framer Motion, Vue 3 et Svelte : [references/integration_patterns.md](references/integration_patterns.md). À ouvrir seulement dans l'un de ces environnements.

## Performance Optimization

### File Size Optimization

**1. Export Settings in After Effects:**
- Enable "Skip images that aren't used"
- Use "Glyphs" instead of fonts when possible
- Simplify paths (reduce points in illustrator)
- Avoid effects that create large data (particles, noise)
- Use shape layers instead of vector layers

**2. Compression:**
- Use dotLottie format (.lottie) for automatic compression
- Run JSON through Lottie optimizer tools
- Remove unnecessary metadata

**3. Lazy Loading:**
```jsx
const LazyLottie = () => {
  const [shouldLoad, setShouldLoad] = React.useState(false);

  React.useEffect(() => {
    const observer = new IntersectionObserver((entries) => {
      if (entries[0].isIntersecting) {
        setShouldLoad(true);
      }
    });

    observer.observe(document.getElementById('lottie-trigger'));
    return () => observer.disconnect();
  }, []);

  return (
    <div id="lottie-trigger">
      {shouldLoad && <DotLottieReact src="animation.lottie" loop autoplay />}
    </div>
  );
};
```

### Runtime Performance

**1. Renderer Selection:**
```javascript
// SVG: Best quality, slower for complex animations
// Canvas: Better performance, rasterized
// HTML: Limited support, use only for simple animations

// For complex animations, prefer canvas
new DotLottie({
  canvas: document.getElementById('canvas'),
  src: 'animation.lottie',
  autoplay: true,
  loop: true,
  renderConfig: {
    devicePixelRatio: window.devicePixelRatio || 1
  }
});
```

**2. Web Workers:**
```javascript
// Offload to worker for heavy animations
import { DotLottieWorker } from '@lottiefiles/dotlottie-web';

new DotLottieWorker({
  canvas: document.getElementById('canvas'),
  src: 'heavy-animation.lottie',
  autoplay: true,
  loop: true
});
```

**3. Mobile Optimization:**
```javascript
// Reduce quality on mobile
const isMobile = /iPhone|iPad|iPod|Android/i.test(navigator.userAgent);

new DotLottie({
  canvas: document.getElementById('canvas'),
  src: isMobile ? 'animation-low.lottie' : 'animation-high.lottie',
  autoplay: true,
  loop: true,
  renderConfig: {
    devicePixelRatio: isMobile ? 1 : window.devicePixelRatio
  }
});
```

## Common Pitfalls

### 1. Memory Leaks from Improper Cleanup

**Problem:** Not destroying Lottie instances when components unmount.

**Solution:**
```jsx
const SafeAnimation = () => {
  const [dotLottie, setDotLottie] = React.useState(null);

  React.useEffect(() => {
    return () => {
      // Always destroy instance on unmount
      dotLottie?.destroy();
    };
  }, [dotLottie]);

  return <DotLottieReact src="animation.lottie" dotLottieRefCallback={setDotLottie} />;
};
```

### 2. Event Listener Cleanup

**Problem:** Event listeners not removed, causing multiple handlers.

**Solution:**
```jsx
useEffect(() => {
  if (!dotLottie) return;

  const handleComplete = () => console.log('Complete');
  dotLottie.addEventListener('complete', handleComplete);

  // MUST return cleanup function
  return () => {
    dotLottie.removeEventListener('complete', handleComplete);
  };
}, [dotLottie]);
```

### 3. Large File Sizes

**Problem:** Exported JSON files are 500KB+ for simple animations.

**Solutions:**
- Simplify After Effects composition (reduce layers, keyframes)
- Use dotLottie format for compression
- Check Bodymovin export settings (disable "Include expressions" if not needed)
- Remove unused assets before export
- Use Lottie optimizer tools: https://lottiefiles.com/tools/lottie-editor

### 4. Animation Performance Issues

**Problem:** Animation stutters or drops frames.

**Solutions:**
- Switch from SVG to Canvas renderer
- Use `DotLottieWorker` for web worker rendering
- Reduce complexity in After Effects (fewer layers, simpler shapes)
- Lower devicePixelRatio on mobile
- Avoid animating too many properties simultaneously

### 5. Incorrect Path/URL References

**Problem:** Animation doesn't load due to CORS or incorrect paths.

**Solution:**
```jsx
// Use animationData for local imports (best for bundled apps)
import animationData from './animation.json';
<Lottie animationData={animationData} />

// OR use path for external URLs (requires CORS headers)
<DotLottieReact src="https://example.com/animation.lottie" />

// For Next.js, place in public/ folder
<DotLottieReact src="/animations/animation.lottie" />
```

### 6. After Effects Export Compatibility

**Problem:** Some After Effects features don't export to Lottie.

**Unsupported features:**
- Layer effects (drop shadows, glows) - use shape layers instead
- Blending modes (limited support)
- 3D layers
- Expressions (partial support)
- Track mattes (partial support)

**Solution:**
- Test export early and often
- Use LottieFiles preview before exporting
- Check Bodymovin compatibility: https://airbnb.io/lottie/#/supported-features
- Convert effects to shapes when possible

## Resources

This skill includes:

### scripts/
- `generate_lottie_component.py` - Generate React/Vue/Svelte Lottie component boilerplate
- `optimize_lottie.py` - Optimize Lottie JSON file size

### references/
- `api_reference.md` - Complete API documentation for lottie-web, lottie-react, and dotlottie-web
- `after_effects_export.md` - Guide for exporting animations from After Effects
- `performance_guide.md` - Detailed performance optimization strategies

### assets/
- `starter_lottie/` - Complete React + Vite starter template with Lottie examples
- `examples/` - Real-world Lottie animation patterns and use cases

## Related Skills

- **gsap-scrolltrigger** - For scroll-driven Lottie animations synchronized with page scroll
- **motion-framer** - Combine with Framer Motion for layout animations wrapping Lottie
- **animated-component-libraries** - Pre-built components that may include Lottie animations
- **threejs-webgl** - For 3D animations beyond Lottie's 2D capabilities
- **react-three-fiber** - Alternative for complex 3D animated scenes

---

*Vendorisée depuis [claudedesignskills](https://github.com/freshtechbro/claudedesignskills) de freshtechbro (plugin `animation-components`, skill `lottie-animations` v1.0.0, licence MIT, © 2025 Claude Skills Project). Copie SKILL.md + references/ uniquement (pas de scripts ni d'assets, conformément à la politique de vendoring du template). Attribution, périmètre retenu et procédure de re-synchronisation : `docs/vendored-animation.md`.*
