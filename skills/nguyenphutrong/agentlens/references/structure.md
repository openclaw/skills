# AgentLens Output Structure

## Directory Layout

```
.agentlens/
├── INDEX.md              # L0: Global routing table
├── AGENT.md              # Agent-specific instructions
├── modules/
│   └── {module-slug}/
│       ├── MODULE.md     # L1: Module overview
│       ├── outline.md    # L1: Symbol maps for large files
│       ├── memory.md     # L1: TODOs, warnings, rules
│       └── imports.md    # L1: File dependencies
└── files/
    └── {file-slug}.md    # L2: Deep docs for complex files
```

## File Purposes

### INDEX.md (Always Read First)
- Project name and description
- Complete list of modules with descriptions
- Entry points (main files)
- Hub files (heavily imported)
- High-priority warnings summary

### MODULE.md
- Module purpose and responsibility
- List of all files in the module
- File descriptions and line counts
- Language breakdown

### outline.md
- Symbol maps for large files (>500 lines)
- Functions, classes, structs, enums, traits
- Line numbers for quick navigation
- Visibility (public/private)

### memory.md
- TODO comments
- FIXME and BUG markers
- WARNING and SAFETY notes
- DEPRECATED markers
- Business rules (RULE, POLICY)

### imports.md
- Which files import which
- Internal dependencies within module
- Helps understand coupling

### files/{slug}.md (L2 - Complex Files Only)
- Generated for very complex files
- Detailed symbol documentation
- More context than outline.md
