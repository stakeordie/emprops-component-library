# Documentation Template

A modern documentation starter template built with VitePress.

## Features

- **Markdown-based** - Write content in Markdown
- **Search** - Full-text search built-in
- **Diagrams** - Mermaid diagrams with fullscreen support
- **Customizable** - Easy to customize and extend
- **Responsive** - Works on all devices
- **Fast** - Built with Vite for optimal performance

## Getting Started

### Prerequisites

- Node.js 18+
- pnpm 10+

### Installation

```bash
# Clone the repository
git clone https://github.com/your-org/docs-template.git
cd docs-template

# Install dependencies
pnpm install

# Start the development server
pnpm docs:dev
```

## Building for Production

```bash
# Build the documentation site
pnpm docs:build

# Preview the production build
pnpm docs:preview
```

## Customization

- Edit `src/.vitepress/config.ts` to customize site configuration
- Add your content in Markdown files
- Customize components in `src/.vitepress/components`
- Add styles in `src/public/css/styles.css`

## License

MIT
