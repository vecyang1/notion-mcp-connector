# Notion MCP Connector

A comprehensive skill for interacting with Notion via the Model Context Protocol (MCP) or Direct API. Includes tools for reading, searching, editing, and automating workflows within Notion workspaces.

## Features

- **Enhanced MCP Support**: Leverage Anthropic's `claude_ai_Notion` enhanced MCP for semantic search, rich property handling, and template support
- **CLI Tools**: Fast command-line interface for bulk operations and direct API access
- **Local MCP Server**: Custom MCP server with domain-specific helpers (e.g., People database management)
- **Comprehensive Documentation**: Troubleshooting guides, workflows, and best practices

## Quick Start

1. **Create Notion Integration**
   - Go to https://www.notion.so/my-integrations
   - Create a new integration and copy the token

2. **Set Environment Variable**
   ```bash
   export NOTION_TOKEN="your_integration_token_here"
   ```

3. **Share Databases with Integration**
   - Open each database/page in Notion
   - Click `...` → `Add connections` → select your integration
   - This is the most common issue - databases must be explicitly shared!

4. **Use the Tools**
   - MCP: Use `claude_ai_Notion` tools in Claude Code
   - CLI: Run scripts in `scripts/` directory
   - Local MCP: Run `python3 scripts/notion_ops.py --mcp`

## Installation

### For Claude Code Skills

```bash
# Copy to your skills directory
cp -r notion-mcp-connector ~/.claude/skills/

# Or symlink
ln -s /path/to/notion-mcp-connector ~/.claude/skills/notion-mcp-connector
```

### Dependencies

```bash
pip install requests mcp
```

## Usage

### CLI Examples

```bash
# Search for databases or pages
python3 scripts/notion_fast_cli.py search "Project" --type database

# Create a database entry
python3 scripts/notion_fast_cli.py create-entry \
  --db-id <DATABASE_ID> \
  --title "New Task" \
  --tags "urgent,work"

# Update a page
python3 scripts/notion_fast_cli.py update-page \
  --page-id <PAGE_ID> \
  --tags "completed"

# Get block children
python3 scripts/notion_fast_cli.py get-children --block-id <BLOCK_ID>
```

### MCP Server

```bash
# Run as MCP server
python3 scripts/notion_ops.py --mcp

# CLI usage
python3 scripts/notion_ops.py search "query"
python3 scripts/notion_ops.py find-person "John Doe" --db-id <DB_ID>
python3 scripts/notion_ops.py create-person "Jane Doe" --birthday 1990-01-01 --db-id <DB_ID>
```

## Configuration

### Database Registry

Track your database IDs in `references/databases.md`:

```markdown
## My Projects Database
- **Database ID**: `abc123...`
- **Purpose**: Track all projects
- **Key Fields**: Name, Status, Tags
```

### MCP Configuration

The `.mcp.json` file configures the local MCP server. Customize the `env` section with your database IDs:

```json
{
  "mcpServers": {
    "notion-ops": {
      "command": "python3",
      "args": ["scripts/notion_ops.py", "--mcp"],
      "env": {
        "NOTION_TOKEN": "your_token_here"
      }
    }
  }
}
```

## Documentation

- **SKILL.md**: Main skill documentation and decision matrix
- **references/enhanced-mcps.md**: Enhanced MCP comparison
- **references/troubleshooting.md**: Common errors and fixes
- **references/workflows.md**: Step-by-step workflows
- **references/principles.md**: Schema rules and best practices
- **references/pre-edit-safety.md**: Safety gates and token economy
- **references/databases.md**: Your database registry (customize this!)

## Common Issues

### `object_not_found` Error
**Solution**: Share the database/page with your integration. This is 99% of authorization issues.

### `NOTION_TOKEN not set`
**Solution**: Set the environment variable: `export NOTION_TOKEN="your_token"`

### Schema Drift
**Solution**: Check `references/databases.md` for correct property names and types.

See `references/troubleshooting.md` for more solutions.

## Contributing

This skill is designed to be customized for your workspace. Key customization points:

1. **Database IDs**: Update `references/databases.md` with your databases
2. **Domain Helpers**: Add custom functions in `scripts/notion_ops.py`
3. **CLI Commands**: Extend `scripts/notion_fast_cli.py` with new subcommands

## License

MIT License - feel free to use and modify for your needs.

## Credits

Created for the Claude Code community. Enhanced MCP support powered by Anthropic's `claude_ai_Notion`.
