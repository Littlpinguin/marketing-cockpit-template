# Recettes AOS de sections de page

*Section « Common Patterns » déplacée telle quelle depuis `SKILL.md` (claudedesignskills v1.0.0, licence MIT), pour garder le corps de la skill sous 500 lignes.*

## Table of Contents

- [Common Patterns](#common-patterns)
  - [1. Landing Page Hero Section](#1-landing-page-hero-section)
  - [2. Feature Cards Grid](#2-feature-cards-grid)
  - [3. Alternating Content Sections](#3-alternating-content-sections)
  - [4. Scroll-Triggered Testimonials](#4-scroll-triggered-testimonials)
  - [5. Custom Anchor Triggers](#5-custom-anchor-triggers)
  - [6. Sequential Animation Chain](#6-sequential-animation-chain)
  - [7. Image Gallery with Zoom Effects](#7-image-gallery-with-zoom-effects)

## Common Patterns

### 1. Landing Page Hero Section

```html
<section class="hero">
  <!-- Staggered heading words -->
  <h1
    data-aos="fade-down"
    data-aos-duration="800"
  >
    Welcome to the Future
  </h1>

  <!-- Delayed subheading -->
  <p
    data-aos="fade-up"
    data-aos-delay="200"
    data-aos-duration="600"
  >
    Transform your ideas into reality
  </p>

  <!-- CTA button -->
  <button
    data-aos="zoom-in"
    data-aos-delay="400"
    data-aos-duration="500"
  >
    Get Started
  </button>
</section>
```

### 2. Feature Cards Grid

```html
<div class="features-grid">
  <!-- Stagger cards with increasing delays -->
  <div
    class="feature-card"
    data-aos="fade-up"
    data-aos-duration="600"
    data-aos-delay="0"
  >
    <h3>Feature 1</h3>
    <p>Description...</p>
  </div>

  <div
    class="feature-card"
    data-aos="fade-up"
    data-aos-duration="600"
    data-aos-delay="100"
  >
    <h3>Feature 2</h3>
    <p>Description...</p>
  </div>

  <div
    class="feature-card"
    data-aos="fade-up"
    data-aos-duration="600"
    data-aos-delay="200"
  >
    <h3>Feature 3</h3>
    <p>Description...</p>
  </div>
</div>
```

### 3. Alternating Content Sections

```html
<!-- Content from left -->
<div class="section">
  <div
    class="content"
    data-aos="slide-right"
    data-aos-duration="800"
  >
    <h2>Section Title</h2>
    <p>Content slides in from left...</p>
  </div>
  <img
    src="image1.jpg"
    data-aos="fade-left"
    data-aos-delay="200"
  />
</div>

<!-- Content from right -->
<div class="section reverse">
  <img
    src="image2.jpg"
    data-aos="fade-right"
  />
  <div
    class="content"
    data-aos="slide-left"
    data-aos-duration="800"
    data-aos-delay="200"
  >
    <h2>Section Title</h2>
    <p>Content slides in from right...</p>
  </div>
</div>
```

### 4. Scroll-Triggered Testimonials

```html
<div class="testimonials">
  <div
    class="testimonial"
    data-aos="zoom-in"
    data-aos-duration="500"
  >
    <blockquote>"Amazing product!"</blockquote>
    <cite>- John Doe</cite>
  </div>

  <div
    class="testimonial"
    data-aos="zoom-in"
    data-aos-duration="500"
    data-aos-delay="100"
  >
    <blockquote>"Exceeded expectations"</blockquote>
    <cite>- Jane Smith</cite>
  </div>
</div>
```

### 5. Custom Anchor Triggers

Trigger animations based on a different element's scroll position:

```html
<!-- Fixed sidebar animates based on main content scroll -->
<div class="main-content">
  <div id="trigger-point" data-aos-id="sidebar-trigger">
    <!-- Content -->
  </div>
</div>

<aside
  class="sidebar"
  data-aos="fade-left"
  data-aos-anchor="#trigger-point"
>
  Sidebar content
</aside>
```

### 6. Sequential Animation Chain

```html
<div class="animation-sequence">
  <!-- Step 1: Heading -->
  <h2
    data-aos="fade-down"
    data-aos-duration="600"
    data-aos-delay="0"
  >
    Our Process
  </h2>

  <!-- Step 2: Description -->
  <p
    data-aos="fade-up"
    data-aos-duration="600"
    data-aos-delay="200"
  >
    Follow these simple steps
  </p>

  <!-- Step 3-5: Process cards -->
  <div
    class="process-step"
    data-aos="flip-left"
    data-aos-delay="400"
  >
    Step 1
  </div>

  <div
    class="process-step"
    data-aos="flip-left"
    data-aos-delay="600"
  >
    Step 2
  </div>

  <div
    class="process-step"
    data-aos="flip-left"
    data-aos-delay="800"
  >
    Step 3
  </div>
</div>
```

### 7. Image Gallery with Zoom Effects

```html
<div class="gallery">
  <img
    src="photo1.jpg"
    data-aos="zoom-in-up"
    data-aos-duration="800"
  />
  <img
    src="photo2.jpg"
    data-aos="zoom-in-up"
    data-aos-duration="800"
    data-aos-delay="100"
  />
  <img
    src="photo3.jpg"
    data-aos="zoom-in-up"
    data-aos-duration="800"
    data-aos-delay="200"
  />
</div>
```
