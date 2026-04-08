import json
import os
import re
import shutil
import subprocess
from pathlib import Path
from typing import Optional


REPO_ROOT = Path(__file__).resolve().parents[1]


class BaseProvider:
    name = "none"

    def __init__(self):
        self.unavailable_reason = ""

    def is_available(self) -> bool:
        return False

    def extract_event(self, candidate, project) -> Optional[dict]:
        return None


class NullProvider(BaseProvider):
    name = "none"


class CLIProvider(BaseProvider):
    command_name = ""

    def __init__(self):
        super().__init__()
        self.command_path = ""

    def is_available(self) -> bool:
        if self.command_path:
            return True
        command_path = shutil.which(self.command_name)
        if not command_path:
            self.unavailable_reason = f"CLI non trovato: {self.command_name}"
            return False
        self.command_path = command_path
        return True

    def extract_event(self, candidate, project) -> Optional[dict]:
        if not self.is_available():
            return None

        prompt = (
            f"{_SYSTEM_PROMPT}\n\n"
            "Restituisci solo JSON valido, senza spiegazioni e senza markdown.\n\n"
            f"{_build_prompt(candidate, project)}"
        )
        command = self._build_command(prompt)

        try:
            result = subprocess.run(
                command,
                cwd=str(REPO_ROOT),
                capture_output=True,
                text=True,
                timeout=180,
            )
        except Exception as exc:
            self.unavailable_reason = str(exc)
            return None

        payload = self._parse_cli_output(result.stdout, result.stderr)
        if payload is None and result.returncode != 0 and not self.unavailable_reason:
            self.unavailable_reason = (result.stderr or result.stdout or "").strip()[:300]
        return payload

    def _build_command(self, prompt: str):
        raise NotImplementedError

    def _parse_cli_output(self, stdout: str, stderr: str) -> Optional[dict]:
        return _safe_json_loads(stdout.strip())


class OpenAIProvider(CLIProvider):
    name = "openai"
    command_name = "codex"

    def __init__(self):
        super().__init__()
        self.model = os.getenv("OPENAI_CLI_MODEL", "gpt-5.4-mini")

    def _build_command(self, prompt: str):
        return [
            self.command_path,
            "exec",
            "--json",
            "--sandbox",
            "danger-full-access",
            "--skip-git-repo-check",
            "-m",
            self.model,
            "-C",
            str(REPO_ROOT),
            prompt,
        ]

    def _parse_cli_output(self, stdout: str, stderr: str) -> Optional[dict]:
        last_message = ""
        for raw_line in stdout.splitlines():
            line = raw_line.strip()
            if not line.startswith("{"):
                continue
            try:
                item = json.loads(line)
            except json.JSONDecodeError:
                continue
            if item.get("type") == "item.completed":
                content = item.get("item", {})
                if content.get("type") == "agent_message":
                    last_message = content.get("text", "") or ""
        return _safe_json_loads(last_message)


class ClaudeProvider(CLIProvider):
    name = "claude"
    command_name = "claude"

    def _build_command(self, prompt: str):
        return [
            self.command_path,
            "-p",
            "--output-format",
            "json",
            prompt,
        ]

    def _parse_cli_output(self, stdout: str, stderr: str) -> Optional[dict]:
        text = stdout.strip()
        if not text:
            return None
        try:
            payload = json.loads(text)
        except json.JSONDecodeError:
            return _safe_json_loads(text)
        return _safe_json_loads(payload.get("result", ""))


class GeminiProvider(CLIProvider):
    name = "gemini"
    command_name = os.getenv("GEMINI_CLI_BIN", "gemini")

    def _build_command(self, prompt: str):
        return [
            self.command_path,
            "-p",
            prompt,
        ]


def create_provider(name: str) -> BaseProvider:
    mapping = {
        "none": NullProvider,
        "openai": OpenAIProvider,
        "claude": ClaudeProvider,
        "gemini": GeminiProvider,
    }
    provider_cls = mapping.get(name, NullProvider)
    return provider_cls()


_SYSTEM_PROMPT = """
Sei un estrattore di eventi pubblici.
Usa i segnali locali come supporto, ma restituisci una decisione finale tua in JSON.
Restituisci solo JSON valido.
Campi JSON attesi:
is_event, title, short_description, full_description, start_date, end_date, time, municipality, venue, category, subcategory, organizer, image_url.
Usa date ISO YYYY-MM-DD. Se un campo manca, restituisci stringa vuota.
""".strip()


def _build_prompt(candidate, project) -> str:
    payload = {
        "project": {
            "theme": project.theme,
            "categories": project.categories,
            "known_municipalities": project.known_municipalities,
            "active_from_date": project.active_from_date,
        },
        "source": {
            "name": candidate.source.name,
            "type": candidate.source.type,
            "area": candidate.source.area,
            "discovery_only": candidate.discovery_only,
        },
        "candidate": {
            "title": candidate.title,
            "text": candidate.text[:5000],
            "detail_text": (candidate.detail_text or "")[:8000],
            "raw_date": candidate.raw_date,
            "raw_end_date": candidate.raw_end_date,
            "raw_time": candidate.raw_time,
            "raw_location": candidate.raw_location,
            "url": candidate.source_url,
        },
    }
    return json.dumps(payload, ensure_ascii=False, indent=2)


def _safe_json_loads(text: str) -> Optional[dict]:
    if not text:
        return None

    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```(?:json)?", "", cleaned).strip()
        cleaned = re.sub(r"```$", "", cleaned).strip()

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        pass

    match = re.search(r"\{.*\}", cleaned, flags=re.DOTALL)
    if not match:
        return None

    try:
        return json.loads(match.group(0))
    except json.JSONDecodeError:
        return None
