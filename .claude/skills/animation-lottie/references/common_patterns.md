# Recettes Lottie

*Section « Common Patterns » déplacée telle quelle depuis `SKILL.md` (claudedesignskills v1.0.0, licence MIT), pour garder le corps de la skill sous 500 lignes.*

## Table of Contents

- [Common Patterns](#common-patterns)
  - [1. Basic HTML Integration with dotLottie-web](#1-basic-html-integration-with-dotlottie-web)
  - [2. React Component with Controls](#2-react-component-with-controls)
  - [3. Event Listeners and Lifecycle Hooks](#3-event-listeners-and-lifecycle-hooks)
  - [4. Scroll-Driven Animation with lottie-react](#4-scroll-driven-animation-with-lottie-react)
  - [5. Hover-Triggered Segment Playback](#5-hover-triggered-segment-playback)
  - [6. Multi-Animation and Theme Support](#6-multi-animation-and-theme-support)
  - [7. Web Worker for Performance (DotLottieWorker)](#7-web-worker-for-performance-dotlottieworker)

## Common Patterns

### 1. Basic HTML Integration with dotLottie-web

```html
<!DOCTYPE html>
<html>
<head>
  <style>
    #canvas {
      width: 400px;
      height: 400px;
    }
  </style>
</head>
<body>
  <canvas id="canvas"></canvas>

  <script type="module">
    import { DotLottie } from 'https://cdn.jsdelivr.net/npm/@lottiefiles/dotlottie-web/+esm';

    new DotLottie({
      canvas: document.getElementById('canvas'),
      src: 'https://lottie.host/4db68bbd-31f6-4cd8-84eb-189de081159a/IGmMCqhzpt.lottie',
      autoplay: true,
      loop: true
    });
  </script>
</body>
</html>
```

### 2. React Component with Controls

```jsx
import React from 'react';
import { DotLottieReact } from '@lottiefiles/dotlottie-react';

const AnimatedButton = () => {
  const [dotLottie, setDotLottie] = React.useState(null);

  const handlePlay = () => dotLottie?.play();
  const handlePause = () => dotLottie?.pause();
  const handleStop = () => dotLottie?.stop();
  const handleSeek = (frame) => dotLottie?.setFrame(frame);

  return (
    <div>
      <DotLottieReact
        src="button-animation.lottie"
        loop
        autoplay={false}
        dotLottieRefCallback={setDotLottie}
        style={{ height: 200 }}
      />

      <div>
        <button onClick={handlePlay}>Play</button>
        <button onClick={handlePause}>Pause</button>
        <button onClick={handleStop}>Stop</button>
        <button onClick={() => handleSeek(30)}>Seek to frame 30</button>
      </div>
    </div>
  );
};
```

### 3. Event Listeners and Lifecycle Hooks

```jsx
import React, { useEffect } from 'react';
import { DotLottieReact } from '@lottiefiles/dotlottie-react';

const EventDrivenAnimation = () => {
  const [dotLottie, setDotLottie] = React.useState(null);

  useEffect(() => {
    if (!dotLottie) return;

    const onLoad = () => console.log('Animation loaded');
    const onPlay = () => console.log('Animation started');
    const onPause = () => console.log('Animation paused');
    const onComplete = () => console.log('Animation completed');
    const onFrame = ({ currentFrame }) => console.log('Frame:', currentFrame);

    dotLottie.addEventListener('load', onLoad);
    dotLottie.addEventListener('play', onPlay);
    dotLottie.addEventListener('pause', onPause);
    dotLottie.addEventListener('complete', onComplete);
    dotLottie.addEventListener('frame', onFrame);

    return () => {
      dotLottie.removeEventListener('load', onLoad);
      dotLottie.removeEventListener('play', onPlay);
      dotLottie.removeEventListener('pause', onPause);
      dotLottie.removeEventListener('complete', onComplete);
      dotLottie.removeEventListener('frame', onFrame);
    };
  }, [dotLottie]);

  return (
    <DotLottieReact
      src="animation.lottie"
      loop
      autoplay
      dotLottieRefCallback={setDotLottie}
    />
  );
};
```

### 4. Scroll-Driven Animation with lottie-react

```jsx
import Lottie from 'lottie-react';
import robotAnimation from './robot.json';

const ScrollAnimation = () => {
  const interactivity = {
    mode: 'scroll',
    actions: [
      {
        visibility: [0, 0.2],
        type: 'stop',
        frames: [0]
      },
      {
        visibility: [0.2, 0.45],
        type: 'seek',
        frames: [0, 45]
      },
      {
        visibility: [0.45, 1.0],
        type: 'loop',
        frames: [45, 60]
      }
    ]
  };

  return (
    <Lottie
      animationData={robotAnimation}
      style={{ height: 300 }}
      interactivity={interactivity}
    />
  );
};
```

### 5. Hover-Triggered Segment Playback

```jsx
import { useLottie, useLottieInteractivity } from 'lottie-react';
import likeButton from './like-button.json';

const HoverAnimation = () => {
  const lottieObj = useLottie({
    animationData: likeButton
  });

  const Animation = useLottieInteractivity({
    lottieObj,
    mode: 'cursor',
    actions: [
      {
        position: { x: [0, 1], y: [0, 1] },
        type: 'loop',
        frames: [45, 60]
      },
      {
        position: { x: -1, y: -1 },
        type: 'stop',
        frames: [45]
      }
    ]
  });

  return <div style={{ height: 300, border: '2px solid black' }}>{Animation}</div>;
};
```

### 6. Multi-Animation and Theme Support

```jsx
import { DotLottieReact } from '@lottiefiles/dotlottie-react';
import React, { useState, useEffect } from 'react';

const ThemedAnimation = () => {
  const [dotLottie, setDotLottie] = useState(null);
  const [animations, setAnimations] = useState([]);
  const [themes, setThemes] = useState([]);
  const [currentAnimationId, setCurrentAnimationId] = useState('');
  const [currentThemeId, setCurrentThemeId] = useState('');

  useEffect(() => {
    if (!dotLottie) return;

    const onLoad = () => {
      setAnimations(dotLottie.manifest.animations || []);
      setThemes(dotLottie.manifest.themes || []);
      setCurrentAnimationId(dotLottie.activeAnimationId);
      setCurrentThemeId(dotLottie.activeThemeId);
    };

    dotLottie.addEventListener('load', onLoad);
    return () => dotLottie.removeEventListener('load', onLoad);
  }, [dotLottie]);

  return (
    <div>
      <DotLottieReact
        src="multi-animation.lottie"
        dotLottieRefCallback={setDotLottie}
        animationId={currentAnimationId}
        themeId={currentThemeId}
      />

      {themes.length > 0 && (
        <select value={currentThemeId} onChange={(e) => setCurrentThemeId(e.target.value)}>
          {themes.map((theme) => (
            <option key={theme.id} value={theme.id}>{theme.id}</option>
          ))}
        </select>
      )}

      {animations.length > 0 && (
        <select value={currentAnimationId} onChange={(e) => setCurrentAnimationId(e.target.value)}>
          {animations.map((anim) => (
            <option key={anim.id} value={anim.id}>{anim.id}</option>
          ))}
        </select>
      )}
    </div>
  );
};
```

### 7. Web Worker for Performance (DotLottieWorker)

```javascript
import { DotLottieWorker } from '@lottiefiles/dotlottie-web';

// Offload animation rendering to a web worker
new DotLottieWorker({
  canvas: document.getElementById('canvas'),
  src: 'heavy-animation.lottie',
  autoplay: true,
  loop: true,
  workerId: 'worker-1' // Group multiple animations by worker
});

// Multiple animations in separate workers
new DotLottieWorker({
  canvas: document.getElementById('canvas-2'),
  src: 'animation-2.lottie',
  autoplay: true,
  loop: true,
  workerId: 'worker-2'
});
```
