import json
import re


def parse_json(text: str) -> dict | None:
    if not text:
        return None

    text = re.sub(r"```json\s*", "", text)
    text = re.sub(r"```\s*$", "", text)
    text = text.strip()

    json_match = re.search(r"\{.*\}", text, flags=re.DOTALL)
    if not json_match:
        return None

    try:
        return json.loads(json_match.group())
    except json.JSONDecodeError:
        pass

    # Fallback: extract content field via regex
    content_match = re.search(
        r'"content"\s*:\s*"([^"]*(?:\\.[^"]*)*)"', text, re.DOTALL
    )
    if content_match:
        return {
            "content": content_match.group(1),
            "response_type": "general_query",
            "action_required": False,
            "suggested_command": None,
        }
    return None


def parse_response_parts(parts) -> dict | None:
    full_text = "".join(part.text for part in parts if hasattr(part, "text") and part.text)
    return parse_json(full_text)


def handle_function_call(part, response_type, action_required=True):
    fc = getattr(part, "function_call", None)
    args = getattr(fc, "args", None) if fc else None
    if not args:
        return None
    return {
        "content": f"**Command:** {args.get('command', '')}\n\n**Explanation:** {args.get('explanation', '')}",
        "response_type": response_type,
        "action_required": action_required,
        "suggested_command": args.get("command", ""),
    }
