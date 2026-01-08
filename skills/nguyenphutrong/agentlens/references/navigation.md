# Navigation Patterns

## Pattern 1: Exploring a New Codebase

```
1. Read .agentlens/INDEX.md
   → Get list of all modules
   → Note entry points and hub modules

2. Pick relevant module from INDEX
   → Read modules/{slug}/MODULE.md
   → Understand module purpose and files

3. Need specific symbol?
   → Read modules/{slug}/outline.md
   → Find line number of function/class

4. Check for issues first?
   → Read modules/{slug}/memory.md
   → See TODOs, warnings before editing
```

## Pattern 2: Finding Where Something Is Defined

```
1. Start with INDEX.md
2. Search for keyword in module descriptions
3. Go to matching MODULE.md
4. Check outline.md for symbol locations
5. Read only the specific source lines needed
```

## Pattern 3: Understanding Dependencies

```
1. Read modules/{slug}/imports.md
2. See which files import what
3. Understand the dependency graph
4. Navigate to related modules as needed
```

## Pattern 4: Before Modifying Code

```
1. Read memory.md for the module
2. Check for:
   - TODO: Pending work
   - FIXME: Known bugs
   - WARNING: Dangerous areas
   - SAFETY: Critical invariants
   - DEPRECATED: Code to avoid
3. Understand the context before changes
```

## Token Efficiency Tips

- **Never read entire source files** in large codebases
- **Use outline.md** to find exact line numbers first
- **Read only relevant sections** of source code
- **Navigate hierarchically**: INDEX → MODULE → outline → source
- **Estimated savings**: 80-96% fewer tokens than reading raw source
