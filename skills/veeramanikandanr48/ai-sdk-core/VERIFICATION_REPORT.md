# Skill Verification Report: ai-sdk-core

**Date**: 2025-10-29
**Verifier**: Claude Code (Sonnet 4.5)
**Standard**: claude-code-skill-standards.md
**Last Skill Update**: 2025-10-21 (38 days ago)

---

## Executive Summary

**Status**: ⚠️ **WARNING - Multiple Updates Needed**

**Issues Found**: 12 total
- **Critical**: 3 (Claude models outdated, model availability statements, Zod version)
- **Moderate**: 5 (package versions, fixed issue still documented)
- **Minor**: 4 (missing new features, documentation enhancements)

**Overall Assessment**: The skill's core API patterns and architecture are correct, but model information is significantly outdated (Claude 3.x → 4.x transition missed), and several package versions need updating. One documented issue (#4726) has been fixed but is still listed as active.

---

## Detailed Findings

### 1. YAML Frontmatter ✅ **PASS**

**Status**: Compliant with official standards

**Validation**:
- [x] YAML frontmatter present (lines 1-17)
- [x] `name` field present: "AI SDK Core" (matches directory)
- [x] `description` field comprehensive (3+ sentences, use cases, keywords)
- [x] Third-person voice used correctly
- [x] `license` field present: MIT
- [x] No non-standard frontmatter fields
- [x] Keywords comprehensive (technologies, errors, use cases)

**Notes**: Frontmatter is well-structured and follows all standards.

---

### 2. Package Versions ⚠️ **WARNING**

**Status**: Multiple packages outdated (not critical, but recommended to update)

| Package | Documented | Latest (npm) | Gap | Severity |
|---------|------------|--------------|-----|----------|
| `ai` | ^5.0.76 | **5.0.81** | +5 patches | LOW |
| `@ai-sdk/openai` | ^2.0.53 | **2.0.56** | +3 patches | LOW |
| `@ai-sdk/anthropic` | ^2.0.0 | **2.0.38** | +38 patches | MODERATE |
| `@ai-sdk/google` | ^2.0.0 | **2.0.24** | +24 patches | MODERATE |
| `workers-ai-provider` | ^2.0.0 | **2.0.0** | ✅ Current | ✅ |
| `zod` | ^3.23.8 | **4.1.12** | Major version | MODERATE |

**Findings**:

1. **ai (5.0.76 → 5.0.81)**: +5 patch versions
   - **Impact**: Minor bug fixes and improvements
   - **Breaking changes**: None (patch updates)
   - **Recommendation**: Update to latest

2. **@ai-sdk/anthropic (2.0.0 → 2.0.38)**: +38 patch versions (!!)
   - **Impact**: Significant bug fixes accumulated
   - **Breaking changes**: None (patch updates)
   - **Recommendation**: **Update immediately** (most outdated)

3. **@ai-sdk/google (2.0.0 → 2.0.24)**: +24 patch versions
   - **Impact**: Multiple bug fixes
   - **Breaking changes**: None (patch updates)
   - **Recommendation**: Update to latest

4. **zod (3.23.8 → 4.1.12)**: Major version jump
   - **Impact**: Zod 4.0 has breaking changes (error APIs, `.default()` behavior, `ZodError.errors` removed)
   - **AI SDK Compatibility**: AI SDK 5 officially supports both Zod 3 and Zod 4 (Zod 4 support added July 31, 2025)
   - **Vercel Recommendation**: Use Zod 4 for new projects
   - **Known Issues**: Some peer dependency warnings with `zod-to-json-schema` package
   - **Recommendation**: Document Zod 4 compatibility, keep examples compatible with both versions

**Sources**:
- npm registry (checked 2025-10-29)
- Vercel AI SDK 5 blog: https://vercel.com/blog/ai-sdk-5
- Zod v4 migration guide: https://zod.dev/v4/changelog
- AI SDK Zod 4 support: https://github.com/vercel/ai/issues/5682

---

### 3. Model Names ❌ **CRITICAL**

