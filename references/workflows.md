# Workflows

## Finding a Database ID

1. **MCP Search**: `API-post-search` → filter `type: "database"` → extract `id`
2. **Browser URL**: `https://www.notion.so/[workspace]/[DATABASE_ID]?v=...`
3. **Pre-indexed**: Check `references/databases.md`

Always share the database with your integration before querying.

## Querying a Database

1. Discover DB ID (above)
2. Share with integration in Notion UI
3. `API-retrieve-a-database` → inspect schema
4. `API-query-data-source` with filters/sorts
5. Use `start_cursor` for >100 results

## Syncing / Importing Data

1. Check if target structure exists
2. Map input fields to Notion property types
3. Use CLI (not MCP) for page creation — see troubleshooting #5

## Centralizing Medical Records into Health[OS]

1. Share ALL source DBs with integration (Expenses, Diary, Tasks, etc.)
2. Query each source with `API-query-data-source` for health-related entries
3. Create Health[OS] entries via CLI:
   ```bash
   python3 scripts/notion_fast_cli.py create-entry ...
   ```
4. Append source links to new entries for traceability (images stay in original location)

> Always create the Health[OS] entry *before* linking — you need the new page ID first.

## Organizing Filtered Views (e.g., Chance Page)

When organizing notes in a filtered database view:

1. **Read schema first**: `notion-fetch` on data source URL to understand property types
   - Multi-select properties (e.g., `Tags`): JSON array format `"[\"Tag1\", \"Tag2\"]"`
   - Relation properties (e.g., `Product`): JSON array of page URLs `"[\"https://notion.so/...\"]"`
   - Select properties (e.g., `Pipeline`, `Rating`): Single string value

2. **Identify blank vs. substantive notes**:
   - Blank: `<blank-page>` or content = title only
   - Substantive: Has actual content beyond title

3. **Merge similar topics**:
   - Use `insert_content_after` to add sections to existing notes
   - Archive source notes after merging (set `Archived: "__YES__"`)

4. **Bind properties**:
   - Search related databases first (e.g., Product DB) to find relevant relations
   - Use JSON string format for arrays: `{"Tags": "[\"Product\", \"Management\"]"}`
   - Match existing property values from schema (don't create new options without user approval)

5. **Preserve filter integrity**:
   - Don't change `Entity` field if it's used in view filters
   - Archived notes automatically disappear from filtered views (if filter includes `Archived = false`)
