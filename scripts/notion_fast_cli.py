#!/usr/bin/env python3
import os
import json
import argparse
import sys
import requests

# Configuration
NOTION_TOKEN = os.environ.get("NOTION_TOKEN")
if not NOTION_TOKEN:
    print("Error: NOTION_TOKEN environment variable not set", file=sys.stderr)
    print("Create an integration at https://www.notion.so/my-integrations", file=sys.stderr)
    sys.exit(1)

NOTION_VERSION = "2022-06-28"
BASE_URL = "https://api.notion.com/v1"

HEADERS = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Content-Type": "application/json",
    "Notion-Version": NOTION_VERSION
}

class NotionFastCLI:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(HEADERS)

    def _handle_response(self, response):
        try:
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            print(f"HTTP Error: {e}", file=sys.stderr)
            try:
                print(json.dumps(response.json(), indent=2), file=sys.stderr)
            except:
                print(response.text, file=sys.stderr)
            sys.exit(1)

    def search(self, query, filter_type=None):
        """
        Search for pages or databases.
        filter_type: 'database' or 'page' (optional)
        """
        url = f"{BASE_URL}/search"
        payload = {
            "query": query,
            "sort": {"direction": "descending", "timestamp": "last_edited_time"}
        }
        if filter_type:
            payload["filter"] = {"value": filter_type, "property": "object"}

        return self._handle_response(self.session.post(url, json=payload))

    def create_database_entry(self, database_id, properties):
        """
        Create a new page in a database.
        Allows passing a dictionary for properties directly.
        """
        url = f"{BASE_URL}/pages"
        payload = {
            "parent": {"database_id": database_id},
            "properties": properties
        }
        return self._handle_response(self.session.post(url, json=payload))

    def update_page(self, page_id, properties):
        """
        Update properties of an existing page.
        """
        url = f"{BASE_URL}/pages/{page_id}"
        payload = {"properties": properties}
        return self._handle_response(self.session.patch(url, json=payload))

    def get_block_children(self, block_id):
        """
        Retrieve children blocks of a page or block.
        """
        url = f"{BASE_URL}/blocks/{block_id}/children"
        return self._handle_response(self.session.get(url))

    def append_block_children(self, block_id, children):
        """
        Append children blocks to a page or block.
        """
        url = f"{BASE_URL}/blocks/{block_id}/children"
        payload = {"children": children}
        return self._handle_response(self.session.patch(url, json=payload))

def build_properties_from_args(args):
    """Helper to build properties dict from CLI args for simple use cases."""
    props = {}

    if hasattr(args, 'title') and args.title:
        title_prop = args.title_prop if hasattr(args, 'title_prop') and args.title_prop else "Name"
        props[title_prop] = {
            "title": [{"text": {"content": args.title}}]
        }

    if hasattr(args, 'url') and args.url:
        props["Url"] = {"url": args.url}

    if hasattr(args, 'tags') and args.tags:
        tag_list = [{"name": t.strip()} for t in args.tags.split(",")]
        props["Tag"] = {"multi_select": tag_list}

    if hasattr(args, 'text') and args.text:
        props["Text"] = {
            "rich_text": [{"text": {"content": args.text}}]
        }

    if hasattr(args, 'json_props') and args.json_props:
        try:
            json_p = json.loads(args.json_props)
            props.update(json_p)
        except json.JSONDecodeError:
            print("Error: Invalid JSON for --json-props", file=sys.stderr)
            sys.exit(1)

    return props

def main():
    parser = argparse.ArgumentParser(description="Notion Fast CLI - robust Notion operations")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # SEARCH
    search_parser = subparsers.add_parser("search", help="Search pages/databases")
    search_parser.add_argument("query", help="Query string")
    search_parser.add_argument("--type", choices=["database", "page"], help="Filter by object type")

    # CREATE ENTRY
    create_parser = subparsers.add_parser("create-entry", help="Create an entry in a database")
    create_parser.add_argument("--db-id", required=True, help="Target Database ID")
    create_parser.add_argument("--title", help="Title of the entry")
    create_parser.add_argument("--title-prop", default="Name", help="Name of the title property (default: Name)")
    create_parser.add_argument("--url", help="Value for 'Url' property")
    create_parser.add_argument("--tags", help="Comma-separated values for 'Tag' multi-select property")
    create_parser.add_argument("--text", help="Value for 'Text' rich_text property")
    create_parser.add_argument("--json-props", help="Raw JSON string for properties (merges with/overrides others)")

    # UPDATE PAGE
    update_parser = subparsers.add_parser("update-page", help="Update a page's properties")
    update_parser.add_argument("--page-id", required=True, help="Page ID to update")
    update_parser.add_argument("--title", help="New title")
    update_parser.add_argument("--url", help="New Url")
    update_parser.add_argument("--tags", help="New Tags (comma-separated)")
    update_parser.add_argument("--text", help="New Text")
    update_parser.add_argument("--json-props", help="Raw JSON string for properties")

    # GET CHILDREN
    children_parser = subparsers.add_parser("get-children", help="Get block/page children")
    children_parser.add_argument("--block-id", required=True, help="Block or Page ID")

    args = parser.parse_args()
    cli = NotionFastCLI()

    if args.command == "search":
        result = cli.search(args.query, args.type)
        print(json.dumps(result, indent=2, ensure_ascii=False))

    elif args.command == "create-entry":
        props = build_properties_from_args(args)
        if not props:
            print("Error: No properties provided. Use flags like --title or --json-props.", file=sys.stderr)
            sys.exit(1)
        result = cli.create_database_entry(args.db_id, props)
        print(json.dumps(result, indent=2, ensure_ascii=False))

    elif args.command == "update-page":
        props = build_properties_from_args(args)
        if not props:
            print("Error: No properties provided to update.", file=sys.stderr)
            sys.exit(1)
        result = cli.update_page(args.page_id, props)
        print(json.dumps(result, indent=2, ensure_ascii=False))

    elif args.command == "get-children":
        result = cli.get_block_children(args.block_id)
        print(json.dumps(result, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()
