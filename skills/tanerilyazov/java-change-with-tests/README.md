# java-change-with-tests

What it is:
- A "minimal diff + tests + evidence" workflow for Java services.

Why it's useful:
- Makes agent-assisted work reviewable and reproducible.
- Prevents "it works on my chat" by requiring commands and results.

How to use:
- Use for any Java feature/refactor/bugfix.

## Example

**Input**:
```
Add a health check endpoint to the payments service.
```

**Output** (abbreviated):
```markdown
## Plan
1. Create HealthController with GET /health endpoint
2. Return simple JSON with status and timestamp
3. Add unit test for endpoint
4. Run tests to verify

## Files Changed
- `src/main/java/com/example/controllers/HealthController.java` (+25 lines)
  - New controller with @GetMapping("/health")
- `src/test/java/com/example/controllers/HealthControllerTest.java` (+35 lines)
  - MockMvc test for 200 response and JSON structure

## Commands Run
- `mvn test -Dtest=HealthControllerTest` → BUILD SUCCESS (3 tests passed)
- `mvn verify` → BUILD SUCCESS

## Risks
- None

## Follow-ups
- Consider adding detailed health checks (DB, external services) in future
```
