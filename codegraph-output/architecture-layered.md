# Layered Architecture
## Layer Dependency Graph
```mermaid
graph TD;
    infra["infra"] -->|3| unknown["unknown"];
    infra["infra"] -->|1| domain["domain"];
    unknown["unknown"] -->|1| infra["infra"];
```