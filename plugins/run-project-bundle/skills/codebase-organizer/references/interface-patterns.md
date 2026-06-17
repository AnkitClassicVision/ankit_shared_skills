# Common Interface and Seam Patterns

When deepening a module, the boundary design is more important than the internal refactor. These patterns solve common brownfield boundary problems.

## Adapter Pattern (Backward Compatibility)

**When to use**: The old interface has many consumers and you cannot update all callers at once.

**Structure**:
```
new-deep-module/
├── internal/          # new clean implementation
├── public-api.ts      # new simple interface
└── adapter.ts         # translates old calls to new internals
```

**Rule**: Old interface delegates to adapter. Adapter delegates to new internals. Once all callers migrate, delete adapter.

## Facade Pattern (Simplify Complex Subsystem)

**When to use**: A subsystem has grown too many public entry points. Consumers need one door.

**Structure**:
```
reports-subsystem/
├── internal/          # all the old report generators
├── report-facade.ts   # single entry: generateReport(config)
└── types.ts           # shared types only
```

**Rule**: Facade owns the public contract. All old generators are marked @internal.

## Port/Adapter (Hexagonal / Clean Architecture)

**When to use**: You need to swap external dependencies (database, API, file system) without touching business logic.

**Structure**:
```
orders/
├── domain/
│   ├── order.ts          # pure business logic
│   └── order-port.ts     # interface: OrderRepository
├── adapters/
│   ├── postgres-order-repo.ts
│   └── api-order-repo.ts
└── service.ts            # wires domain to adapter
```

**Rule**: Domain depends ONLY on ports (interfaces). Adapters depend on domain.

## Repository Pattern (Data Access Boundary)

**When to use**: Database queries are scattered across the codebase.

**Rule**: One repository per aggregate root. All queries for that aggregate go through the repository. No raw SQL outside repository.

## Anti-Corruption Layer

**When to use**: Integrating with a legacy or external system whose model does not match yours.

**Rule**: Never leak external types into your domain. Translate at the boundary. The ACL owns all conversion logic.

## Progressive Disclosure via Module Exports

**When to use**: A module has both public API and internal utilities that other modules in the same package need.

**Pattern**:
```typescript
// public-api.ts — what consumers see
export { processOrder } from './internal/order-processor';

// internal.ts — what sibling modules see
export * from './internal/order-processor';
export * from './internal/order-utils';
```

**Rule**: Package.json `exports` field controls what consumers can import. Internal paths are accessible only to sibling modules via direct file imports during migration.
