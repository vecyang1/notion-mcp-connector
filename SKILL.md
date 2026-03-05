---
name: notion-mcp-connector
description: Guide and tools for interacting with Notion via the Model Context Protocol (MCP) or Direct API. Use this skill when you need to read, search, edit, or automate workflows within a Notion workspace, including handling databases, pages, and specific integrations.
---

# Notion MCP Connector

## Setup & Connectivity

### Prerequisites
1. **Notion Integration Token**: Create an integration at https://www.notion.so/my-integrations
2. **Environment Variable**: Set `NOTION_TOKEN` with your integration token
3. **Share Databases**: Share each database/page with your integration (most common issue!)

### MCP Servers (Two Options)

#### 1. `claude_ai_Notion` (Recommended - Enhanced)
- **Source**: Anthropic's official enhanced Notion MCP
- **Features**:
  - Semantic search across workspace + connected sources (Slack, Drive, GitHub, Jira, Teams, etc.)
  - Enhanced Markdown format with structured XML tags (`<page>`, `<properties>`, `<content>`)
  - Ancestor path tracking (shows full page hierarchy)
  - Rich property handling (formulas, relations, rollups)
  - Data source management with SQL-like DDL syntax
  - Template support built-in
  - Discussion/comment management
- **Tools**: `notion-search`, `notion-fetch`, `notion-create-pages`, `notion-update-page`, `notion-move-pages`, `notion-create-database`, `notion-update-data-source`, `notion-create-comment`, `notion-get-comments`, etc.
- **Best for**: Search, complex queries, template operations, full-featured Notion automation

#### 2. `@notionhq/notion-mcp-server` (Basic)
- **Package**: `@notionhq/notion-mcp-server` (Official Notion API wrapper)
- **Env var**: `NOTION_TOKEN` (not `NOTION_API_KEY`)
- **Transport**: Stdio via `npx -y`
- **Best for**: Simple CRUD operations, direct API access

**Recommendation**: Use `claude_ai_Notion` exclusively and disable basic `notion` MCP to save tokens.

### Authorization (Most Common Issue)
Agents cannot see your workspace by default. Share each database/page with the integration:
1. Open DB/page → `...` → `Add connections` → select integration
2. **Error `object_not_found`** = resource not shared (99% of cases)

Each integration needs separate sharing. See `references/troubleshooting.md` for all error fixes.

## Decision Matrix: MCP vs CLI

| Action | Tool | Reason |
|---|---|---|
| Search | `claude_ai_Notion` `notion-search` | Semantic search + connected sources |
| Read page | `claude_ai_Notion` `notion-fetch` | Enhanced format with hierarchy |
| Query DB | `claude_ai_Notion` `notion-search` with filters | Native filters + date/creator filtering |
| Update property | `claude_ai_Notion` `notion-update-page` | Works fine |
| Create page/entry | `claude_ai_Notion` `notion-create-pages` | Native support with templates |
| Bulk operations | CLI `notion_fast_cli.py` | Faster, easier error handling |
| Comments/discussions | `claude_ai_Notion` `notion-create-comment` | Only available in enhanced MCP |

**Rule**: Default `claude_ai_Notion` for all operations. Use CLI only for bulk operations or when MCP fails.

### CLI Usage
```bash
# Search
python3 scripts/notion_fast_cli.py search "Query" [--type database|page]

# Create entry
python3 scripts/notion_fast_cli.py create-entry --db-id <DATABASE_ID> --title "Title" --tags "Tag1,Tag2"

# Update page
python3 scripts/notion_fast_cli.py update-page --page-id <PAGE_ID> --tags "NewTag"

# Get block children
python3 scripts/notion_fast_cli.py get-children --block-id <BLOCK_ID>
```

### notion-ops Local MCP
- **Server**: `notion-ops` (registered in `.mcp.json`)
- **Script**: `scripts/notion_ops.py`
- **Tools**: `search_notion`, `find_person_in_notion`, `create_person_in_notion`, `update_birthday_in_notion`, `append_notion_blocks`
- **Usage**: Run as MCP server with `python3 scripts/notion_ops.py --mcp`

## Configuration

### Database Registry
Create a `references/databases.md` file to track your database IDs and schemas:

```markdown
# My Databases

## Database Name
- **Database ID**: `your-database-id-here`
- **Purpose**: Description of what this database tracks
- **Key Fields**: List important properties
```

### Environment Variables
```bash
export NOTION_TOKEN="your_integration_token_here"
```

## References

Load these only when needed:

- **`references/enhanced-mcps.md`** — Enhanced MCP comparison: `claude_ai_Notion` vs basic, other potential enhanced MCPs
- **`references/databases.md`** — Your database IDs, schemas, and quick references
- **`references/troubleshooting.md`** — Error fixes (object_not_found, schema drift, SSL, etc.)
- **`references/workflows.md`** — Step-by-step workflows for common operations
- **`references/principles.md`** — Schema rules, naming preservation, self-evolution
- **`references/pre-edit-safety.md`** — Read-before-write matrix, local cache (TTL), safety gates, token economy rules

## Quick Start

1. Create Notion integration at https://www.notion.so/my-integrations
2. Set `NOTION_TOKEN` environment variable
3. Share your databases with the integration
4. Use MCP tools or CLI scripts to interact with Notion
5. Track your database IDs in `references/databases.md`
