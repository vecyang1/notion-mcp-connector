# Principles & Guidelines

## Database Schema Rules (Critical)
1. **NEVER rename properties** without explicit user approval — may break n8n/Zapier automations silently
2. **Semantic clarifications ≠ action** — "Rating = priority" is for interpretation only, do NOT rename
3. **Read before suggesting** — query actual data first; existing schema may already cover the use case
4. **Minimal schema changes** — exhaust existing fields before proposing new ones
5. **Always confirm before schema writes** — any `update-data-source` modifying property names/types requires explicit approval

## Naming Preservation
Always preserve original page/database names (e.g., "People ppl", "Health[OS]"). Users recognize their workspace by exact naming. Do not alias or shorten names in docs or logs.

## Pre-Edit Safety
Before any write, follow `references/pre-edit-safety.md`:
1. Check read-before-write matrix for required pre-read
2. Use local cache (`cache/`) to skip redundant API calls within TTL
3. Run safety gates: read-only guard → idempotency check → overwrite warning
4. After write: invalidate relevant cache file

## Property vs. Content Reasoning
- Data matching an existing property → update that property
- Structured data with no matching property → use sub-blocks, recommend adding property if highly reusable
- Always use correct format (ISO dates, etc.)

## Systemic Principles
1. Respect original intent — don't change *what* the skill does
2. Consolidate for agents — prefer clear CLIs over messy scripts
3. Traceability — leave breadcrumbs (comments, logs) for the next agent
4. Safety first — `cp file file.bak` if unsure
5. Token economy — move static setup info to references/
6. User wisdom > source — prioritize user customizations over upstream updates

## Self-Evolution (Autopoiesis)
After each session: "Did I learn a new pattern, fix a bug, or add a critical feature?"
- YES → update SKILL.md / references/ immediately (high-signal only)
- NO → do nothing
