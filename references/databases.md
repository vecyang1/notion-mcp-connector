# Database Registry Template

Keep workspace-specific identifiers outside this community package. Use an ignored local file or your secret manager for real database IDs, while retaining this template as the shared reference.

## Example Database

- **Database ID**: `your-database-id-here`
- **Purpose**: Description of what this database tracks
- **Key writable fields**:
  - Name (title)
  - Status (status)
  - Tags (multi_select)
- **Read-only fields**: Created time, Last edited time

## How to find a database ID

1. Open the database in Notion and copy its link.
2. Read the 32-character ID from the link locally.
3. Store the ID in an ignored local configuration file or a secret manager; never add it to Git, issue text, screenshots, or public logs.

## Local registry template

Create `references/databases.local.md` (already ignored) if a task needs a human-readable private mapping:

```markdown
## <Database name>
- Database ID: <private-database-id>
- Purpose: <one-line purpose>
- Key fields: <human-readable schema notes>
```

The public skill remains portable; it receives a database ID through a command argument or a configured private environment.
