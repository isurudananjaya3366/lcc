# Frontend Development Guide

## Prerequisites

- **Node.js** 20.x LTS or later
- **pnpm** 8.x or later (`corepack enable && corepack prepare pnpm@latest`)
- **Docker** 24.x+ (optional, for containerized development)
- **Git** ≥ 2.40
- **VS Code** (recommended) with extensions from `.vscode/extensions.json`

## Getting Started

```bash
# Install dependencies
pnpm install

# Set up environment
cp .env.local.example .env.local
# Edit .env.local with your values

# Start development server
pnpm dev
```

Open [http://localhost:3000](http://localhost:3000).

## Development Workflow

1. Create a feature branch from `develop`
2. Run `pnpm dev` for hot-reloading development server
3. Write code following the project conventions
4. Run `pnpm type-check && pnpm lint` before committing
5. Husky pre-commit hooks run lint-staged automatically
6. Pre-push hook runs `pnpm type-check`

## Available Commands

| Command              | Purpose                           |
| -------------------- | --------------------------------- |
| `pnpm dev`           | Start dev server (Turbopack)      |
| `pnpm build`         | Production build                  |
| `pnpm start`         | Start production server           |
| `pnpm lint`          | Run ESLint                        |
| `pnpm lint:fix`      | Auto-fix ESLint issues            |
| `pnpm lint:strict`   | Strict lint (fail on warnings)    |
| `pnpm format`        | Format with Prettier              |
| `pnpm format:check`  | Check formatting (CI)             |
| `pnpm type-check`    | TypeScript check (`tsc --noEmit`) |
| `pnpm test`          | Run tests                         |
| `pnpm test:watch`    | Watch mode tests                  |
| `pnpm test:coverage` | Tests with coverage               |
| `pnpm clean`         | Remove `.next` and `out`          |
| `pnpm analyze`       | Bundle size analysis              |

## Code Conventions

- **File naming:** kebab-case (`user-profile.tsx`)
- **Component naming:** PascalCase (`UserProfile`)
- **Import paths:** Use `@/` aliases (`@/components`, `@/lib`, etc.)
- **TypeScript:** Strict mode mandatory
- **Formatting:** Prettier on save (configured in `.vscode/settings.json`)

## Docker Development

```bash
# From project root
docker compose up frontend

# Or build standalone
cd frontend
docker build -f ../docker/frontend/Dockerfile.dev -t lcc-frontend:dev .
docker run -p 3000:3000 -v $(pwd):/app lcc-frontend:dev
```

## Troubleshooting

| Issue                     | Solution                                      |
| ------------------------- | --------------------------------------------- |
| Port 3000 in use          | `lsof -i :3000` then `kill -9 <PID>`          |
| Module not found          | `pnpm clean && pnpm install`                  |
| Type errors               | `pnpm type-check` for details                 |
| Hot reload not working    | Restart dev server                             |
| Build failures            | Check console, clear `.next` cache             |
| Env variable undefined    | Check `.env.local` and rebuild                 |
| Node version mismatch     | Run `nvm use` (reads `.nvmrc`)                 |
| Git hooks not running     | Run `pnpm prepare` to reinstall Husky          |

## Testing Guide

```bash
# Run all tests
pnpm test

# Watch mode
pnpm test:watch

# Coverage report
pnpm test:coverage
```

- Tests live in `__tests__/` directories alongside source
- Use `vitest` for unit/integration tests
- Follow naming convention: `component-name.test.tsx`
- Coverage thresholds are configured in `vitest.config.ts`

## Build Process

```bash
# Development build (with source maps)
pnpm build

# Analyze bundle size
pnpm analyze

# Clean build artifacts
pnpm clean
```

- Output: `.next/` directory (standalone mode)
- Standalone output: `.next/standalone/` for Docker
- Static assets: `.next/static/`
- Build fails on TypeScript errors (`ignoreBuildErrors: false`)

## Common Tasks

### Adding a New Page

Create `app/(dashboard)/your-page/page.tsx` with a default export component.

### Adding a New Component

1. Create file in `components/ui/` (shared) or `components/modules/<feature>/` (feature-specific)
2. Use kebab-case filename, PascalCase component name
3. Export from the module's `index.ts` barrel file

### Adding Environment Variables

1. Add to `.env.local.example` with documentation
2. Add to `lib/env.ts` validation schema  
3. Add TypeScript type to `types/env.d.ts`
4. Use via `import { env } from '@/lib/env'`

### Installing a New Package

```bash
pnpm add <package>           # production dep
pnpm add -D <package>        # dev dep
```
