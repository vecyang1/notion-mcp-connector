import os
import json
import sys
import argparse
import requests
from mcp.server.fastmcp import FastMCP

# Configuration - reads from environment variable
NOTION_API_KEY = os.environ.get("NOTION_TOKEN")
if not NOTION_API_KEY:
    print("Warning: NOTION_TOKEN environment variable not set", file=sys.stderr)
    print("Create an integration at https://www.notion.so/my-integrations", file=sys.stderr)

NOTION_VERSION = "2022-06-28"

# Example database mappings - customize for your workspace
DATABASES = {
    "example_db": "your-database-id-here"
}

HEADERS = {
    "Authorization": f"Bearer {NOTION_API_KEY}",
    "Content-Type": "application/json",
    "Notion-Version": NOTION_VERSION
} if NOTION_API_KEY else {}

class NotionOps:
    def __init__(self):
        if not NOTION_API_KEY:
            raise ValueError("NOTION_TOKEN environment variable must be set")
        self.session = requests.Session()
        self.session.headers.update(HEADERS)

    def search(self, query):
        """Strategic Workspace Search."""
        url = "https://api.notion.com/v1/search"
        payload = {"query": query, "sort": {"direction": "descending", "timestamp": "last_edited_time"}}
        response = self.session.post(url, json=payload)
        response.raise_for_status()
        return response.json()

    def query_database(self, db_id, filter_obj=None):
        """Query a specific database with structured filters."""
        url = f"https://api.notion.com/v1/databases/{db_id}/query"
        payload = {}
        if filter_obj:
            payload["filter"] = filter_obj
        response = self.session.post(url, json=payload)
        response.raise_for_status()
        return response.json()

    def update_page_properties(self, page_id, properties):
        """Update properties of a specific page."""
        url = f"https://api.notion.com/v1/pages/{page_id}"
        payload = {"properties": properties}
        response = self.session.patch(url, json=payload)
        response.raise_for_status()
        return response.json()

    def append_blocks(self, block_id, blocks):
        """Append content blocks to a page or block."""
        url = f"https://api.notion.com/v1/blocks/{block_id}/children"
        payload = {"children": blocks}
        response = self.session.patch(url, json=payload)
        response.raise_for_status()
        return response.json()

    def create_page(self, db_id, properties):
        """Create a new page in a database."""
        url = "https://api.notion.com/v1/pages"
        payload = {
            "parent": {"database_id": db_id},
            "properties": properties
        }
        response = self.session.post(url, json=payload)
        response.raise_for_status()
        return response.json()

    def archive_page(self, page_id):
        """Archive (delete) a page."""
        url = f"https://api.notion.com/v1/pages/{page_id}"
        payload = {"archived": True}
        response = self.session.patch(url, json=payload)
        response.raise_for_status()
        return response.json()

    # --- Domain Specific Helpers (Example: People Database) ---

    def find_person(self, name, exact=True, db_id=None):
        """Locate a person in a People database.

        Args:
            name: Name to search for.
            exact: If True, uses 'equals'. If False, uses 'contains'.
            db_id: Database ID (required if not in DATABASES dict)

        Returns:
            List of matching records.
        """
        if not db_id:
            db_id = DATABASES.get("People", None)
            if not db_id:
                raise ValueError("Database ID required. Pass db_id parameter or set in DATABASES dict.")

        filter_condition = "equals" if exact else "contains"

        filter_obj = {
            "property": "Full Name",
            "title": {filter_condition: name}
        }
        results = self.query_database(db_id, filter_obj)
        return results.get("results", [])

    def create_person(self, name, birthday=None, note=None, force=False, db_id=None):
        """Create a new person record."""
        if not db_id:
            db_id = DATABASES.get("People", None)
            if not db_id:
                raise ValueError("Database ID required. Pass db_id parameter or set in DATABASES dict.")

        # Check for exact duplicate
        exact_matches = self.find_person(name, exact=True, db_id=db_id)
        if exact_matches:
            existing = exact_matches[0]
            return {"error": f"Person '{name}' already exists with ID: {existing['id']}"}

        # Check for partial/fuzzy duplicate (if not forcing creation)
        if not force:
            partial_matches = self.find_person(name, exact=False, db_id=db_id)
            if partial_matches:
                match_info = []
                for p in partial_matches:
                    props = p.get("properties", {})
                    full_name = props.get("Full Name", {}).get("title", [{}])[0].get("text", {}).get("content", "Unknown")
                    match_info.append(f"- {full_name} (ID: {p['id']})")

                return {
                    "error": "Possible duplicates found. Use --force to create anyway.",
                    "matches": match_info,
                    "requires_confirmation": True
                }

        properties = {
            "Full Name": {"title": [{"text": {"content": name}}]}
        }

        if birthday:
            properties["Birthday"] = {"date": {"start": birthday}}

        if note:
            properties["Note"] = {"rich_text": [{"text": {"content": note}}]}

        return self.create_page(db_id, properties)

    def update_birthday(self, name, date_str, db_id=None):
        """Specialized helper for updating birthdays."""
        results = self.find_person(name, exact=True, db_id=db_id)
        if not results:
            return {"error": f"Person '{name}' not found."}

        person = results[0]

        properties = {
            "Birthday": {"date": {"start": date_str}}
        }
        return self.update_page_properties(person["id"], properties)

