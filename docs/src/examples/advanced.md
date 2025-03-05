# Advanced Examples

## Complex Mermaid Diagrams

### Git Workflow

<FullscreenDiagram>

```mermaid
gitGraph
    commit
    commit
    branch develop
    checkout develop
    commit
    commit
    checkout main
    merge develop
    commit
    commit
```

</FullscreenDiagram>

### Entity Relationship

```mermaid
erDiagram
    CUSTOMER ||--o{ ORDER : places
    ORDER ||--|{ LINE-ITEM : contains
    CUSTOMER }|..|{ DELIVERY-ADDRESS : uses
```

## Custom Components



```vue
<script setup>
import { ref } from 'vue'

const count = ref(0)
</script>

<template>
  <button @click="count++">
    Count is: {{ count }}
  </button>
</template>
```


## Advanced Configuration

<FullscreenDiagram>

```typescript
export default defineConfig({
  markdown: {
    config: (md) => {
      // Add custom markdown extensions
    }
  },
  vite: {
    plugins: [
      // Add custom Vite plugins
    ]
  }
})
```

</FullscreenDiagram>