# Examples

This section contains various examples of what you can do with this documentation template.

## Mermaid Diagrams

### Sequence Diagram

```mermaid
sequenceDiagram
    participant User
    participant Docs
    participant Tests

    User->>Docs: Write documentation
    Docs->>Tests: Validate routes
    Tests-->>Docs: Report issues
    Docs-->>User: Show errors
```

### Class Diagram

<FullscreenDiagram>

```mermaid
classDiagram
    class Document {
        +String title
        +String content
        +validate()
        +render()
    }
    class Route {
        +String path
        +Boolean isDirectory
        +validate()
    }
    Document <|-- Route
```
</FullscreenDiagram>

## Code Blocks

```typescript
interface DocConfig {
  title: string;
  description: string;
  themeConfig: {
    nav: NavItem[];
    sidebar: SidebarConfig;
  }
}
```
