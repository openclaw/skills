# Patterns: Information Relationships

Patterns for organizing, relating, and surfacing content.

---

## What are Information Relationships?

How content connects, relates, and is organized. Good information architecture makes content findable and understandable.

**Core principle:** Users should always know where they are, how they got there, and where they can go.

---

## Breadcrumbs

**What:** Hierarchical trail showing location in site structure.

### Types

| Type | Use Case |
|------|----------|
| **Hierarchy-based** | Shows parent/child path (Home > Category > Item) |
| **History-based** | Shows pages visited (like browser back) |
| **Attribute-based** | Shows filters/selections applied |

### Benefits

- **Orientation** — Users know where they are
- **Efficiency** — Quick navigation to parent levels
- **Context** — Understand content hierarchy
- **Recovery** — Easy return to previous levels

### Implementation Guidelines

**DO:**
- Use for sites with 3+ hierarchy levels
- Link all but current page
- Use separator (/ or >) between levels
- Truncate long trails intelligently
- Position consistently (top of content area)

**DON'T:**
- Use for flat site structures
- Make current page a link
- Use breadcrumbs as primary navigation
- Show breadcrumbs on homepage
- Inconsistent placement across pages

### Breadcrumb Examples

**Standard:**
```
Home / Products / Electronics / Headphones
```

**Attribute-based:**
```
Headphones > Over-ear > Wireless > Sony
```

**Truncated:**
```
Home / ... / Category / Subcategory / Item
```

---

## Sitemaps & Information Architecture

**What:** Structured overview of all site content.

### Sitemap Types

| Type | Purpose |
|------|---------|
| **Visual sitemap** | Design/planning tool |
| **HTML sitemap** | User-facing page listing |
| **XML sitemap** | SEO, search engine crawling |

### IA Organization Schemes

| Scheme | Examples |
|--------|----------|
| **Alphabetical** | Directories, glossaries |
| **Chronological** | News, blog archives |
| **Geographical** | Store locators, regional content |
| **Topical** | Subject-based categories |
| **Task-based** | What users want to do |
| **Audience-based** | By user type (admin, user) |

### IA Principles

**DO:**
- Organize by user mental model
- Use card sorting to validate
- Limit depth (3-4 levels max)
- Use clear, descriptive labels
- Cross-link related content

**DON'T:**
- Organize by org structure
- Create deep hierarchies
- Use internal jargon
- Duplicate content in multiple places
- Forget search as navigation

---

## Tagging & Categorization

**What:** Metadata that makes content findable and relatable.

### Categories vs. Tags

| Categories | Tags |
|------------|------|
| Hierarchical | Flat |
| Mutually exclusive | Multiple allowed |
| Pre-defined | Often user-created |
| Broad classification | Specific descriptors |
| Navigation structure | Discovery/filtering |

### Implementation Guidelines

**DO:**
- Define clear taxonomy
- Limit tag proliferation (governance)
- Show related content via shared tags
- Allow multiple tags per item
- Make tags clickable (for discovery)

**DON'T:**
- Over-tag content
- Create overlapping categories
- Use inconsistent naming
- Hide tag functionality
- Ignore tag maintenance

### Tag UI Patterns

**Tag display:**
```
[UX Design] [Mobile] [Case Study]
```

**Tag filtering:**
```
Filter by tag:
☑ UX Design (24)
☐ Mobile (18)
☐ Case Study (12)
```

**Tag input:**
```
Tags: [UX Design ×] [Mobile ×] [Add tag...]
      Suggested: Case Study, Research
```

---

## Faceted Search & Filters

**What:** Multi-dimensional filtering to narrow results.

### Components

| Component | Function |
|-----------|----------|
| **Facets** | Filter categories (price, size, color) |
| **Values** | Options within facets |
| **Counts** | Number of results per value |
| **Applied filters** | Currently active filters |
| **Clear all** | Reset to unfiltered state |

### Benefits

- **Precision** — Find exactly what's needed
- **Exploration** — Discover by browsing facets
- **Transparency** — See how results are filtered
- **Control** — User-driven refinement

### Implementation Guidelines

**DO:**
- Show result counts per facet value
- Allow multiple selections within facets
- Update results immediately (or on apply)
- Show applied filters prominently
- Provide clear "reset all"

