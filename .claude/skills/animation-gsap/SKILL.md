---
name: animation-gsap
description: "GSAP (GreenSock) and ScrollTrigger for web animation. Use when creating tweens, timelines, scroll-driven or scroll-triggered animations, pinning, scrubbing, parallax, or animating DOM, SVG, Canvas, WebGL or Three.js."
---

# GSAP & ScrollTrigger Development

## Overview

GSAP (GreenSock Animation Platform) is the industry-leading JavaScript animation library for creating high-performance, production-quality animations. ScrollTrigger is GSAP's powerful plugin for scroll-driven animations. Together, they enable everything from simple UI transitions to complex scroll-based storytelling experiences.

## Fichiers de référence

- [references/scrolltrigger_recipes.md](references/scrolltrigger_recipes.md) : les sept recettes de base (fondu au scroll, épinglage, section horizontale, parallaxe, timeline pilotée par le scroll, animations par lot, stagger) et les techniques avancées (séquence d'images pilotée par le scroll, défilement vers une ancre, animations selon la media query). À ouvrir en premier pour monter une animation au scroll.
- [references/common_patterns.md](references/common_patterns.md) : bibliothèque étendue de motifs prêts à copier (épinglage, défilement horizontal, parallaxe, textes, révélations d'images, navigation, transitions de page, indicateurs de progression, séquences d'images, responsive, intégrations), avec bonnes pratiques et pièges. À ouvrir quand les recettes de base ne couvrent pas le besoin.
- [references/integration_patterns.md](references/integration_patterns.md) : Three.js et WebGL, React (`useGSAP`, timeline partagée entre composants), Locomotive Scroll. À ouvrir seulement dans l'un de ces environnements.
- [references/api_reference.md](references/api_reference.md) : aide-mémoire de l'API (méthodes de tween, timelines, propriétés et callbacks, easings, stagger, propriétés et méthodes de ScrollTrigger, utilitaires). À ouvrir pour vérifier une propriété ou une signature.
- [references/easing_guide.md](references/easing_guide.md) : familles d'easings et leurs usages, arbre de décision, combinaisons, easings sur mesure, erreurs courantes, aide-mémoire. À ouvrir pour choisir une courbe au-delà de la section Easing Reference.

## Core Concepts

### The Basics: Tweens

A **tween** is a single animation from point A to point B.

```javascript
// Animate TO a state (from current)
gsap.to(".box", {
  x: 200,
  rotation: 360,
  duration: 1,
  ease: "power2.inOut"
});

// Animate FROM a state (to current)
gsap.from(".box", {
  opacity: 0,
  y: -50,
  duration: 0.8
});

// Animate FROM-TO (define both start and end)
gsap.fromTo(".box",
  { opacity: 0, scale: 0.5 }, // FROM
  { opacity: 1, scale: 1, duration: 1 } // TO
);
```

### Timelines: Sequencing Animations

**Timelines** orchestrate multiple tweens in sequence or overlap.

```javascript
const tl = gsap.timeline();

// Sequential by default
tl.to(".box1", { x: 100, duration: 1 })
  .to(".box2", { y: 100, duration: 1 })
  .to(".box3", { rotation: 360, duration: 1 });

// With labels for organization
tl.addLabel("start")
  .to(".hero", { opacity: 1, duration: 1 })
  .addLabel("reveal")
  .to(".content", { y: 0, duration: 0.8 }, "reveal") // Start at "reveal" label
  .to(".cta", { scale: 1, duration: 0.5 }, "reveal+=0.5"); // 0.5s after "reveal"
```

### Position Parameter (Timeline Timing)

Control when animations start within a timeline:

```javascript
const tl = gsap.timeline();

// Default: One after another
tl.to(".box1", { x: 100 })
  .to(".box2", { x: 100 }); // Starts after box1 finishes

// Start at the same time
tl.to(".box1", { x: 100 })
  .to(".box2", { y: 100 }, 0); // Starts at 0 seconds

// Relative positioning
tl.to(".box1", { x: 100, duration: 2 })
  .to(".box2", { y: 100 }, "-=1"); // Starts 1 second before box1 ends
  .to(".box3", { rotation: 360 }, "+=0.5"); // Starts 0.5s after box2 finishes

// At a specific time
tl.to(".box1", { x: 100 }, 2.5); // Starts at 2.5 seconds
```

## ScrollTrigger Fundamentals

### Basic Scroll Animation

```javascript
gsap.registerPlugin(ScrollTrigger);

gsap.to(".box", {
  x: 500,
  scrollTrigger: {
    trigger: ".box",
    start: "top center", // When top of trigger hits center of viewport
    end: "bottom center",
    markers: true, // Development only - shows start/end positions
    scrub: true, // Links animation to scrollbar
    toggleActions: "play none none reverse" // onEnter onLeave onEnterBack onLeaveBack
  }
});
```

### Start & End Positions

Format: `"[trigger position] [viewport position]"`

```javascript
// Common patterns
start: "top top"      // Trigger top hits viewport top
start: "top center"   // Trigger top hits viewport center (default)
start: "top bottom"   // Trigger top hits viewport bottom
start: "center center" // Trigger center hits viewport center

// With offsets
start: "top top+=100"   // 100px below viewport top
start: "top 80%"        // 80% down the viewport
end: "+=500"            // 500px after start position
end: "bottom top"       // Trigger bottom hits viewport top
```

### Scrubbing (Scroll-Synced Animation)

```javascript
// Boolean: Direct link to scrollbar (immediate)
scrub: true

// Number: Smoothing delay in seconds
scrub: 1  // Takes 1 second to "catch up" to scrollbar
scrub: 0.5 // Faster, tighter feel
```

### Toggle Actions

Control animation at four scroll points:

```javascript
toggleActions: "play pause resume reset"
// onEnter | onLeave | onEnterBack | onLeaveBack

// Actions: play, pause, resume, restart, reset, complete, reverse, none
```

Common patterns:
```javascript
toggleActions: "play none none none"       // Play once on enter
toggleActions: "play none none reverse"    // Play forward, reverse back
toggleActions: "play complete reverse reset" // Full control
toggleActions: "restart pause resume pause"  // Restart on each enter
```

## Common Patterns

Les sept recettes de base (fondu, épinglage, section horizontale, parallaxe, timeline au scroll, animations par lot, stagger) : [references/scrolltrigger_recipes.md](references/scrolltrigger_recipes.md). À ouvrir pour monter une animation au scroll ; la bibliothèque étendue est dans [references/common_patterns.md](references/common_patterns.md).

## Integration Patterns

Three.js et WebGL, React (`useGSAP`, timeline partagée), Locomotive Scroll : [references/integration_patterns.md](references/integration_patterns.md). À ouvrir seulement dans l'un de ces environnements.

## Advanced Techniques

Séquence d'images pilotée par le scroll, défilement vers une ancre, animations selon la media query : [references/scrolltrigger_recipes.md](references/scrolltrigger_recipes.md), après les recettes de base.

## Performance Best Practices

### 1. Use `will-change` CSS

```css
.animated-element {
  will-change: transform, opacity;
}
```

### 2. Limit Repaints

```javascript
// Good: Animate transform/opacity (GPU accelerated)
gsap.to(".box", { x: 100, opacity: 0.5 });

// Avoid: Animating layout properties
// gsap.to(".box", { width: 500, height: 300 }); // Causes reflow
```

### 3. Dispose of ScrollTriggers

```javascript
// Kill individual trigger
const trigger = ScrollTrigger.create({ /* ... */ });
trigger.kill();

// Kill all triggers
ScrollTrigger.getAll().forEach(t => t.kill());

// In React with cleanup
useGSAP(() => {
  const tween = gsap.to(".box", { /* ... */ });

  return () => {
    tween.kill();
  };
}, []);
```

### 4. Debounce Resize

ScrollTrigger handles this automatically, but for custom resize logic:

```javascript
let resizeTimer;
window.addEventListener("resize", () => {
  clearTimeout(resizeTimer);
  resizeTimer = setTimeout(() => {
    ScrollTrigger.refresh();
  }, 250);
});
```

### 5. Use `invalidateOnRefresh`

For dynamic values that change on resize:

```javascript
gsap.to(".box", {
  x: () => window.innerWidth / 2, // Dynamic value
  scrollTrigger: {
    trigger: ".box",
    start: "top center",
    invalidateOnRefresh: true // Recalculate x on resize
  }
});
```

## Common Pitfalls

### 1. Multiple Tweens on Same Element

```javascript
// Problem: Second tween conflicts with first
gsap.to('h1', { x: 100, scrollTrigger: { /* ... */ } });
gsap.to('h1', { x: 200, scrollTrigger: { /* ... */ } }); // Jumps!

// Solution 1: Use fromTo
gsap.fromTo('h1', { x: 100 }, { x: 200, scrollTrigger: { /* ... */ } });

// Solution 2: Use immediateRender: false
gsap.to('h1', { x: 200, immediateRender: false, scrollTrigger: { /* ... */ } });

// Solution 3: Apply ScrollTrigger to timeline
const tl = gsap.timeline({ scrollTrigger: { /* ... */ } });
tl.to('h1', { x: 100 })
  .to('h1', { x: 200 });
```

### 2. Not Using Loops for Multiple Elements

```javascript
// Wrong: Animates all at once
gsap.to('.section', {
  y: -100,
  scrollTrigger: { trigger: '.section', scrub: true }
});

// Right: Loop for individual triggers
gsap.utils.toArray('.section').forEach(section => {
  gsap.to(section, {
    y: -100,
    scrollTrigger: { trigger: section, scrub: true }
  });
});
```

### 3. Forgetting to Register Plugins

```javascript
import gsap from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';
import { ScrollToPlugin } from 'gsap/ScrollToPlugin';

gsap.registerPlugin(ScrollTrigger, ScrollToPlugin); // Must register!
```

### 4. Nested ScrollTriggers in Timelines

```javascript
// Wrong: ScrollTriggers on individual tweens in timeline
const tl = gsap.timeline();
tl.to('.box1', { x: 100, scrollTrigger: { /* ... */ } }) // Don't do this!
  .to('.box2', { y: 100, scrollTrigger: { /* ... */ } });

// Right: ScrollTrigger on parent timeline
const tl = gsap.timeline({
  scrollTrigger: { /* ... */ }
});
tl.to('.box1', { x: 100 })
  .to('.box2', { y: 100 });
```

## Easing Reference

```javascript
// Power easings (most common)
ease: "power1.out"  // Subtle deceleration
ease: "power2.inOut" // Smooth acceleration/deceleration
ease: "power3.in"   // Strong acceleration
ease: "power4.out"  // Very strong deceleration

// Special easings
ease: "elastic.out"  // Bouncy overshoot
ease: "back.out"     // Slight overshoot
ease: "bounce.out"   // Bouncing effect
ease: "circ.inOut"   // Circular motion feel
ease: "expo.inOut"   // Exponential (dramatic)

// Linear (for scrubbed scroll animations)
ease: "none"
```

## ScrollTrigger Methods

```javascript
// Refresh all ScrollTriggers (after DOM changes)
ScrollTrigger.refresh();

// Get all ScrollTriggers
const triggers = ScrollTrigger.getAll();

// Get specific trigger by ID
const st = ScrollTrigger.getById("myTrigger");

// Kill trigger
st.kill();

// Update trigger
st.scroll(500); // Programmatically set scroll position
st.enable();
st.disable();

// Global ScrollTrigger config
ScrollTrigger.config({
  limitCallbacks: true, // Improve performance
  syncInterval: 15 // Throttle scroll checks (ms)
});

// Debug mode
ScrollTrigger.defaults({
  markers: true // Show markers on all triggers
});
```

## Resources

This skill includes bundled resources:

### references/
- `api_reference.md`: Quick API reference (tween methods, timeline methods, ScrollTrigger properties)
- `easing_guide.md`: Visual easing reference with use cases
- `common_patterns.md`: Copy-paste patterns for common scenarios

Les scripts et assets de la skill d'origine ne sont pas copiés dans ce template : voir `docs/vendored-animation.md`, section « Périmètre retenu ».

## When to Use This Skill

Use this skill when:
- Creating smooth web animations
- Building scroll-driven experiences
- Implementing parallax effects
- Sequencing complex animations
- Animating DOM, SVG, Canvas, or WebGL
- Integrating animations with Three.js or React
- Building scrollytelling websites
- Creating interactive UI transitions

For Three.js-specific animations, also reference the **threejs-webgl** skill.
For React components with built-in animations, reference the **motion-framer** skill.

---

*Vendorisée depuis [claudedesignskills](https://github.com/freshtechbro/claudedesignskills) de freshtechbro (plugin `gsap-scrolltrigger`, skill `gsap-scrolltrigger` v1.0.0, licence MIT, © 2025 Claude Skills Project). Copie SKILL.md + references/ uniquement (pas de scripts ni d'assets, conformément à la politique de vendoring du template). Attribution, périmètre retenu et procédure de re-synchronisation : `docs/vendored-animation.md`.*
