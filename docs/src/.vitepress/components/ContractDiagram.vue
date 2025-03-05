<template>
  <div class="contract-diagram">
    <FullscreenDiagram>
      <slot></slot>
    </FullscreenDiagram>
  </div>
</template>

<script setup lang="ts">
import FullscreenDiagram from './FullscreenDiagram.vue'
</script>

<style scoped>
.contract-diagram {
  margin: 1rem 0;
}
</style>
