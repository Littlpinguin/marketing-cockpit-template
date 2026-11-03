---
name: animation-animejs
description: "Anime.js animation engine for DOM, CSS, SVG and JS objects. Use when building timeline animations, stagger effects, SVG path animations or morphing, keyframe sequences or multi-step choreography. Alternative to GSAP for SVG-heavy, React-independent projects."
---

# Anime.js

Lightweight JavaScript animation library with powerful timeline and stagger capabilities for web animations.

## Overview

Anime.js (pronounced "Anime JS") is a versatile animation engine that works with DOM elements, CSS properties, SVG attributes, and JavaScript objects. Unlike React-specific libraries, Anime.js works with vanilla JavaScript and any framework.

**When to use this skill:**
- Timeline-based animation sequences with precise choreography
- Staggered animations across multiple elements
- SVG path morphing and drawing animations
- Keyframe animations with percentage-based timing
- Framework-agnostic animation (works with React, Vue, vanilla JS)
- Complex easing functions (spring, steps, cubic-bezier)

**Core features:**
- Timeline sequencing with relative positioning
- Powerful stagger utilities (grid, from center, easing)
- SVG morphing and path animations
- Built-in spring physics easing
- Keyframe support with flexible timing
- Small bundle size (~9KB gzipped)

## Fichiers de référence