**DON'T:**
- Show zero-result facet values (or mark unavailable)
- Hide facet values users might need
- Create too many facets
- Remove facets that would narrow to zero
- Make filters hard to clear

### Faceted Search UI

```
Filters               [Clear all]

Price
○ Under $50 (120)
○ $50-$100 (85)
● $100-$200 (42)
○ Over $200 (23)

Brand
☑ Nike (35)
☑ Adidas (28)
☐ Puma (15)
☐ Under Armour (12)

[Show 42 results]
```

---

## Related Content

**What:** Surfacing connections between content.

### Types

| Type | Basis |
|------|-------|
| **Manual curation** | Editor-selected relations |
| **Automatic** | Shared tags, categories, keywords |
| **Behavioral** | "Users also viewed" |
| **Temporal** | "Recent" or "trending" |

### Placement

- End of content (post-consumption)
- Sidebar (during consumption)
- Inline (contextual mentions)
- Below fold (scroll to discover)

### Implementation Guidelines

**DO:**
- Show genuinely related content
- Limit quantity (3-5 items)
- Include visual preview
- Vary recommendation types
- Track click-through

**DON'T:**
- Show unrelated content
- Overwhelm with recommendations
- Use only one recommendation type
- Show same recommendations everywhere
- Link to outdated content

### Related Content UI

```
Related Articles

[Image] How to improve your UX process
        3 min read

[Image] Design systems for startups
        5 min read

[Image] User research on a budget
        4 min read
```

---

## Cross-Linking & Content Discovery

**What:** Connecting content through intentional links.

### Cross-Link Types

| Type | Purpose |
|------|---------|
| **See also** | Alternative content |
| **Learn more** | Deeper dive |
| **Prerequisites** | Required knowledge |
| **Next steps** | Sequential content |
| **Examples** | Illustrative content |

### Implementation Guidelines

**DO:**
- Link to genuinely useful content
- Use descriptive anchor text
- Open external links appropriately
- Maintain links (fix broken)
- Use bidirectional linking

**DON'T:**
- Use "click here" as anchor text
- Link excessively (every paragraph)
- Link to irrelevant pages
- Open all links in new tabs
- Create orphan pages (no inbound links)

### Link Patterns

**Inline:**
```
For more details, see our guide to [user research methods].
```

**Call-out:**
```
📚 Related: [Complete guide to design systems →]
```

**Footer:**
```
Learn more:
• User research fundamentals
• Conducting user interviews
• Analyzing research findings
```

---

## Search

**What:** Finding content through queries.

### Search Components

| Component | Function |
|-----------|----------|
| **Search box** | Query input |
| **Suggestions** | Autocomplete, recent, popular |
| **Results** | Matched content |
| **Filters** | Refine results |
| **Sort** | Order results |
| **No results** | Empty state handling |

### Implementation Guidelines

**DO:**
- Make search prominent
- Support autocomplete
- Show result count
- Highlight matched terms
- Handle no results gracefully
- Remember recent searches

**DON'T:**
- Hide search (especially on content-heavy sites)
- Require exact matches
- Show empty results without guidance
- Ignore typos/synonyms
- Make filters hard to find

### Search UI Patterns

**Search box:**
```
🔍 [Search products, articles...  ]
    Recent: shoes, headphones
    Popular: new arrivals, sale
```

**Search results:**
```
42 results for "wireless headphones"

[Filter by: Price ▼] [Category ▼] [Sort by: Relevance ▼]

Sony WH-1000XM5
Wireless noise-canceling **headphones** with...
$349 ★★★★★ (2,341)

AirPods Max
Premium **wireless headphones** from Apple...
$549 ★★★★☆ (1,892)
```

---

## Information Architecture Checklist

| Element | Implemented? |
|---------|--------------|
| ☐ Clear hierarchy (3-4 levels max) | |
| ☐ Breadcrumbs for deep content | |
| ☐ Consistent categorization | |
| ☐ Useful tagging system | |
| ☐ Effective search | |
| ☐ Faceted filtering where appropriate | |
| ☐ Related content surfacing | |
| ☐ Cross-linking strategy | |
| ☐ No orphan content | |
