# Intégration d'AOS dans React, Vue.js et Next.js

*Section « Integration Patterns » déplacée telle quelle depuis `SKILL.md` (claudedesignskills v1.0.0, licence MIT), pour garder le corps de la skill sous 500 lignes.*

## Table of Contents

- [Integration Patterns](#integration-patterns)
  - [React Integration](#react-integration)
  - [Vue.js Integration](#vuejs-integration)
  - [Next.js Integration](#nextjs-integration)

## Integration Patterns

### React Integration

**Basic Setup**:
```jsx
import { useEffect } from 'react';
import AOS from 'aos';
import 'aos/dist/aos.css';

function App() {
  useEffect(() => {
    AOS.init({
      duration: 800,
      once: true,
      offset: 100
    });
  }, []);

  return (
    <div>
      <h1 data-aos="fade-down">Welcome</h1>
      <p data-aos="fade-up">Content here</p>
    </div>
  );
}
```

**Refreshing on Route Changes**:
```jsx
import { useEffect } from 'react';
import { useLocation } from 'react-router-dom';
import AOS from 'aos';

function App() {
  const location = useLocation();

  useEffect(() => {
    AOS.init({ duration: 800 });
  }, []);

  // Refresh AOS on route change
  useEffect(() => {
    AOS.refresh();
  }, [location]);

  return <Routes>{/* routes */}</Routes>;
}
```

**Dynamic Content Updates**:
```jsx
import { useState, useEffect } from 'react';
import AOS from 'aos';

function DynamicList() {
  const [items, setItems] = useState([]);

  useEffect(() => {
    AOS.init();
  }, []);

  const addItem = () => {
    setItems([...items, { id: Date.now(), text: 'New Item' }]);

    // Refresh AOS to detect new elements
    setTimeout(() => AOS.refresh(), 50);
  };

  return (
    <div>
      <button onClick={addItem}>Add Item</button>
      <ul>
        {items.map((item) => (
          <li key={item.id} data-aos="fade-in">
            {item.text}
          </li>
        ))}
      </ul>
    </div>
  );
}
```

**Component Wrapper Pattern**:
```jsx
import AOS from 'aos';
import 'aos/dist/aos.css';

function AnimatedSection({ children, animation = "fade-up", delay = 0, ...props }) {
  return (
    <div
      data-aos={animation}
      data-aos-delay={delay}
      {...props}
    >
      {children}
    </div>
  );
}

// Usage
<AnimatedSection animation="slide-right" delay={200}>
  <h2>Animated Content</h2>
</AnimatedSection>
```

### Vue.js Integration

```vue
<template>
  <div>
    <h1 data-aos="fade-down">Vue + AOS</h1>
    <div
      v-for="(item, index) in items"
      :key="item.id"
      data-aos="fade-up"
      :data-aos-delay="index * 100"
    >
      {{ item.text }}
    </div>
  </div>
</template>

<script>
import AOS from 'aos';
import 'aos/dist/aos.css';

export default {
  mounted() {
    AOS.init({ duration: 800 });
  },
  updated() {
    // Refresh when component updates
    this.$nextTick(() => {
      AOS.refresh();
    });
  },
  data() {
    return {
      items: [/*...*/]
    };
  }
};
</script>
```

### Next.js Integration

```jsx
// pages/_app.js
import { useEffect } from 'react';
import AOS from 'aos';
import 'aos/dist/aos.css';

function MyApp({ Component, pageProps }) {
  useEffect(() => {
    AOS.init({
      duration: 800,
      once: true
    });
  }, []);

  return <Component {...pageProps} />;
}

export default MyApp;
```

```jsx
// pages/index.js
export default function Home() {
  return (
    <main>
      <h1 data-aos="fade-down">Next.js + AOS</h1>
      <p data-aos="fade-up">Server-side rendered content with animations</p>
    </main>
  );
}
```
