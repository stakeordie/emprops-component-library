import { defineConfig } from 'vitepress'
import { withMermaid } from 'vitepress-plugin-mermaid'
import type { DefaultTheme, UserConfig } from 'vitepress'

const config = defineConfig({
  cacheDir: '.vitepress/.cache',
  outDir: '.vitepress/dist',
  title: "Documentation",
  description: "Project Documentation",
  base: '/',
  lastUpdated: true,
  cleanUrls: true,
  head: [
    ['link', { rel: 'icon', type: 'image/png', href: '/images/favicon.png' }],
    ['link', { rel: 'stylesheet', href: '/css/styles.css' }]
  ],

  markdown: {
    lineNumbers: true,
    container: {
      tipLabel: 'Tip',
      warningLabel: 'Warning',
      dangerLabel: 'Danger',
      infoLabel: 'Info',
      detailsLabel: 'Details'
    }
  },

  mermaid: { // @ts-ignore -- Mermaid config using plain JS as per team guidelines
    theme: 'default',
    securityLevel: 'loose',
    startOnLoad: true,
    maxTextSize: 50000,
    flowchart: {
      useMaxWidth: false,
      htmlLabels: true
    },
    themeVariables: {
      nodeTextColor: '#000000',
      mainBkg: '#ffffff',
      textColor: '#000000',
      classFontColor: '#000000',
      labelTextColor: '#000000',
      stateLabelColor: '#000000',
      entityTextColor: '#000000',
      flowchartTextColor: '#000000'
    }
  },

  themeConfig: {
    // Search
    search: {
      provider: 'local'
    },
    logo: '/images/logo.png',
    
    // Social links
    socialLinks: [
      { icon: 'github', link: 'https://github.com/your-org/your-repo' }
    ],

    // Footer
    footer: {
      message: 'Released under the MIT License.',
      copyright: 'Copyright 2024'
    },
    
    nav: [
      { text: 'Home', link: '/' },
      { text: 'Guide', link: '/guide/' },
      { text: 'Examples', link: '/examples/' }
    ],

    sidebar: {
      '/': [
        {
          text: 'Getting Started',
          items: [
            { text: 'Overview', link: '/' },
            { text: 'Installation', link: '/installation' }
          ]
        }
      ],
      '/guide/': [
        {
          text: 'Guide',
          items: [
            { text: 'Overview', link: '/guide/' },
            { text: 'Configuration', link: '/guide/configuration' },
            { text: 'Markdown', link: '/guide/markdown' }
          ]
        }
      ],
      '/examples/': [
        {
          text: 'Examples',
          items: [
            { text: 'Overview', link: '/examples/' },
            { text: 'Mermaid', link: '/examples/mermaid' },
            { text: 'Advanced', link: '/examples/advanced' },
            { text: 'SubPage', link: '/examples/another-one-of-the-same' },
          ]
        }
      ]
    }
  },

  vite: {
    resolve: {
      alias: {
        '@': '/src'
      }
    }
  }
})

export default withMermaid(config)
