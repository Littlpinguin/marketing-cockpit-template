---
name: animation-scroll-reveal
description: "Simple scroll-triggered reveals with AOS (Animate On Scroll). Use when a marketing or landing page needs basic fade or slide effects on scroll without complex orchestration. Lighter alternative to GSAP ScrollTrigger and Locomotive Scroll."
---

# Scroll Reveal Libraries

## Overview

This skill covers AOS (Animate On Scroll), a lightweight CSS-driven library for scroll-triggered animations. AOS excels at simple fade, slide, and zoom effects activated when elements enter the viewport.

**Key Features**:
- **Minimal Setup**: Single JavaScript file + CSS
- **Data Attribute API**: Configure animations in HTML
- **Performance**: CSS-driven, GPU-accelerated animations
- **50+ Built-in Animations**: Fades, slides, zooms, flips
- **Framework Agnostic**: Works with vanilla JS, React, Vue, etc.

**When to Use**:
- Marketing/landing pages with simple scroll effects
- Content-heavy sites (blogs, documentation)
- Quick prototypes requiring scroll animations
- Projects where GSAP/Framer Motion complexity isn't needed

**When NOT to Use**:
- Complex animation timelines or orchestration → Use GSAP ScrollTrigger
- Physics-based animations → Use React Spring or Framer Motion
- Precise scroll-synced animations → Use GSAP ScrollTrigger
- Heavy interactive animations → Use Framer Motion

## Fichiers de référence

