# Recettes Anime.js

*Section « Common Patterns » déplacée telle quelle depuis `SKILL.md` (claudedesignskills v1.0.0, licence MIT), pour garder le corps de la skill sous 500 lignes.*

## Table of Contents

- [Common Patterns](#common-patterns)
  - [1. Stagger Animation (Sequential Reveal)](#1-stagger-animation-sequential-reveal)
  - [2. Stagger from Center](#2-stagger-from-center)
  - [3. SVG Line Drawing](#3-svg-line-drawing)
  - [4. SVG Morphing](#4-svg-morphing)
  - [5. Timeline Sequence](#5-timeline-sequence)
  - [6. Keyframe Animation](#6-keyframe-animation)
  - [7. Scroll-Triggered Animation](#7-scroll-triggered-animation)

## Common Patterns

### 1. Stagger Animation (Sequential Reveal)

```javascript
anime({
  targets: '.stagger-element',
  translateY: [100, 0],
  opacity: [0, 1],
  delay: anime.stagger(100), // Increase delay by 100ms
  easing: 'easeOutQuad',
  duration: 600
})
```

### 2. Stagger from Center

```javascript
anime({
  targets: '.grid-item',
  scale: [0, 1],
  delay: anime.stagger(50, {
    grid: [14, 5],
    from: 'center', // Also: 'first', 'last', index, [x, y]
    axis: 'x'       // Also: 'y', null
  }),
  easing: 'easeOutQuad'
})
```

### 3. SVG Line Drawing

```javascript
anime({
  targets: 'path',
  strokeDashoffset: [anime.setDashoffset, 0],
  easing: 'easeInOutQuad',
  duration: 2000,
  delay: (el, i) => i * 250
})
```

### 4. SVG Morphing

```javascript
anime({
  targets: '#morphing-path',
  d: [
    { value: 'M10 80 Q 77.5 10, 145 80' }, // Start shape
    { value: 'M10 80 Q 77.5 150, 145 80' }  // End shape
  ],
  duration: 2000,
  easing: 'easeInOutQuad',
  loop: true,
  direction: 'alternate'
})
```

### 5. Timeline Sequence

```javascript
const tl = anime.timeline({
  easing: 'easeOutExpo',
  duration: 750
})

tl.add({
  targets: '.title',
  translateY: [-50, 0],
  opacity: [0, 1]
})
.add({
  targets: '.subtitle',
  translateY: [-30, 0],
  opacity: [0, 1]
}, '-=500')
.add({
  targets: '.button',
  scale: [0, 1],
  opacity: [0, 1]
}, '-=300')
```

### 6. Keyframe Animation

```javascript
anime({
  targets: '.element',
  keyframes: [
    { translateX: 100 },
    { translateY: 100 },
    { translateX: 0 },
    { translateY: 0 }
  ],
  duration: 4000,
  easing: 'easeInOutQuad',
  loop: true
})
```

### 7. Scroll-Triggered Animation

```javascript
const animation = anime({
  targets: '.scroll-element',
  translateY: [100, 0],
  opacity: [0, 1],
  easing: 'easeOutQuad',
  autoplay: false
})

window.addEventListener('scroll', () => {
  const scrollPercent = window.scrollY / (document.body.scrollHeight - window.innerHeight)
  animation.seek(animation.duration * scrollPercent)
})
```
