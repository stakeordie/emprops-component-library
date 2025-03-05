`<template>
  <div class="diagram-container">
    <div class="diagram" ref="diagramRef">
      <slot></slot>
    </div>
    <button class="expand-btn" @click="toggleExpand" :title="isExpanded ? 'Close' : 'Expand'">
      <svg v-if="!isExpanded" xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24">
        <path fill="currentColor" d="M7 14H5v5h5v-2H7v-3zm-2-4h2V7h3V5H5v5zm12 7h-3v2h5v-5h-2v3zM14 5v2h3v3h2V5h-5z"/>
      </svg>
      <svg v-else xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24">
        <path fill="currentColor" d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z"/>
      </svg>
    </button>

    <Teleport to="body">
      <div v-if="isExpanded" class="modal-overlay" @click.self="toggleExpand">
        <div class="modal-content">
          <div class="expanded-diagram">
            <div ref="expandedDiagramRef" v-html="diagramHTML"></div>
          </div>
          <div class="zoom-controls">
            <button @click="zoomOut" :disabled="zoom <= 0.5" title="Zoom Out">
              <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24">
                <path fill="currentColor" d="M19 13H5v-2h14v2z"/>
              </svg>
            </button>
            <span class="zoom-level">{{ Math.round(zoom * 100) }}%</span>
            <button @click="zoomIn" :disabled="zoom >= 3" title="Zoom In">
              <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24">
                <path fill="currentColor" d="M19 13h-6v6h-2v-6H5v-2h6V5h2v6h6v2z"/>
              </svg>
            </button>
            <button @click="resetZoom" title="Reset Zoom">
              <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24">
                <path fill="currentColor" d="M12 5V1L7 6l5 5V7c3.31 0 6 2.69 6 6s-2.69 6-6 6-6-2.69-6-6H4c0 4.42 3.58 8 8 8s8-3.58 8-8-3.58-8-8-8z"/>
              </svg>
            </button>
          </div>
          <button class="close-btn" @click="toggleExpand">
            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24">
              <path fill="currentColor" d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z"/>
            </svg>
          </button>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup>
import { ref, watch, onMounted, nextTick } from 'vue'
import panzoom from 'panzoom'

const isExpanded = ref(false)
const diagramRef = ref(null)
const expandedDiagramRef = ref(null)
const zoom = ref(1)
/**
 * Handles interactive pan and zoom functionality for the expanded diagram.
 * Uses panzoom library to provide smooth zooming and bounded panning.
 * - Zoom range: 50% to 300%
 * - Bounds: diagram can't be panned outside visible area
 * - Smooth transitions for zoom operations
 */
const panzoomInstance = ref(null)
const diagramHTML = ref('')

/**
 * Clones the original diagram content for use in the expanded view.
 * This preserves the original diagram state while allowing independent
 * manipulation in the expanded view.
 */
const cloneDiagram = () => {
  if (!diagramRef.value) return
  try {
    // Clone the rendered SVG directly
    diagramHTML.value = diagramRef.value.innerHTML
  } catch (error) {
    console.error('Failed to clone diagram:', error)
    diagramHTML.value = ''
  }
}

/**
 * Toggles the expanded view state and manages panzoom initialization/cleanup.
 * - Initializes panzoom when expanding
 * - Cleans up panzoom instance when closing
 * - Manages body scroll lock
 * - Resets zoom state on close
 */
const toggleExpand = () => {
  if (!isExpanded.value) {
    cloneDiagram()
  }
  isExpanded.value = !isExpanded.value
  if (isExpanded.value) {
    document.body.style.overflow = 'hidden'
    // Initialize panzoom after diagram is mounted
    nextTick(() => {
      if (expandedDiagramRef.value) {
        panzoomInstance.value = panzoom(expandedDiagramRef.value.firstChild, {
          bounds: true,
          boundsPadding: 0.1,
          minZoom: 0.5,
          maxZoom: 3
        })
      }
    })
  } else {
    document.body.style.overflow = ''
    if (panzoomInstance.value) {
      panzoomInstance.value.dispose()
      panzoomInstance.value = null
    }
    resetZoom()
  }
}

/**
 * Smoothly zooms in the diagram by 10%
 * Uses panzoom's smoothZoom for fluid animation
 * Respects maxZoom boundary of 300%
 */
const zoomIn = () => {
  if (panzoomInstance.value) {
    const currentZoom = panzoomInstance.value.getTransform().scale
    if (currentZoom < 3) {
      panzoomInstance.value.smoothZoom(0, 0, 1.1)
    }
  }
}

/**
 * Smoothly zooms out the diagram by 10%
 * Uses panzoom's smoothZoom for fluid animation
 * Respects minZoom boundary of 50%
 */
const zoomOut = () => {
  if (panzoomInstance.value) {
    const currentZoom = panzoomInstance.value.getTransform().scale
    if (currentZoom > 0.5) {
      panzoomInstance.value.smoothZoom(0, 0, 0.9)
    }
  }
}

/**
 * Resets the diagram to its initial state
 * - Sets zoom level to 100%
 * - Centers the diagram in the viewport
 */
const resetZoom = () => {
  if (panzoomInstance.value) {
    panzoomInstance.value.zoomAbs(0, 0, 1)
    panzoomInstance.value.moveTo(0, 0)
  }
}



// Reset zoom when closing
watch(isExpanded, (newValue) => {
  if (!newValue) {
    resetZoom()
  }
})
</script>

<style scoped>
.diagram-container {
  position: relative;
  width: 100%;
}

.diagram {
  width: 100%;
  background: white;
  padding: 1rem;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.expand-btn {
  position: absolute;
  top: 1rem;
  right: 1rem;
  background: white;
  border: 1px solid #ddd;
  border-radius: 4px;
  padding: 8px;
  cursor: pointer;
  opacity: 0.7;
  transition: opacity 0.2s;
  z-index: 10;
}

.expand-btn:hover {
  opacity: 1;
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background: rgba(0, 0, 0, 0.75);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  position: relative;
  background: white;
  padding: 2rem;
  border-radius: 8px;
  width: 95vw;
  height: 95vh;
  display: flex;
  flex-direction: column;
}

.expanded-diagram {
  flex: 1;
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
  background: white;
}

.expanded-diagram > div {
  cursor: move;
}

.expanded-diagram :deep(svg) {
  display: block;
  width: auto;
  height: auto;
  min-width: 1000px;
  max-width: 90%;
  max-height: 90%;
  margin: auto;
}

.expanded-diagram :deep(.mermaid) {
  display: flex;
  justify-content: center;
  align-items: center;
  width: 100%;
  height: 100%;
}

.zoom-controls {
  position: absolute;
  bottom: 1rem;
  left: 50%;
  transform: translateX(-50%);
  display: flex;
  align-items: center;
  gap: 0.5rem;
  background: white;
  padding: 0.5rem;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.zoom-controls button {
  background: #f0f0f0;
  border: 1px solid #ddd;
  border-radius: 4px;
  padding: 4px;
  cursor: pointer;
  opacity: 0.7;
  transition: opacity 0.2s;
}

.zoom-controls button:hover {
  opacity: 1;
}

.zoom-controls button:disabled {
  opacity: 0.3;
  cursor: not-allowed;
}

.zoom-level {
  min-width: 4rem;
  text-align: center;
  font-size: 0.9rem;
}

.close-btn {
  position: absolute;
  top: 1rem;
  right: 1rem;
  background: #f0f0f0;
  border: 1px solid #ddd;
  border-radius: 4px;
  padding: 8px;
  cursor: pointer;
  opacity: 0.7;
  transition: opacity 0.2s;
  z-index: 10;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.close-btn:hover {
  opacity: 1;
}
</style>
