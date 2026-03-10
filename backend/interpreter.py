from __future__ import annotations

import os
import re
from typing import Optional

from pathlib import Path

try:
    from dotenv import load_dotenv
    # Always load .env from the backend directory regardless of cwd
    _env_path = Path(__file__).resolve().parent / ".env"
    load_dotenv(_env_path)
except ImportError:
    pass

try:
    import anthropic
    _AI_AVAILABLE = bool(os.environ.get("ANTHROPIC_API_KEY"))
except ImportError:
    _AI_AVAILABLE = False

_AI_SYSTEM_PROMPT = (
    "You translate English programming instructions into Python code.\n"
    "Rules:\n"
    "- Return ONLY valid Python code, no explanations, no markdown fences.\n"
    "- Use simple, beginner-friendly Python.\n"
    "- If the instruction is ambiguous, make a reasonable assumption.\n"
    "- Always include print() for any output the user expects to see.\n"
    "- Keep it concise."
)


class EnglishInterpreter:
    """Translates English instructions into Python code."""

    def __init__(self):
        self._ai_client = anthropic.Anthropic() if _AI_AVAILABLE else None
        self.patterns = [
            # Assignment: set X to N
            (
                r"^set\s+(\w+)\s+to\s+(.+)$",
                self._handle_set,
                "assignment",
            ),
            # Print: print X
            (
                r"^print\s+(.+)$",
                self._handle_print,
                "output",
            ),
            # Repeat: repeat N times / repeat N times:
            (
                r"^repeat\s+(\d+)\s+times\s*:?\s*$",
                self._handle_repeat,
                "loop",
            ),
            # Add: add N to X
            (
                r"^add\s+(.+)\s+to\s+(\w+)$",
                self._handle_add,
                "arithmetic",
            ),
            # Subtract: subtract N from X
            (
                r"^subtract\s+(.+)\s+from\s+(\w+)$",
                self._handle_subtract,
                "arithmetic",
            ),
            # Multiply: multiply X by N
            (
                r"^multiply\s+(\w+)\s+by\s+(.+)$",
                self._handle_multiply,
                "arithmetic",
            ),
            # If greater than
            (
                r"^if\s+(\w+)\s+is\s+greater\s+than\s+(.+)$",
                self._handle_if_gt,
                "conditional",
            ),
            # If less than
            (
                r"^if\s+(\w+)\s+is\s+less\s+than\s+(.+)$",
                self._handle_if_lt,
                "conditional",
            ),
            # If equal
            (
                r"^if\s+(\w+)\s+is\s+(.+)$",
                self._handle_if_eq,
                "conditional",
            ),
            # Create list/array: create list/array X with A, B, C
            (
                r"^create\s+(?:list|array)\s+(\w+)\s+with\s+(.+)$",
                self._handle_create_list,
                "assignment",
            ),
            # Append: add/append X to list/array Y
            (
                r"^(?:add|append)\s+(.+)\s+to\s+(?:list|array)\s+(\w+)$",
                self._handle_append,
                "operation",
            ),
            # Remove from list: remove X from list/array Y
            (
                r"^remove\s+(.+)\s+from\s+(?:list|array)\s+(\w+)$",
                self._handle_remove,
                "operation",
            ),
            # Find shortest/longest in list
            (
                r"^(?:find|get|output|print|show)\s+(?:the\s+)?shortest\s+(?:in|from|of)\s+(\w+)$",
                self._handle_shortest,
                "output",
            ),
            (
                r"^(?:find|get|output|print|show)\s+(?:the\s+)?longest\s+(?:in|from|of)\s+(\w+)$",
                self._handle_longest,
                "output",
            ),
            # Find smallest/largest (numeric)
            (
                r"^(?:find|get|output|print|show)\s+(?:the\s+)?(?:smallest|minimum|min)\s+(?:in|from|of)\s+(\w+)$",
                self._handle_min,
                "output",
            ),
            (
                r"^(?:find|get|output|print|show)\s+(?:the\s+)?(?:largest|maximum|max)\s+(?:in|from|of)\s+(\w+)$",
                self._handle_max,
                "output",
            ),
            # Length of list: get/find length of X
            (
                r"^(?:get|find|set)\s+(?:the\s+)?length\s+of\s+(\w+)$",
                self._handle_length,
                "output",
            ),
            # Sort list: sort X
            (
                r"^sort\s+(\w+)(?:\s+in\s+(ascending|descending)\s+order)?$",
                self._handle_sort,
                "operation",
            ),
            # Output/show/display: output X / show X / display X
            (
                r"^(?:output|show|display)\s+(.+)$",
                self._handle_print_alias,
                "output",
            ),
            # For each: for each X in Y
            (
                r"^for\s+each\s+(\w+)\s+in\s+(\w+)$",
                self._handle_for_each,
                "loop",
            ),
            # While loop: while X is greater/less/equal ...
            (
                r"^while\s+(\w+)\s+is\s+greater\s+than\s+(.+)$",
                self._handle_while_gt,
                "loop",
            ),
            (
                r"^while\s+(\w+)\s+is\s+less\s+than\s+(.+)$",
                self._handle_while_lt,
                "loop",
            ),
            (
                r"^while\s+(\w+)\s+is\s+not\s+(.+)$",
                self._handle_while_ne,
                "loop",
            ),
            # Divide: divide X by N
            (
                r"^divide\s+(\w+)\s+by\s+(.+)$",
                self._handle_divide,
                "arithmetic",
            ),
            # Get item from list: get item N from X
            (
                r"^get\s+item\s+(\d+)\s+from\s+(\w+)$",
                self._handle_get_item,
                "operation",
            ),
            # Store result: store EXPR in/as X
            (
                r"^store\s+(.+)\s+(?:in|as)\s+(\w+)$",
                self._handle_store,
                "assignment",
            ),
            # Concatenate / join: join X with SEP
            (
                r"^join\s+(\w+)\s+with\s+(.+)$",
                self._handle_join,
                "operation",
            ),
            # Input: ask/input X
            (
                r"^(?:ask|input|read)\s+(.+)$",
                self._handle_input,
                "input",
            ),
        ]

    # ── Pattern handlers ──────────────────────────────────────────────

    def _handle_set(self, match: re.Match) -> str:
        var = match.group(1)
        value = self._parse_value(match.group(2))
        return f"{var} = {value}"

    def _handle_print(self, match: re.Match) -> str:
        expr = match.group(1).strip()
        # If it looks like a quoted string keep as-is, otherwise treat as identifier/expression
        if (expr.startswith('"') and expr.endswith('"')) or (
            expr.startswith("'") and expr.endswith("'")
        ):
            return f"print({expr})"
        return f"print({expr})"

    def _handle_repeat(self, match: re.Match) -> str:
        count = match.group(1)
        return f"for _i in range({count}):"

    def _handle_add(self, match: re.Match) -> str:
        value = self._parse_value(match.group(1))
        var = match.group(2)
        return f"{var} += {value}"

    def _handle_subtract(self, match: re.Match) -> str:
        value = self._parse_value(match.group(1))
        var = match.group(2)
        return f"{var} -= {value}"

    def _handle_multiply(self, match: re.Match) -> str:
        var = match.group(1)
        value = self._parse_value(match.group(2))
        return f"{var} *= {value}"

    def _handle_if_gt(self, match: re.Match) -> str:
        var = match.group(1)
        value = self._parse_value(match.group(2))
        return f"if {var} > {value}:"

    def _handle_if_lt(self, match: re.Match) -> str:
        var = match.group(1)
        value = self._parse_value(match.group(2))
        return f"if {var} < {value}:"

    def _handle_if_eq(self, match: re.Match) -> str:
        var = match.group(1)
        value = self._parse_value(match.group(2))
        return f"if {var} == {value}:"

    def _handle_create_list(self, match: re.Match) -> str:
        var = match.group(1)
        items_raw = match.group(2)
        # Split by commas or "and"
        items = re.split(r"\s*,\s*|\s+and\s+", items_raw)
        parsed = [self._parse_list_item(item.strip()) for item in items if item.strip()]
        return f"{var} = [{', '.join(parsed)}]"

    def _handle_append(self, match: re.Match) -> str:
        value = self._parse_value(match.group(1))
        var = match.group(2)
        return f"{var}.append({value})"

    def _handle_remove(self, match: re.Match) -> str:
        value = self._parse_value(match.group(1))
        var = match.group(2)
        return f"{var}.remove({value})"

    def _handle_shortest(self, match: re.Match) -> str:
        var = match.group(1)
        return f"print(min({var}, key=len))"

    def _handle_longest(self, match: re.Match) -> str:
        var = match.group(1)
        return f"print(max({var}, key=len))"

    def _handle_min(self, match: re.Match) -> str:
        var = match.group(1)
        return f"print(min({var}))"

    def _handle_max(self, match: re.Match) -> str:
        var = match.group(1)
        return f"print(max({var}))"

    def _handle_length(self, match: re.Match) -> str:
        var = match.group(1)
        return f"print(len({var}))"

    def _handle_sort(self, match: re.Match) -> str:
        var = match.group(1)
        order = match.group(2)
        if order and order.lower() == "descending":
            return f"{var}.sort(reverse=True)"
        return f"{var}.sort()"

    def _handle_print_alias(self, match: re.Match) -> str:
        expr = match.group(1).strip()
        if (expr.startswith('"') and expr.endswith('"')) or (
            expr.startswith("'") and expr.endswith("'")
        ):
            return f"print({expr})"
        return f"print({expr})"

    def _handle_for_each(self, match: re.Match) -> str:
        item = match.group(1)
        collection = match.group(2)
        return f"for {item} in {collection}:"

    def _handle_while_gt(self, match: re.Match) -> str:
        var = match.group(1)
        value = self._parse_value(match.group(2))
        return f"while {var} > {value}:"

    def _handle_while_lt(self, match: re.Match) -> str:
        var = match.group(1)
        value = self._parse_value(match.group(2))
        return f"while {var} < {value}:"

    def _handle_while_ne(self, match: re.Match) -> str:
        var = match.group(1)
        value = self._parse_value(match.group(2))
        return f"while {var} != {value}:"

    def _handle_divide(self, match: re.Match) -> str:
        var = match.group(1)
        value = self._parse_value(match.group(2))
        return f"{var} /= {value}"

    def _handle_get_item(self, match: re.Match) -> str:
        index = match.group(1)
        var = match.group(2)
        return f"print({var}[{index}])"

    def _handle_store(self, match: re.Match) -> str:
        expr = match.group(1).strip()
        var = match.group(2)
        # Map English expressions to Python
        expr = re.sub(r"\bshortest\s+(?:in|from|of)\s+(\w+)\b", r"min(\1, key=len)", expr)
        expr = re.sub(r"\blongest\s+(?:in|from|of)\s+(\w+)\b", r"max(\1, key=len)", expr)
        expr = re.sub(r"\bsmallest\s+(?:in|from|of)\s+(\w+)\b", r"min(\1)", expr)
        expr = re.sub(r"\blargest\s+(?:in|from|of)\s+(\w+)\b", r"max(\1)", expr)
        expr = re.sub(r"\blength\s+of\s+(\w+)\b", r"len(\1)", expr)
        return f"{var} = {expr}"

    def _handle_join(self, match: re.Match) -> str:
        var = match.group(1)
        sep = self._parse_value(match.group(2))
        return f"print({sep}.join({var}))"

    def _handle_input(self, match: re.Match) -> str:
        var = match.group(1).strip()
        return f'{var} = input("{var}: ")'

    # ── Helpers ────────────────────────────────────────────────────────

    @staticmethod
    def _parse_list_item(raw: str) -> str:
        """Parse a list item — auto-quote bare words as strings."""
        raw = raw.strip()
        # Already quoted
        if (raw.startswith('"') and raw.endswith('"')) or (
            raw.startswith("'") and raw.endswith("'")
        ):
            return raw
        # Numeric
        try:
            int(raw)
            return raw
        except ValueError:
            pass
        try:
            float(raw)
            return raw
        except ValueError:
            pass
        # Boolean
        if raw.lower() in ("true", "false"):
            return raw.capitalize()
        # Bare word(s) → treat as string
        return f'"{raw}"'

    @staticmethod
    def _parse_value(raw: str) -> str:
        """Return a cleaned value string — numeric literal, quoted string, or identifier."""
        raw = raw.strip()
        # Integer
        try:
            int(raw)
            return raw
        except ValueError:
            pass
        # Float
        try:
            float(raw)
            return raw
        except ValueError:
            pass
        # Already quoted string
        if (raw.startswith('"') and raw.endswith('"')) or (
            raw.startswith("'") and raw.endswith("'")
        ):
            return raw
        # Bare string that contains spaces → wrap in quotes
        if " " in raw:
            return f'"{raw}"'
        # Otherwise treat as variable name / identifier
        return raw

    def _match_line(self, line: str) -> Optional[tuple]:
        """Try each pattern against the line. Returns (python_code, command_type) or None."""
        normalized = line.strip()
        # Collapse multiple spaces
        normalized = re.sub(r"\s+", " ", normalized)

        for pattern, handler, cmd_type in self.patterns:
            m = re.match(pattern, normalized, re.IGNORECASE)
            if m:
                return handler(m), cmd_type
        return None

    def _ai_translate(self, english: str) -> Optional[str]:
        """Use Claude to translate English that regex couldn't handle."""
        if not self._ai_client:
            return None
        try:
            response = self._ai_client.messages.create(
                model="claude-haiku-4-5-20251001",
                max_tokens=512,
                system=_AI_SYSTEM_PROMPT,
                messages=[{"role": "user", "content": english}],
            )
            code = response.content[0].text.strip()
            # Strip markdown fences if the model included them anyway
            if code.startswith("```"):
                code = re.sub(r"^```\w*\n?", "", code)
                code = re.sub(r"\n?```$", "", code)
            return code.strip()
        except Exception:
            return None

    # ── Public API ─────────────────────────────────────────────────────

    def classify(self, code: str) -> list[dict]:
        """Parse English code into classified instructions (used by /parse)."""
        lines = code.split("\n")
        instructions: list[dict] = []

        for idx, raw_line in enumerate(lines):
            stripped = raw_line.strip()
            if not stripped:
                continue

            result = self._match_line(stripped)
            if result:
                _, cmd_type = result
                instructions.append({"line": idx, "text": stripped, "type": cmd_type})
            else:
                instructions.append({"line": idx, "text": stripped, "type": "unknown"})

        return instructions

    def translate(self, code: str) -> tuple[list[dict], str]:
        """
        Translate English instructions into Python.

        Returns (translations, full_python_code).
        Each translation: {"english": ..., "python": ..., "line": ...}
        """
        lines = code.split("\n")
        translations: list[dict] = []
        python_lines: list[str] = []

        # Track indentation depth for generated Python
        indent_level = 0
        # Stack: each entry is the indent level to restore when the block closes
        block_stack: list[int] = []

        def _current_indent() -> str:
            return "    " * indent_level

        for idx, raw_line in enumerate(lines):
            stripped = raw_line.strip()

            # Blank line closes all open blocks (simple convention)
            if not stripped:
                while block_stack:
                    indent_level = block_stack.pop()
                continue

            # Check if the English source uses explicit indentation
            leading_spaces = len(raw_line) - len(raw_line.lstrip())

            # If user explicitly de-indented (wrote at column 0 while inside a block)
            # and the source uses indentation elsewhere, close blocks accordingly.
            # But if all lines are at column 0 (flat input), keep the block open
            # until a blank line or a new block-opening command at the same level.

            result = self._match_line(stripped)

            if result is None:
                # Try AI fallback for the entire remaining input
                remaining = "\n".join(
                    l for l in lines[idx:] if l.strip()
                )
                ai_code = self._ai_translate(remaining)
                if ai_code:
                    # AI handled everything from here onward as a block
                    translations.append(
                        {"english": remaining, "python": ai_code, "line": idx}
                    )
                    for ai_line in ai_code.split("\n"):
                        python_lines.append(f"{_current_indent()}{ai_line}")
                    break  # AI consumed the rest
                translations.append(
                    {
                        "english": stripped,
                        "python": f"# unrecognized: {stripped}",
                        "line": idx,
                    }
                )
                python_lines.append(f"{_current_indent()}# unrecognized: {stripped}")
                continue

            py_code, cmd_type = result

            # A new block opener at the top level (no indentation in source)
            # closes any existing blocks first, so consecutive "repeat" blocks
            # don't nest inside each other unintentionally.
            if cmd_type in ("loop", "conditional") and leading_spaces == 0:
                while block_stack:
                    indent_level = block_stack.pop()

            indented_py = f"{_current_indent()}{py_code}"
            translations.append({"english": stripped, "python": py_code, "line": idx})
            python_lines.append(indented_py)

            # If this line opens a block, increase indent for subsequent lines
            if cmd_type in ("loop", "conditional"):
                block_stack.append(indent_level)
                indent_level += 1

        full_code = "\n".join(python_lines) + "\n"
        return translations, full_code