- [references/aos_api.md](references/aos_api.md) : référence complète d'AOS (initialisation, options globales, attributs `data-aos-*`, méthodes, événements, easings, valeurs d'ancrage, désactivation, compatibilité, dépannage). À ouvrir pour une option absente de la configuration ci-dessous ou quand un déclenchement se comporte mal.
- [references/animation_catalog.md](references/animation_catalog.md) : catalogue des animations intégrées (fondus, glissements, zooms, bascules) avec combinaisons, animations sur mesure, classement de performance et guide de choix par type de contenu. À ouvrir pour choisir l'effet d'une section.
- [references/common_patterns.md](references/common_patterns.md) : sept recettes HTML de sections (hero de landing page, grille de cartes, sections alternées, témoignages, déclencheur sur une autre ancre, enchaînement séquentiel, galerie d'images). À ouvrir au moment d'écrire le balisage d'une section.
- [references/integration_patterns.md](references/integration_patterns.md) : mise en place dans React (initialisation, changement de route, contenu dynamique, composant enveloppe), Vue.js et Next.js. À ouvrir seulement si la page tourne dans l'un de ces frameworks.

## Core Concepts

### Installation

**CDN (Quickest)**:
```html
<head>
  <link rel="stylesheet" href="https://unpkg.com/aos@next/dist/aos.css" />
</head>
<body>
  <!-- Content with data-aos attributes -->

  <script src="https://unpkg.com/aos@next/dist/aos.js"></script>
  <script>
    AOS.init();
  </script>
</body>
```

**NPM/Yarn (Recommended)**:
```bash
npm install aos@next
# or
yarn add aos@next
```

```javascript
import AOS from 'aos';
import 'aos/dist/aos.css';

AOS.init();
```

### Basic Usage

Apply animations using the `data-aos` attribute:

```html
<!-- Fade in -->
<div data-aos="fade-in">Content</div>

<!-- Fade up -->
<div data-aos="fade-up">Content</div>

<!-- Slide from right -->
<div data-aos="slide-left">Content</div>

<!-- Zoom in -->
<div data-aos="zoom-in">Content</div>
```

### Configuration Options

**Global Configuration**:
```javascript
AOS.init({
  // Animation settings
  duration: 800,  // Animation duration (ms): 0-3000
  delay: 0,       // Delay before animation (ms): 0-3000
  offset: 120,    // Offset from trigger point (px)
  easing: 'ease', // Easing function
  once: false,    // Animate only once (true) or every time (false)
  mirror: false,  // Animate out when scrolling past

  // Placement
  anchorPlacement: 'top-bottom', // Which position triggers animation

  // Performance
  disable: false,                // Disable on mobile/tablet
  startEvent: 'DOMContentLoaded', // Initialization event
  debounceDelay: 50,             // Window resize debounce
  throttleDelay: 99              // Scroll throttle
});
```

**Per-Element Overrides**:
```html
<div
  data-aos="fade-up"
  data-aos-duration="1000"
  data-aos-delay="200"
  data-aos-offset="50"
  data-aos-easing="ease-in-out"
  data-aos-once="true"
  data-aos-mirror="true"
  data-aos-anchor-placement="center-bottom"
>
  Custom configured element
</div>
```

## Common Patterns

Sept recettes HTML de sections de page (hero, grille de cartes, sections alternées, témoignages, ancre externe, enchaînement, galerie) : [references/common_patterns.md](references/common_patterns.md). À ouvrir au moment d'écrire le balisage `data-aos` d'une section.

## Integration Patterns

React, Vue.js et Next.js : [references/integration_patterns.md](references/integration_patterns.md). À ouvrir seulement si la page tourne dans l'un de ces frameworks.

## Performance Optimization

### 1. Disable on Mobile Devices

```javascript
AOS.init({
  disable: 'mobile', // Disable on mobile
  // Or use function for custom logic
  disable: function() {
    return window.innerWidth < 768;
  }
});
```

### 2. Use Once for Better Performance

```javascript
AOS.init({
  once: true, // Animate only once (better performance)
  mirror: false // Don't animate out
});
```

### 3. Optimize Throttle and Debounce

```javascript
AOS.init({
  throttleDelay: 99,  // Scroll event throttle (default)
  debounceDelay: 50   // Resize event debounce (default)
});
```

### 4. Disable Mutation Observer for Static Content

```javascript
AOS.init({
  disableMutationObserver: true // Disable for fully static content
});
```

### 5. Reduce Animation Complexity

```html
<!-- Simpler animations perform better -->
<div data-aos="fade-in">Simple fade</div>

<!-- Complex animations may cause jank -->
<div data-aos="flip-left">Complex flip</div>
```

### 6. Use RequestIdleCallback for Initialization

```javascript
if ('requestIdleCallback' in window) {
  requestIdleCallback(() => {
    AOS.init({ duration: 800 });
  });
} else {
  AOS.init({ duration: 800 });
}
```

## Common Pitfalls

### 1. Forgetting to Refresh After DOM Changes

**Problem**: New elements don't animate after being added dynamically.

**Solution**: Call `AOS.refresh()` or `AOS.refreshHard()`:

```javascript
// After adding elements to DOM
const newElement = document.createElement('div');
newElement.setAttribute('data-aos', 'fade-in');
container.appendChild(newElement);

// Refresh AOS
AOS.refresh(); // Recalculate positions
// or
AOS.refreshHard(); // Reinitialize completely
```

### 2. Animations Not Working in React

**Problem**: AOS doesn't detect elements on first render or route changes.

**Solution**: Initialize in `useEffect` and refresh on route/content changes:

```jsx
useEffect(() => {
  AOS.init();
  return () => AOS.refresh(); // Cleanup
}, []);

useEffect(() => {
  AOS.refresh(); // Refresh on route change
}, [location.pathname]);
```

### 3. Scroll Performance Issues

**Problem**: Page scrolling feels janky with many animated elements.

**Solution**: Reduce animated elements and use `once: true`:

```javascript
AOS.init({
  once: true, // Animate only once
  disable: window.innerWidth < 768 // Disable on mobile
});
```

### 4. CSS Conflicts

**Problem**: Custom CSS interferes with AOS animations.

**Solution**: Use more specific selectors and avoid `!important`:

```css
/* Bad: Conflicts with AOS */
div {
  opacity: 1 !important;
}

/* Good: Specific selector */
.my-content > div {
  /* styles */
}
```

### 5. Anchor Placement Confusion

**Problem**: Animations trigger at unexpected scroll positions.

**Solution**: Understand anchor placement options:

```javascript
// Triggers when element's top hits viewport bottom
data-aos-anchor-placement="top-bottom"

// Triggers when element's center hits viewport center
data-aos-anchor-placement="center-center"

// Triggers when element's bottom hits viewport top
data-aos-anchor-placement="bottom-top"
```

### 6. Duration/Delay Limits

**Problem**: Values above 3000ms don't work.

**Solution**: Add custom CSS for extended durations:

```css
body[data-aos-duration='4000'] [data-aos],
[data-aos][data-aos][data-aos-duration='4000'] {
  transition-duration: 4000ms;
}
```

```html
<div data-aos="fade-in" data-aos-duration="4000">
  Long animation
</div>
```

## Built-in Animations

### Fade Animations
- `fade-in` - Simple fade in
- `fade-up` - Fade in from bottom
- `fade-down` - Fade in from top
- `fade-left` - Fade in from right
- `fade-right` - Fade in from left
- `fade-up-right` - Diagonal fade
- `fade-up-left` - Diagonal fade
- `fade-down-right` - Diagonal fade
- `fade-down-left` - Diagonal fade

### Slide Animations
- `slide-up` - Slide from bottom
- `slide-down` - Slide from top
- `slide-left` - Slide from right
- `slide-right` - Slide from left

### Zoom Animations
- `zoom-in` - Zoom in
- `zoom-in-up` - Zoom in from bottom
- `zoom-in-down` - Zoom in from top
- `zoom-in-left` - Zoom in from right
- `zoom-in-right` - Zoom in from left
- `zoom-out` - Zoom out
- `zoom-out-up` - Zoom out to top
- `zoom-out-down` - Zoom out to bottom
- `zoom-out-left` - Zoom out to left
- `zoom-out-right` - Zoom out to right

### Flip Animations
- `flip-up` - Flip from bottom
- `flip-down` - Flip from top
- `flip-left` - Flip from right
- `flip-right` - Flip from left

## Custom Animations

Create custom animations with CSS:

```css
[data-aos="custom-slide-bounce"] {
  opacity: 0;
  transform: translateY(100px);
  transition-property: transform, opacity;
}

[data-aos="custom-slide-bounce"].aos-animate {
  opacity: 1;
  transform: translateY(0);
  animation: bounce 0.5s;
}

@keyframes bounce {
  0%, 20%, 50%, 80%, 100% {
    transform: translateY(0);
  }
  40% {
    transform: translateY(-10px);
  }
  60% {
    transform: translateY(-5px);
  }
}
```

```html
<div data-aos="custom-slide-bounce">
  Custom animation
</div>
```

## Comparison with Alternatives

### AOS vs GSAP ScrollTrigger

| Feature | AOS | GSAP ScrollTrigger |
|---------|-----|-------------------|
| **Complexity** | Simple, data-attribute based | Advanced, JavaScript API |
| **Use Case** | Simple reveals | Complex timelines |
| **File Size** | ~13KB | ~27KB (GSAP) + ScrollTrigger |
| **Performance** | CSS-driven | JavaScript-driven |
| **Learning Curve** | Minutes | Hours |
| **Customization** | Limited | Extensive |
| **Best For** | Marketing pages | Interactive experiences |

**Use AOS when**:
- Simple fade/slide/zoom effects
- Quick implementation needed
- Minimal JavaScript preferred
- Basic scroll reveals sufficient

**Use GSAP ScrollTrigger when**:
- Complex animation sequences
- Precise scroll-synced animations
- Timeline orchestration needed
- Advanced easing/physics required

## Resources

### Official Documentation
- **AOS**: https://michalsnik.github.io/aos/
- **GitHub**: https://github.com/michalsnik/aos

Les scripts et assets de la skill d'origine ne sont pas copiés dans ce template : voir `docs/vendored-animation.md`, section « Périmètre retenu ».

### References
- `references/aos_api.md` - Complete AOS API reference
- `references/animation_catalog.md` - All built-in animations with demos
- `references/integration_patterns.md` - Framework integration guides

## Related Skills

- **gsap-scrolltrigger**: For complex scroll-driven animations
- **motion-framer**: For React-specific animations with physics
- **locomotive-scroll**: For smooth scrolling with parallax
- **animated-component-libraries**: For pre-built animated React components

---

*Vendorisée depuis [claudedesignskills](https://github.com/freshtechbro/claudedesignskills) de freshtechbro (plugin `animation-components`, skill `scroll-reveal-libraries` v1.0.0, licence MIT, © 2025 Claude Skills Project). Copie SKILL.md + references/ uniquement (pas de scripts ni d'assets, conformément à la politique de vendoring du template). Attribution, périmètre retenu et procédure de re-synchronisation : `docs/vendored-animation.md`.*
