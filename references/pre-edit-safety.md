# Pre-Edit Safety & Local Cache Reference

## 1. Read-Before-Write Matrix

| Operation | Required Pre-Read | MCP Call | Skip If |
|---|---|---|---|
| Update page property | Page properties | `API-retrieve-a-page` + `filter_properties` | Cache hit within TTL |
| Append block content | Block children | `API-get-block-children` | Cache hit within TTL |
| Replace/delete block | Block children | `API-get-block-children` | Never skip — always verify |
| Create page in DB | DB schema | `API-retrieve-a-database` | Cache hit within TTL |
| Update DB schema | DB schema | `API-retrieve-a-database` | Never skip — always verify |
| Query DB (read-only) | None | — | Always skip pre-read |

**Token economy rule**: Use `filter_properties` on `API-retrieve-a-page` to fetch only the specific property you intend to edit — not the full page object.

---

## 2. Local Cache

**Location**: `~/.claude/skills/notion-mcp-connector/cache/`

**File naming**:
- `{id}.page.json` — page properties snapshot
- `{id}.schema.json` — database schema snapshot
- `{id}.blocks.json` — block children snapshot

**File format**:
```json
{
  "fetched_at": "2026-03-01T00:32:13Z",
  "ttl_minutes": 30,
  "source": "API-retrieve-a-page",
  "data": { }
}
```

**TTL by object type**:
| Object | TTL | Rationale |
|---|---|---|
| DB schema | 120 min | Properties rarely change |
| Page properties | 30 min | Moderate change rate |
| Block content | 10 min | Can change frequently |

**Cache decision flow**:
```
Need to read X?
  → Cache file exists AND age < TTL?
      YES → use cache, skip API call
      NO  → fetch via MCP → save to cache → proceed
```

---

## 3. Safety Gates (Pre-Write Checks)

Run these in order before any write operation:

1. **Read-Only Guard** — if target property is in the DB's read-only list (e.g. formula, rollup, created_time), block and warn. Do not attempt patch.

2. **Idempotency Check** — if cached value already matches intended new value, skip the write entirely. Log: `[SKIP] value unchanged`.

3. **Overwrite Warning** — if block content exists at target location AND operation is "replace" (not "append"), surface current content to user before proceeding. Require implicit or explicit confirmation.

4. **Stale Cache on Destructive Ops** — for any delete or replace-block operation, always re-fetch (ignore cache) to ensure you have the latest state.

---

## 4. Token Economy Rules

- **Targeted property fetch**: always pass `filter_properties=[property_id]` to `API-retrieve-a-page` — never fetch the full page object just to read one field.
- **Session reuse**: within a single session, treat a fresh fetch as valid for its full TTL. Do not re-fetch the same object twice in one session unless a write occurred in between.
- **Schema from databases.md first**: if the DB schema is already documented in `references/databases.md`, use that as the source of truth for property names/types. Only call `API-retrieve-a-database` if the task involves a DB not listed there, or if schema drift is suspected.
- **Block reads are expensive**: only fetch block children when the edit explicitly targets page content (body text, sub-blocks). Property-only edits never need a block read.

---

## 5. Post-Write Cache Invalidation

After any successful write:
- Delete or overwrite the relevant cache file immediately
- On next read, a fresh fetch will repopulate it

This prevents stale cache from causing silent data drift on the next operation.

---

## 6. Discovery Logging

**Trigger**: any time a database ID, page ID, or URL surfaces during a session — from search results, API responses, user messages, or block content.

**Rule**: log it immediately to `references/databases.md` under the appropriate section (or a new one). Do not wait until end of session.

**Minimum log entry**:
```md
## {Title or Name}
- **Type**: database | page
- **ID**: `{id}`
- **URL**: {url if available}
- **Discovered**: {YYYY-MM-DD}
- **Purpose**: {one-line description if known, else "unknown"}
```

**What qualifies**:
- Any DB or page the user references by name or URL
- Any ID returned by `API-post-search` that the agent acts on
- Any parent page of a DB being edited
- Any related DB linked via a relation property

**What does NOT qualify**:
- Temporary/throwaway pages
- IDs that appear only in block content with no clear purpose
- Duplicates already in `databases.md`

**Before logging**: check `references/databases.md` for an existing entry with the same ID. If found, update it (add URL, correct title) rather than duplicate.

---

## 7. Relation Linking (Pre-Create / Pre-Edit)

When creating a new entry or editing an existing one in any DB that has relation fields:

1. **Identify all relation fields** from the DB schema (or `references/databases.md` if already documented)
2. **For each relation field**, ask: does the current context mention or imply a relevant linked record?
   - People mentioned by name → search `People ppl` DB, get page ID, link it
   - Topics/themes present → check Global Tags DB, link matching tags
   - Content, MEMOs, Notes → link if the entry references or generates them
3. **Do not leave relations empty by default** — actively populate what's contextually obvious
4. **Relation search order** (token-efficient):
   - Check `references/databases.md` for known IDs first (e.g. Tag ID Quick Reference)
   - Only call `API-post-search` or `API-query-data-source` if ID is not cached locally

**Example — 每日复盘 entry**: always consider linking People, Tags, Content, MEMOs based on what the entry is about. A diary entry about a person should have that person linked under People.

---

## 8. Template & Pattern Learning

Before creating a new entry in any DB, sample 2–3 recent existing entries to learn the expected fill pattern:

```
API-query-data-source(db_id, sorts=[{last_edited_time, descending}], page_size=3)
```

From the sample, extract:
- Which properties are typically filled vs. left empty
- Which relation fields are commonly populated
- Tag/status patterns in use

Cache result as `{db_id}.pattern.json` with TTL 4 hours. Use it as the baseline for the new entry — don't create a structurally thinner entry than the existing ones.

**Also check for default templates**: if the DB has templates (via `API-list-data-source-templates`), fetch once and cache. Templates reveal the owner's intended structure — treat them as authoritative over inferred patterns.
