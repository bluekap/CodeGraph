# High-Level Architecture
## Layer Dependency Graph
```mermaid
graph TD;
    backend_codegraph["backend/codegraph"] -->|3| backend_codegraph_analyzer["backend/codegraph/analyzer"];
    backend_codegraph_analyzer["backend/codegraph/analyzer"] -->|1| backend_codegraph_models["backend/codegraph/models"];
```
