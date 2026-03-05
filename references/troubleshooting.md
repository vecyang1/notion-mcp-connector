# Troubleshooting

## 1. object_not_found (Most Common)
**Cause**: Database/page not shared with the integration.
**Fix**: Open in Notion → `...` → `Add connections` → select integration. No restart needed.

## 2. Schema Drift / HTTP 400 Validation Error
**Symptom**: `database property text does not match filter multi_select`
**Fix**: Check actual property type in Notion, update filter payload:
- Tags: `multi_select: { "contains": "value" }`
- Text: `rich_text: { "contains": "value" }`
- Select: `select: { "equals": "value" }`

## 3. SSL Certificate Verify Failed
```python
import ssl
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE
```

## 4. Formula Properties Are Read-Only
**Symptom**: `property [X] is a formula and cannot be updated`
**Fix**: Update the *input* properties instead (e.g., update `Birthday` not `Age`).

## 5. API-post-page Serialization Bug (Page Creation)
**Scope**: Any `API-post-page` call with a `parent` object — both DB entries and child pages.
**Cause**: MCP serializes `parent` as string instead of object.
**Fix**: Use `notion_fast_cli.py` or direct curl instead. Reading/updating existing pages still works fine.

## 6. page_size Type Issue
Pass `page_size` as a number (`100`), not string (`"100"`). Max is 100; use `start_cursor` for pagination.
