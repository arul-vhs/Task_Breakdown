# GoalPilot Frontend Client

This is the Next.js 15 client application for the GoalPilot AI Goal Operating System.

## OpenAPI Type Generation

To automatically generate TypeScript types from the running FastAPI backend, execute the following command:

```bash
npx openapi-typescript http://localhost:8000/api/v1/openapi.json -o src/types/generated/api.ts
```

This will output the Pydantic schemas as TS interfaces inside `src/types/generated/api.ts`.
