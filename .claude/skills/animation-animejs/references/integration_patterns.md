# Intégrations Anime.js et suivi de tracé

*Section « Integration Patterns » déplacée telle quelle depuis `SKILL.md` (claudedesignskills v1.0.0, licence MIT), pour garder le corps de la skill sous 500 lignes.*

## Table of Contents

- [Integration Patterns](#integration-patterns)
  - [With React](#with-react)
  - [With Vue](#with-vue)
  - [Path Following Animation](#path-following-animation)

## Integration Patterns

### With React

```javascript
import { useEffect, useRef } from 'react'
import anime from 'animejs'

function AnimatedComponent() {
  const ref = useRef(null)

  useEffect(() => {
    const animation = anime({
      targets: ref.current,
      translateX: 250,
      duration: 800,
      easing: 'easeInOutQuad'
    })

    return () => animation.pause()
  }, [])

  return <div ref={ref}>Animated</div>
}
```

### With Vue

```javascript
export default {
  mounted() {
    anime({
      targets: this.$el,
      translateX: 250,
      duration: 800
    })
  }
}
```

### Path Following Animation

```javascript
const path = anime.path('#motion-path')

anime({
  targets: '.element',
  translateX: path('x'),
  translateY: path('y'),
  rotate: path('angle'),
  easing: 'linear',
  duration: 2000,
  loop: true
})
```
