# Recettes GSAP et ScrollTrigger

*Sections « Common Patterns » et « Advanced Techniques » déplacées telles quelles depuis `SKILL.md` (claudedesignskills v1.0.0, licence MIT), pour garder le corps de la skill sous 500 lignes.*

## Table of Contents

- [Common Patterns](#common-patterns)
  - [1. Fade In On Scroll](#1-fade-in-on-scroll)
  - [2. Pin Element While Scrolling](#2-pin-element-while-scrolling)
  - [3. Horizontal Scroll Section](#3-horizontal-scroll-section)
  - [4. Parallax Effect](#4-parallax-effect)
  - [5. Scroll-Triggered Timeline](#5-scroll-triggered-timeline)
  - [6. Batch Animations (Multiple Elements)](#6-batch-animations-multiple-elements)
  - [7. Staggered Animations](#7-staggered-animations)
- [Advanced Techniques](#advanced-techniques)
  - [Image Sequence Scrubbing](#image-sequence-scrubbing)
  - [Smooth Scroll to Element](#smooth-scroll-to-element)
  - [Conditional Animations (Media Queries)](#conditional-animations-media-queries)

## Common Patterns

### 1. Fade In On Scroll

```javascript
gsap.from(".fade-in", {
  opacity: 0,
  y: 50,
  duration: 1,
  scrollTrigger: {
    trigger: ".fade-in",
    start: "top 80%",
    end: "top 50%",
    scrub: 1,
    once: true // Only animate once
  }
});
```

### 2. Pin Element While Scrolling

```javascript
ScrollTrigger.create({
  trigger: ".panel",
  start: "top top",
  end: "+=500", // Pin for 500px of scrolling
  pin: true,
  pinSpacing: true // Add spacing (default true)
});
```

### 3. Horizontal Scroll Section

```javascript
const sections = gsap.utils.toArray(".panel");

gsap.to(sections, {
  xPercent: -100 * (sections.length - 1),
  ease: "none",
  scrollTrigger: {
    trigger: ".container",
    pin: true,
    scrub: 1,
    end: () => "+=" + document.querySelector(".container").offsetWidth
  }
});
```

### 4. Parallax Effect

```javascript
// Slower movement (background layer)
gsap.to(".bg", {
  y: 200,
  ease: "none",
  scrollTrigger: {
    trigger: ".section",
    start: "top bottom",
    end: "bottom top",
    scrub: true
  }
});

// Faster movement (foreground layer)
gsap.to(".fg", {
  y: -100,
  ease: "none",
  scrollTrigger: {
    trigger: ".section",
    start: "top bottom",
    end: "bottom top",
    scrub: true
  }
});
```

### 5. Scroll-Triggered Timeline

```javascript
const tl = gsap.timeline({
  scrollTrigger: {
    trigger: ".container",
    start: "top top",
    end: "+=500",
    scrub: 1,
    pin: true,
    snap: {
      snapTo: "labels", // Snap to timeline labels
      duration: { min: 0.2, max: 3 },
      delay: 0.2,
      ease: "power1.inOut"
    }
  }
});

tl.addLabel("start")
  .from(".title", { scale: 0.3, rotation: 45, autoAlpha: 0 })
  .addLabel("color")
  .from(".box", { backgroundColor: "#28a92b" })
  .addLabel("spin")
  .to(".box", { rotation: 360 })
  .addLabel("end");
```

### 6. Batch Animations (Multiple Elements)

```javascript
// Loop through multiple elements
gsap.utils.toArray(".box").forEach((box, i) => {
  gsap.from(box, {
    y: 100,
    opacity: 0,
    scrollTrigger: {
      trigger: box,
      start: "top 80%",
      end: "top 50%",
      scrub: 1
    }
  });
});

// Or use ScrollTrigger.batch
ScrollTrigger.batch(".box", {
  onEnter: batch => gsap.to(batch, { opacity: 1, y: 0, stagger: 0.15 }),
  onLeave: batch => gsap.set(batch, { opacity: 0 }),
  start: "top 80%",
  once: true
});
```

### 7. Staggered Animations

```javascript
gsap.from(".item", {
  y: 50,
  opacity: 0,
  duration: 0.8,
  stagger: 0.1, // 0.1s between each item
  scrollTrigger: {
    trigger: ".grid",
    start: "top 80%"
  }
});

// Advanced stagger
gsap.from(".item", {
  scale: 0,
  duration: 1,
  stagger: {
    each: 0.1,
    from: "center", // "start", "center", "end", "edges", or index number
    grid: "auto", // For grid layouts
    ease: "power2.inOut"
  }
});
```

## Advanced Techniques

### Image Sequence Scrubbing

```javascript
const canvas = document.querySelector("canvas");
const context = canvas.getContext("2d");

const images = [];
const imageCount = 147;
const currentFrame = { value: 0 };

for (let i = 0; i < imageCount; i++) {
  const img = new Image();
  img.src = `./frames/frame_${i.toString().padStart(4, '0')}.jpg`;
  images.push(img);
}

images[0].onload = () => {
  canvas.width = images[0].width;
  canvas.height = images[0].height;
  render();
};

function render() {
  context.clearRect(0, 0, canvas.width, canvas.height);
  context.drawImage(images[Math.floor(currentFrame.value)], 0, 0);
}

gsap.to(currentFrame, {
  value: imageCount - 1,
  snap: "value",
  ease: "none",
  scrollTrigger: {
    trigger: canvas,
    start: "top top",
    end: "+=500%",
    scrub: true,
    pin: true
  },
  onUpdate: render
});
```

### Smooth Scroll to Element

```javascript
gsap.registerPlugin(ScrollToPlugin);

// Scroll to element
gsap.to(window, {
  duration: 1,
  scrollTo: "#section2",
  ease: "power2.inOut"
});

// With offset
gsap.to(window, {
  duration: 1.5,
  scrollTo: { y: "#section2", offsetY: 50 },
  ease: "expo.inOut"
});

// Horizontal scroll
gsap.to(".container", {
  duration: 2,
  scrollTo: { x: 1000, autoKill: true }
});
```

### Conditional Animations (Media Queries)

```javascript
ScrollTrigger.matchMedia({
  // Desktop
  "(min-width: 800px)": function() {
    gsap.to(".box", {
      x: 500,
      scrollTrigger: {
        trigger: ".box",
        start: "top center",
        end: "bottom top",
        scrub: true
      }
    });
  },

  // Mobile
  "(max-width: 799px)": function() {
    gsap.to(".box", {
      y: 200,
      scrollTrigger: {
        trigger: ".box",
        start: "top 80%",
        scrub: 1
      }
    });
  }
});
```