- [references/common_patterns.md](references/common_patterns.md) : sept recettes (stagger séquentiel, stagger depuis le centre d'une grille, tracé de ligne SVG, morphing SVG, séquence en timeline, keyframes, animation liée au scroll). À ouvrir pour partir d'un motif existant.
- [references/integration_patterns.md](references/integration_patterns.md) : intégration React et Vue, animation le long d'un tracé SVG. À ouvrir dans l'un de ces frameworks ou pour faire suivre un chemin à un élément.
- [references/api_reference.md](references/api_reference.md) : référence de l'API (`anime()`, cibles, propriétés, paramètres, timeline, stagger, easings, helpers, callbacks, instance d'animation, exemples). À ouvrir pour un paramètre ou une méthode précise.
- [references/stagger_guide.md](references/stagger_guide.md) : `anime.stagger` en détail (options, point de départ, grilles, direction, easing, motifs, erreurs courantes, débogage). À ouvrir pour une cascade sur plusieurs éléments ou une grille.
- [references/timeline_guide.md](references/timeline_guide.md) : timelines en détail (ajout d'animations, décalages, motifs, contrôles de lecture, labels et timelines imbriquées, erreurs courantes, exemples réels, débogage). À ouvrir pour une séquence en plusieurs étapes.

## Core Concepts

### Basic Animation

The `anime()` function creates animations:

```javascript
import anime from 'animejs'

anime({
  targets: '.element',
  translateX: 250,
  rotate: '1turn',
  duration: 800,
  easing: 'easeInOutQuad'
})
```

### Targets

Multiple ways to specify animation targets:

```javascript
// CSS selector
anime({ targets: '.box' })

// DOM elements
anime({ targets: document.querySelectorAll('.box') })

// Array of elements
anime({ targets: [el1, el2, el3] })

// JavaScript object
const obj = { x: 0 }
anime({ targets: obj, x: 100 })
```

### Animatable Properties

**CSS Properties:**
```javascript
anime({
  targets: '.element',
  translateX: 250,
  scale: 2,
  opacity: 0.5,
  backgroundColor: '#FFF'
})
```

**CSS Transforms (Individual):**
```javascript
anime({
  targets: '.element',
  translateX: 250,   // Individual transform
  rotate: '1turn',   // Not 'transform: rotate()'
  scale: 2
})
```

**SVG Attributes:**
```javascript
anime({
  targets: 'path',
  d: 'M10 80 Q 77.5 10, 145 80', // Path morphing
  fill: '#FF0000',
  strokeDashoffset: [anime.setDashoffset, 0] // Line drawing
})
```

**JavaScript Objects:**
```javascript
const obj = { value: 0 }
anime({
  targets: obj,
  value: 100,
  round: 1,
  update: () => console.log(obj.value)
})
```

### Timeline

Create complex sequences with precise control:

```javascript
const timeline = anime.timeline({
  duration: 750,
  easing: 'easeOutExpo'
})

timeline
  .add({
    targets: '.box1',
    translateX: 250
  })
  .add({
    targets: '.box2',
    translateX: 250
  }, '-=500') // Start 500ms before previous animation ends
  .add({
    targets: '.box3',
    translateX: 250
  }, '+=200') // Start 200ms after previous animation ends
```

## Common Patterns

Sept recettes (stagger, stagger depuis le centre, tracé SVG, morphing SVG, timeline, keyframes, scroll) : [references/common_patterns.md](references/common_patterns.md). À ouvrir pour partir d'un motif existant.

## Integration Patterns

React, Vue et animation le long d'un tracé : [references/integration_patterns.md](references/integration_patterns.md). À ouvrir dans l'un de ces frameworks ou pour faire suivre un chemin à un élément.

## Advanced Techniques

### Spring Easing

```javascript
anime({
  targets: '.element',
  translateX: 250,
  easing: 'spring(1, 80, 10, 0)', // mass, stiffness, damping, velocity
  duration: 2000
})
```

### Steps Easing

```javascript
anime({
  targets: '.element',
  translateX: 250,
  easing: 'steps(5)',
  duration: 1000
})
```

### Custom Bezier

```javascript
anime({
  targets: '.element',
  translateX: 250,
  easing: 'cubicBezier(.5, .05, .1, .3)',
  duration: 1000
})
```

### Direction and Loop

```javascript
anime({
  targets: '.element',
  translateX: 250,
  direction: 'alternate', // 'normal', 'reverse', 'alternate'
  loop: true,             // or number of iterations
  easing: 'easeInOutQuad'
})
```

### Playback Control

```javascript
const animation = anime({
  targets: '.element',
  translateX: 250,
  autoplay: false
})

animation.play()
animation.pause()
animation.restart()
animation.reverse()
animation.seek(500) // Seek to 500ms
```

## Performance Optimization

### Use Transform and Opacity

```javascript
// ✅ Good: GPU-accelerated
anime({
  targets: '.element',
  translateX: 250,
  opacity: 0.5
})

// ❌ Avoid: Triggers layout
anime({
  targets: '.element',
  left: '250px',
  width: '500px'
})
```

### Batch Similar Animations

```javascript
// ✅ Single animation for multiple targets
anime({
  targets: '.multiple-elements',
  translateX: 250
})

// ❌ Avoid: Multiple separate animations
elements.forEach(el => {
  anime({ targets: el, translateX: 250 })
})
```

### Use `will-change` for Complex Animations

```css
.animated-element {
  will-change: transform, opacity;
}
```

### Disable autoplay for Scroll Animations

```javascript
const animation = anime({
  targets: '.element',
  translateX: 250,
  autoplay: false // Control manually
})
```

## Common Pitfalls

### 1. Forgetting Unit Types

```javascript
// ❌ Wrong: No unit
anime({ targets: '.element', width: 200 })

// ✅ Correct: Include unit
anime({ targets: '.element', width: '200px' })
```

### 2. Using CSS transform Property Directly

```javascript
// ❌ Wrong: Can't animate transform string
anime({ targets: '.element', transform: 'translateX(250px)' })

// ✅ Correct: Individual transform properties
anime({ targets: '.element', translateX: 250 })
```

### 3. Not Handling Animation Cleanup

```javascript
// ❌ Wrong: Animation continues after unmount
useEffect(() => {
  anime({ targets: ref.current, translateX: 250 })
}, [])

// ✅ Correct: Pause on cleanup
useEffect(() => {
  const anim = anime({ targets: ref.current, translateX: 250 })
  return () => anim.pause()
}, [])
```

### 4. Animating Too Many Elements

```javascript
// ❌ Avoid: Animating 1000+ elements
anime({ targets: '.many-items', translateX: 250 }) // 1000+ elements

// ✅ Better: Use CSS animations for large sets
// Or reduce element count with virtualization
```

### 5. Incorrect Timeline Timing

```javascript
// ❌ Wrong: Missing offset operator
.add({ targets: '.el2' }, '500') // Treated as absolute time

// ✅ Correct: Use relative operators
.add({ targets: '.el2' }, '-=500') // Relative to previous
.add({ targets: '.el3' }, '+=200') // Relative to previous
```

### 6. Overusing Loop

```javascript
// ❌ Avoid: Infinite loops drain battery
anime({
  targets: '.element',
  rotate: '1turn',
  loop: true,
  duration: 1000
})

// ✅ Better: Use CSS animations for infinite loops
@keyframes rotate {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}
```

## Resources

Les scripts et assets de la skill d'origine ne sont pas copiés dans ce template : voir `docs/vendored-animation.md`, section « Périmètre retenu ».

### References
- `api_reference.md` - Complete Anime.js API documentation
- `stagger_guide.md` - Stagger utilities and patterns
- `timeline_guide.md` - Timeline sequencing deep dive

## Related Skills

- **gsap-scrolltrigger** - More powerful timeline features and scroll integration
- **motion-framer** - React-specific declarative animations
- **react-spring-physics** - Physics-based spring animations
- **lightweight-3d-effects** - Simple 3D effects (Zdog, Vanta.js)

**Anime.js vs GSAP**: Use Anime.js for SVG-heavy animations, simpler projects, or when bundle size matters. Use GSAP for complex scroll-driven experiences, advanced timelines, and professional-grade control.

**Anime.js vs Framer Motion**: Use Anime.js for framework-agnostic projects or when working outside React. Use Framer Motion for React-specific declarative animations with gesture integration.

---

*Vendorisée depuis [claudedesignskills](https://github.com/freshtechbro/claudedesignskills) de freshtechbro (plugin `animation-components`, skill `animejs` v1.0.0, licence MIT, © 2025 Claude Skills Project). Copie SKILL.md + references/ uniquement (pas de scripts ni d'assets, conformément à la politique de vendoring du template). Attribution, périmètre retenu et procédure de re-synchronisation : `docs/vendored-animation.md`.*