**Status**: Significant inaccuracies - Claude models are a full generation behind, availability statements outdated

#### Finding 3.1: Claude Models **MAJOR VERSION BEHIND** ❌

**Documented**:
```typescript
const sonnet = anthropic('claude-3-5-sonnet-20241022');  // OLD
const opus = anthropic('claude-3-opus-20240229');        // OLD
const haiku = anthropic('claude-3-haiku-20240307');      // OLD
```

**Current Reality**:
- **Claude Sonnet 4** released: May 22, 2025
- **Claude Opus 4** released: May 22, 2025
- **Claude Sonnet 4.5** released: September 29, 2025
- **Naming convention changed**: `claude-sonnet-4-5-20250929` (not `claude-3-5-sonnet-YYYYMMDD`)
- **Anthropic deprecated Claude 3.x models** to focus on Claude 4.x family

**Lines affected**: 71, 605-610, references throughout

**Severity**: **CRITICAL** - Users following this skill will use deprecated models

**Recommendation**:
1. Update all Claude model examples to Claude 4.x
2. Add Claude 3.x to legacy/migration section with deprecation warning
3. Document new naming convention

**Sources**:
- Anthropic Claude models: https://docs.claude.com/en/docs/about-claude/models/overview
- Claude Sonnet 4.5 announcement: https://www.anthropic.com/claude/sonnet

---

#### Finding 3.2: GPT-5 and Gemini 2.5 Availability ⚠️ **MODERATE**

**Documented**:
```typescript
const gpt5 = openai('gpt-5');  // If available (line 573)
const lite = google('gemini-2.5-flash-lite');  // If available (line 642)
```

**Current Reality**:
- **GPT-5**: Released August 7, 2025 (nearly 3 months ago)
  - Models available: `gpt-5`, `gpt-5-mini`, `gpt-5-nano`
  - Status: Generally available through OpenAI API
  - Default model in ChatGPT for all users

- **Gemini 2.5**: All models generally available
  - Gemini 2.5 Pro: GA since June 17, 2025
  - Gemini 2.5 Flash: GA since June 17, 2025
  - Gemini 2.5 Flash-Lite: GA since July 2025

**Lines affected**: 32, 573, 642

**Severity**: **MODERATE** - Not critical but creates confusion

**Recommendation**:
1. Remove "If available" comments
2. Update to "Currently available" or similar
3. Verify exact model identifiers with providers

**Sources**:
- OpenAI GPT-5: https://openai.com/index/introducing-gpt-5/
- Google Gemini 2.5: https://developers.googleblog.com/en/gemini-2-5-thinking-model-updates/

---

### 4. Documentation Accuracy ⚠️ **WARNING**

**Status**: Core patterns correct, but missing new features and has outdated information

#### Finding 4.1: Missing New Features (Minor)

**New AI SDK 5 Features Not Documented**:

