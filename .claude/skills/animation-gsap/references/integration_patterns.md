# Intégration de GSAP avec Three.js, React et Locomotive Scroll

*Section « Integration Patterns » déplacée telle quelle depuis `SKILL.md` (claudedesignskills v1.0.0, licence MIT), pour garder le corps de la skill sous 500 lignes.*

## Table of Contents

- [Integration Patterns](#integration-patterns)
  - [With Three.js / WebGL](#with-threejs--webgl)
  - [With React (useGSAP Hook)](#with-react-usegsap-hook)
  - [Sharing Timeline in React](#sharing-timeline-in-react)
  - [Locomotive Scroll Integration](#locomotive-scroll-integration)

## Integration Patterns

### With Three.js / WebGL

```javascript
import * as THREE from 'three';
import gsap from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';

gsap.registerPlugin(ScrollTrigger);

// Animate camera
gsap.to(camera.position, {
  x: 5,
  y: 3,
  z: 10,
  scrollTrigger: {
    trigger: "#section2",
    start: "top top",
    end: "bottom top",
    scrub: 1,
    onUpdate: () => camera.lookAt(scene.position)
  }
});

// Animate mesh rotation
gsap.to(mesh.rotation, {
  y: Math.PI * 2,
  scrollTrigger: {
    trigger: "#section3",
    start: "top bottom",
    end: "bottom top",
    scrub: true
  }
});

// Animate material properties
gsap.to(material, {
  opacity: 0,
  scrollTrigger: {
    trigger: "#section4",
    start: "top center",
    end: "center center",
    scrub: 1
  }
});
```

### With React (useGSAP Hook)

```javascript
import { useRef } from 'react';
import { useGSAP } from '@gsap/react';
import gsap from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';

gsap.registerPlugin(ScrollTrigger);

function Component() {
  const container = useRef();
  const box = useRef();

  useGSAP(() => {
    gsap.to(box.current, {
      x: 200,
      scrollTrigger: {
        trigger: box.current,
        start: "top center",
        end: "bottom center",
        scrub: true,
        markers: true
      }
    });
  }, { scope: container }); // Scoping for cleanup

  return (
    <div ref={container}>
      <div ref={box} className="box">Animated Box</div>
    </div>
  );
}
```

### Sharing Timeline in React

```javascript
function App() {
  const [tl, setTl] = useState();

  useGSAP(() => {
    const timeline = gsap.timeline();
    setTl(timeline);
  }, []);

  return (
    <div>
      <Box timeline={tl} index={0} />
      <Circle timeline={tl} index={1} />
    </div>
  );
}

function Box({ timeline, index }) {
  const ref = useRef();

  useGSAP(() => {
    timeline && timeline.to(ref.current, { x: 100 }, index * 0.1);
  }, [timeline, index]);

  return <div ref={ref} className="box" />;
}
```

### Locomotive Scroll Integration

```javascript
import LocomotiveScroll from 'locomotive-scroll';

const scroller = new LocomotiveScroll({
  el: document.querySelector('[data-scroll-container]'),
  smooth: true
});

ScrollTrigger.scrollerProxy("[data-scroll-container]", {
  scrollTop(value) {
    return arguments.length ? scroller.scrollTo(value, 0, 0) : scroller.scroll.instance.scroll.y;
  },
  getBoundingClientRect() {
    return {top: 0, left: 0, width: window.innerWidth, height: window.innerHeight};
  },
  pinType: document.querySelector("[data-scroll-container]").style.transform ? "transform" : "fixed"
});

ScrollTrigger.addEventListener("refresh", () => scroller.update());
ScrollTrigger.refresh();
```