# --- MCP Server Setup ---
mcp = FastMCP("notion-ops")

try:
    ops = NotionOps()
except ValueError as e:
    print(f"Warning: {e}", file=sys.stderr)
    ops = None

@mcp.tool()
def search_notion(query: str):
    """Search Notion workspace for pages or databases."""
    if not ops:
        return {"error": "NOTION_TOKEN not configured"}
    return ops.search(query)

@mcp.tool()
def find_person_in_notion(name: str, db_id: str = None):
    """Locate a record in a People database by name."""
    if not ops:
        return {"error": "NOTION_TOKEN not configured"}
    matches = ops.find_person(name, exact=False, db_id=db_id)
    return matches

@mcp.tool()
def create_person_in_notion(name: str, birthday: str = None, note: str = None, force: bool = False, db_id: str = None):
    """Create a new person record in Notion.

    Args:
        name: Full name of the person
        birthday: Optional birthday in YYYY-MM-DD format
        note: Optional note about the person
        force: Set to True to bypass fuzzy duplicate check
        db_id: Database ID (required if not configured in DATABASES)
    """
    if not ops:
        return {"error": "NOTION_TOKEN not configured"}
    return ops.create_person(name, birthday, note, force=force, db_id=db_id)

@mcp.tool()
def update_birthday_in_notion(name: str, date_iso: str, db_id: str = None):
    """Update the birthday property for a person in Notion (YYYY-MM-DD)."""
    if not ops:
        return {"error": "NOTION_TOKEN not configured"}
    return ops.update_birthday(name, date_iso, db_id=db_id)

@mcp.tool()
def append_notion_blocks(page_id: str, blocks_json: str):
    """Append blocks to a Notion page. blocks_json should be a list of blocks."""
    if not ops:
        return {"error": "NOTION_TOKEN not configured"}
    blocks = json.loads(blocks_json)
    return ops.append_blocks(page_id, blocks)

# --- CLI and Main ---

def main():
    parser = argparse.ArgumentParser(description="Notion Centralized Operations Tool")
    parser.add_argument("--mcp", action="store_true", help="Run as MCP server")

    subparsers = parser.add_subparsers(dest="command")

    # Search Command
    search_parser = subparsers.add_parser("search")
    search_parser.add_argument("query", help="Search query")

    # Update Birthday Command
    bday_parser = subparsers.add_parser("update-birthday")
    bday_parser.add_argument("name", help="Name of the person")
    bday_parser.add_argument("date", help="Date in YYYY-MM-DD format")
    bday_parser.add_argument("--db-id", help="Database ID")

    # Find Person Command
    find_parser = subparsers.add_parser("find-person")
    find_parser.add_argument("name", help="Name to find")
    find_parser.add_argument("--exact", action="store_true", help="Match name exactly")
    find_parser.add_argument("--db-id", help="Database ID")

    # Create Person Command
    create_parser = subparsers.add_parser("create-person")
    create_parser.add_argument("name", help="Name of the person")
    create_parser.add_argument("--birthday", help="Birthday in YYYY-MM-DD format")
    create_parser.add_argument("--note", help="Note about the person")
    create_parser.add_argument("--force", action="store_true", help="Force creation even if similar name exists")
    create_parser.add_argument("--db-id", help="Database ID")

    # Archive Page Command
    archive_parser = subparsers.add_parser("archive-page")
    archive_parser.add_argument("page_id", help="ID of the page to archive")

    args = parser.parse_args()

    if args.mcp:
        mcp.run()
        return

    if not ops:
        print("Error: NOTION_TOKEN environment variable must be set", file=sys.stderr)
        sys.exit(1)

    try:
        if args.command == "search":
            result = ops.search(args.query)
            print(json.dumps(result, indent=2, ensure_ascii=False))
        elif args.command == "update-birthday":
            result = ops.update_birthday(args.name, args.date, db_id=args.db_id if hasattr(args, 'db_id') else None)
            print(json.dumps(result, indent=2, ensure_ascii=False))
        elif args.command == "find-person":
            is_exact = args.exact
            result = ops.find_person(args.name, exact=is_exact, db_id=args.db_id if hasattr(args, 'db_id') else None)
            if result:
                print(json.dumps(result, indent=2, ensure_ascii=False))
            else:
                print(f"No results for '{args.name}'")
        elif args.command == "create-person":
            result = ops.create_person(args.name, args.birthday, args.note, force=args.force, db_id=args.db_id if hasattr(args, 'db_id') else None)
            print(json.dumps(result, indent=2, ensure_ascii=False))
        elif args.command == "archive-page":
            result = ops.archive_page(args.page_id)
            print(json.dumps(result, indent=2, ensure_ascii=False))
        else:
            if not args.mcp:
                parser.print_help()
    except Exception as e:
        print(f"Critical Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