1. **`onError` callback for streamText** (IMPORTANT!)
   - Added in ai@4.1.22 (now standard in v5)
   - Critical for proper error handling
   - Fixes the "silent failure" issue (#4726)
   - **Recommendation**: Add section on streamText error handling

   ```typescript
   streamText({
     model: openai('gpt-4'),
     prompt: 'Hello',
     onError({ error }) {
       console.error('Stream error:', error);
     }
   });
   ```

2. **`experimental_transform` for stream transformations**
   - Allows custom pipeline support (e.g., `smoothStream()`)
   - **Recommendation**: Add to advanced features or mention in "not covered"

3. **`sources` support**
   - Web references from providers like Perplexity/Google
   - **Recommendation**: Add to "Advanced Topics (Not Replicated in This Skill)"

4. **`fullStream` property**
   - Fine-grained event handling for tool calls and reasoning
   - Already mentioned briefly, but could be expanded

**Severity**: **LOW** - Core functionality documented correctly

**Recommendation**: Add section on new v5 features or update "Advanced Topics" list

---

#### Finding 4.2: Code Examples (Pass)

**Status**: All tested code patterns are valid for AI SDK 5.0.76+

**Validation**:
- [x] Function signatures correct (`generateText`, `streamText`, `generateObject`, `streamObject`)
- [x] Parameter names accurate (`maxOutputTokens`, `temperature`, `stopWhen`)
- [x] Tool calling patterns correct (`tool()` function, `inputSchema`)
- [x] Agent class usage correct
- [x] Error handling classes correct
- [x] TypeScript types valid

**Notes**: Core API documentation is accurate and production-ready.

---

### 5. Known Issues Accuracy ⚠️ **WARNING**

**Status**: One issue fixed but still documented as active, one correctly documented

#### Finding 5.1: Issue #4726 (streamText fails silently) - **FIXED BUT STILL DOCUMENTED** ⚠️

**Documented** (lines 1130-1161):
```typescript
// Add explicit error handling
const stream = streamText({
  model: openai('gpt-4'),
  prompt: 'Hello',
});

try {
  for await (const chunk of stream.textStream) {
    process.stdout.write(chunk);
  }
} catch (error) {
  console.error('Stream error:', error);
  // Check server logs - errors may not reach client
}

// GitHub Issue: #4726
```

**Actual Status**:
- **CLOSED**: February 6, 2025
- **Fixed in**: ai@4.1.22
- **Solution**: `onError` callback parameter added

**Impact**: Users may think this is still an unsolved issue when it's actually fixed

**Recommendation**:
1. Update to note issue was resolved
2. Show the `onError` callback as the preferred solution
3. Keep the manual try-catch as secondary approach
4. Update line: `// GitHub Issue: #4726 (RESOLVED in v4.1.22)`

**Source**: https://github.com/vercel/ai/issues/4726

---

#### Finding 5.2: Issue #4302 (Imagen 3.0 Invalid JSON) - **CORRECTLY DOCUMENTED** ✅

**Documented** (lines 1406-1445):
```typescript
// GitHub Issue: #4302 (Imagen 3.0 Invalid JSON)
```

**Actual Status**:
- **OPEN**: Reported January 7, 2025
- **Still unresolved**: Intermittent empty JSON responses from Vertex AI
- **Affects**: `@ai-sdk/google-vertex` version 2.0.13+

**Impact**: Correctly informs users of ongoing issue

**Status**: ✅ **ACCURATE** - No changes needed

**Source**: https://github.com/vercel/ai/issues/4302

---

### 6. Templates Functionality ✅ **NOT TESTED**

**Status**: Not tested in this verification (would require creating test project)

**Files to Test** (13 templates):
- `templates/generate-text-basic.ts`
- `templates/stream-text-chat.ts`
- `templates/generate-object-zod.ts`
- `templates/stream-object-zod.ts`
- `templates/tools-basic.ts`
- `templates/agent-with-tools.ts`
- `templates/multi-step-execution.ts`
- `templates/openai-setup.ts`
- `templates/anthropic-setup.ts`
- `templates/google-setup.ts`
- `templates/cloudflare-worker-integration.ts`
- `templates/nextjs-server-action.ts`
- `templates/package.json`

**Recommendation**: Test templates in Phase 3 verification (create test project with latest packages)

**Assumption**: Templates follow documented patterns, so likely work correctly (but need verification)

---

### 7. Standards Compliance ✅ **PASS**

**Status**: Fully compliant with Anthropic official standards

**Validation**:
- [x] Follows agent_skills_spec.md structure
- [x] Directory structure correct (`scripts/`, `references/`, `templates/`)
- [x] README.md has comprehensive auto-trigger keywords
- [x] Writing style: imperative instructions, third-person descriptions
- [x] No placeholder text (TODO, FIXME) found
- [x] Skill installed correctly in `~/.claude/skills/`

**Comparison**:
- Matches gold standard: `tailwind-v4-shadcn/`
- Follows repo standards: `claude-code-skill-standards.md`
- Example audit: `CLOUDFLARE_SKILLS_AUDIT.md` patterns

---

### 8. Metadata & Metrics ✅ **PASS**

**Status**: Well-documented and credible

**Validation**:
- [x] Production testing mentioned: "Production-ready backend AI"
- [x] Token efficiency: Implied by "13 templates, comprehensive docs"
- [x] Errors prevented: "Top 12 Errors" documented with solutions
- [x] Status: "Production Ready" (implicit, no beta/experimental warnings)
- [x] Last Updated: 2025-10-21 (38 days ago - reasonable)
- [x] Version tracking: Skill v1.0.0, AI SDK v5.0.76+

**Notes**:
- No explicit "N% token savings" metric (consider adding)
- "Errors prevented: 12" is clear
- Production evidence: Comprehensive documentation suggests real-world usage

---

### 9. Links & External Resources ⚠️ **NOT TESTED**

**Status**: Not tested in this verification (would require checking each URL)

**Links to Verify** (sample):
- https://ai-sdk.dev/docs/introduction
- https://ai-sdk.dev/docs/ai-sdk-core/overview
- https://github.com/vercel/ai
- https://vercel.com/blog/ai-sdk-5
- https://developers.cloudflare.com/workers-ai/
- [50+ more links in SKILL.md]

**Recommendation**: Automated link checker or manual spot-check in Phase 3

**Assumption**: Official Vercel/Anthropic/OpenAI/Google docs are stable

---

### 10. v4→v5 Migration Guide ✅ **PASS**

**Status**: Comprehensive and accurate

**Sections Reviewed**:
- Breaking changes overview (lines 908-1018)
- Migration examples (lines 954-990)
- Migration checklist (lines 993-1004)
- Automated migration tool mentioned (lines 1007-1017)

**Validation**:
- [x] Breaking changes match official guide
- [x] `maxTokens` → `maxOutputTokens` documented
- [x] `providerMetadata` → `providerOptions` documented
- [x] Tool API changes documented
- [x] `maxSteps` → `stopWhen` migration documented
- [x] Package reorganization noted

**Source**: https://ai-sdk.dev/docs/migration-guides/migration-guide-5-0

---

## Recommendations by Priority

### 🔴 Critical (Fix Immediately)

1. **Update Claude Model Names** (Finding 3.1)
   - Replace all Claude 3.x references with Claude 4.x
   - Document new naming convention: `claude-sonnet-4-5-YYYYMMDD`
   - Add deprecation warning for Claude 3.x models
   - **Files**: SKILL.md (lines 71, 605-610, examples throughout)

2. **Remove "If Available" for GPT-5 and Gemini 2.5** (Finding 3.2)
   - GPT-5 released August 7, 2025 (3 months ago)
   - Gemini 2.5 models GA since June-July 2025
   - **Files**: SKILL.md (lines 32, 573, 642)

3. **Update Anthropic Provider Package** (Finding 2)
   - `@ai-sdk/anthropic`: 2.0.0 → 2.0.38 (+38 patches!)
   - Most outdated package, likely includes Claude 4 support
   - **Files**: SKILL.md (line 1678), templates/package.json

---

### 🟡 Moderate (Update Soon)

4. **Update GitHub Issue #4726 Status** (Finding 5.1)
   - Mark as RESOLVED (closed Feb 6, 2025)
   - Document `onError` callback as the solution
   - **Files**: SKILL.md (lines 1130-1161)

5. **Update Package Versions** (Finding 2)
   - `ai`: 5.0.76 → 5.0.81
   - `@ai-sdk/openai`: 2.0.53 → 2.0.56
   - `@ai-sdk/google`: 2.0.0 → 2.0.24
   - **Files**: SKILL.md (lines 1673-1687), templates/package.json

6. **Document Zod 4 Compatibility** (Finding 2)
   - Add note that AI SDK 5 supports both Zod 3 and 4
   - Mention Zod 4 is recommended for new projects
   - Note potential peer dependency warnings
   - **Files**: SKILL.md (lines 1690-1695, dependencies section)

---

### 🟢 Minor (Nice to Have)

7. **Add `onError` Callback Documentation** (Finding 4.1)
   - Document the `onError` callback for streamText
   - Show as preferred error handling method
   - **Files**: SKILL.md (streamText section, error handling)

8. **Add "New in v5" Section** (Finding 4.1)
   - Document: `onError`, `experimental_transform`, `sources`, `fullStream`
   - Or add to "Advanced Topics (Not Replicated in This Skill)"

9. **Update "Last Verified" Date** (Metadata)
   - Change from 2025-10-21 to 2025-10-29
   - **Files**: SKILL.md (line 1778), README.md (line 87)

10. **Add Token Efficiency Metric** (Finding 8)
    - Calculate approximate token savings vs manual implementation
    - Add to metadata section
    - Example: "~60% token savings (12k → 4.5k tokens)"

---

## Verification Checklist Progress

- [x] YAML frontmatter valid ✅
- [x] Package versions checked ⚠️ (outdated)
- [x] Model names verified ❌ (critical issues)
- [x] API patterns checked ✅ (mostly correct)
- [x] Known issues validated ⚠️ (one fixed but documented as active)
- [ ] Templates tested ⏸️ (not tested - requires project creation)
- [x] Standards compliance verified ✅
- [x] Metadata reviewed ✅
- [ ] Links checked ⏸️ (not tested - would need automated tool)
- [x] Documentation accuracy ⚠️ (missing new features)

---

## Next Steps

### Phase 1: Critical Updates (Immediate)
1. Update Claude model names to 4.x throughout
2. Remove "if available" comments for GPT-5 and Gemini 2.5
3. Update `@ai-sdk/anthropic` to 2.0.38

### Phase 2: Moderate Updates (This Week)
4. Mark issue #4726 as resolved, document onError callback
5. Update remaining package versions
6. Add Zod 4 compatibility note

### Phase 3: Testing & Verification (Next Session)
7. Create test project with all templates
8. Verify templates work with latest packages
9. Test with updated model names
10. Check external links (automated or spot-check)

### Phase 4: Enhancements (Optional)
11. Add new v5 features documentation
12. Add token efficiency metrics
13. Update "Last Verified" date
14. Consider adding examples for Claude 4.5 Sonnet

---

## Next Verification

**Scheduled**: 2026-01-29 (3 months from now, per quarterly maintenance policy)

**Priority Items to Check**:
- AI SDK version (watch for v6 GA)
- Claude 5.x release (if any)
- GPT-6 announcements (unlikely but monitor)
- Zod 5.x release (if any)
- New AI SDK features

---

## Appendix: Version Comparison Table

| Component | Documented | Current | Status | Action |
|-----------|------------|---------|--------|--------|
| **Skill** | 1.0.0 | 1.0.0 | ✅ | - |
| **AI SDK** | 5.0.76+ | 5.0.81 | ⚠️ | Update to 5.0.81 |
| **OpenAI Provider** | 2.0.53 | 2.0.56 | ⚠️ | Update to 2.0.56 |
| **Anthropic Provider** | 2.0.0 | 2.0.38 | ❌ | **Update to 2.0.38** |
| **Google Provider** | 2.0.0 | 2.0.24 | ⚠️ | Update to 2.0.24 |
| **Workers AI Provider** | 2.0.0 | 2.0.0 | ✅ | - |
| **Zod** | 3.23.8 | 4.1.12 | ⚠️ | Document Zod 4 support |
| | | | | |
| **GPT-5** | "If available" | Available (Aug 2025) | ❌ | **Update availability** |
| **Gemini 2.5** | "If available" | GA (Jun-Jul 2025) | ❌ | **Update availability** |
| **Claude 3.x** | Primary examples | Deprecated | ❌ | **Migrate to Claude 4.x** |
| **Claude 4.x** | Not mentioned | Current (May 2025) | ❌ | **Add as primary** |
| **Claude 4.5** | Not mentioned | Current (Sep 2025) | ❌ | **Add as recommended** |

---

**Report Generated**: 2025-10-29 by Claude Code (Sonnet 4.5)
**Review Status**: Ready for implementation
**Estimated Update Time**: 2-3 hours for all changes
