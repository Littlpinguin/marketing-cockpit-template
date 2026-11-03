# Intégration de Lottie avec GSAP, Framer Motion, Vue et Svelte

*Section « Integration Patterns » déplacée telle quelle depuis `SKILL.md` (claudedesignskills v1.0.0, licence MIT), pour garder le corps de la skill sous 500 lignes.*

## Table of Contents

- [Integration Patterns](#integration-patterns)
  - [With GSAP ScrollTrigger](#with-gsap-scrolltrigger)
  - [With Framer Motion](#with-framer-motion)
  - [Vue 3 Integration](#vue-3-integration)
  - [Svelte Integration](#svelte-integration)

## Integration Patterns

### With GSAP ScrollTrigger

```jsx
import Lottie from 'lottie-react';
import gsap from 'gsap';
import ScrollTrigger from 'gsap/ScrollTrigger';
import animationData from './animation.json';

gsap.registerPlugin(ScrollTrigger);

const GSAPLottieIntegration = () => {
  const lottieRef = React.useRef();

  React.useEffect(() => {
    const anim = lottieRef.current;
    if (!anim) return;

    // Sync Lottie with scroll
    gsap.to(anim, {
      scrollTrigger: {
        trigger: '#animation-section',
        start: 'top center',
        end: 'bottom center',
        scrub: 1,
        onUpdate: (self) => {
          const frame = Math.floor(self.progress * (anim.totalFrames - 1));
          anim.goToAndStop(frame, true);
        }
      }
    });
  }, []);

  return (
    <div id="animation-section" style={{ height: '200vh' }}>
      <Lottie
        lottieRef={lottieRef}
        animationData={animationData}
        autoplay={false}
        loop={false}
      />
    </div>
  );
};
```

### With Framer Motion

```jsx
import { motion } from 'framer-motion';
import { DotLottieReact } from '@lottiefiles/dotlottie-react';

const MotionLottie = () => {
  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.8 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.6 }}
    >
      <DotLottieReact
        src="animation.lottie"
        loop
        autoplay
        style={{ height: 400 }}
      />
    </motion.div>
  );
};
```

### Vue 3 Integration

```vue
<script setup>
import { DotLottieVue } from '@lottiefiles/dotlottie-vue';
</script>

<template>
  <DotLottieVue
    style="height: 500px; width: 500px"
    autoplay
    loop
    src="https://path-to-animation.lottie"
  />
</template>
```

### Svelte Integration

```svelte
<script lang="ts">
  import { DotLottieSvelte } from '@lottiefiles/dotlottie-svelte';
  import type { DotLottie } from '@lottiefiles/dotlottie-svelte';

  let dotLottie: DotLottie | null = null;

  function play() {
    dotLottie?.play();
  }
</script>

<DotLottieSvelte
  src="animation.lottie"
  loop={true}
  autoplay={true}
  dotLottieRefCallback={(ref) => dotLottie = ref}
/>

<button on:click={play}>Play</button>
```
