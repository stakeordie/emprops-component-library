import DefaultTheme from 'vitepress/theme'
import type { Theme } from 'vitepress'
import ContractDiagram from '../components/ContractDiagram.vue'
import FullscreenDiagram from '../components/FullscreenDiagram.vue'

export default {
  extends: DefaultTheme,
  enhanceApp({ app }) {
    app.component('ContractDiagram', ContractDiagram)
    app.component('FullscreenDiagram', FullscreenDiagram)
  }
} satisfies Theme
