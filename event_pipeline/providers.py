import json
import os
import re
from typing import Optional


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


class OpenAIProvider(BaseProvider):
    name = "openai"

    def __init__(self):
        super().__init__()
        self.api_key = os.getenv("OPENAI_API_KEY", "")
        self.model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        self._client = None

    def is_available(self) -> bool:
        if not self.api_key:
            self.unavailable_reason = "manca OPENAI_API_KEY"
            return False
        try:
            from openai import OpenAI
        except ImportError:
            self.unavailable_reason = "pacchetto openai non installato"
            return False
        self._client = OpenAI(api_key=self.api_key)
        return True

    def extract_event(self, candidate, project) -> Optional[dict]:
        if not self._client and not self.is_available():
            return None
        prompt = _build_prompt(candidate, project)
        try:
            response = self._client.chat.completions.create(
                model=self.model,
                response_format={"type": "json_object"},
                messages=[
                    {"role": "system", "content": _SYSTEM_PROMPT},
                    {"role": "user", "content": prompt},
                ],
                temperature=0,
            )
            content = response.choices[0].message.content or "{}"
            return _safe_json_loads(content)
        except Exception:
            return None


class ClaudeProvider(BaseProvider):
    name = "claude"

    def __init__(self):
        super().__init__()
        self.api_key = os.getenv("ANTHROPIC_API_KEY", "")
        self.model = os.getenv("ANTHROPIC_MODEL", "claude-3-5-sonnet-latest")
        self._client = None

    def is_available(self) -> bool:
        if not self.api_key:
            self.unavailable_reason = "manca ANTHROPIC_API_KEY"
            return False
        try:
            from anthropic import Anthropic
        except ImportError:
            self.unavailable_reason = "pacchetto anthropic non installato"
            return False
        self._client = Anthropic(api_key=self.api_key)
        return True

    def extract_event(self, candidate, project) -> Optional[dict]:
        if not self._client and not self.is_available():
            return None
        prompt = _build_prompt(candidate, project)
        try:
            response = self._client.messages.create(
                model=self.model,
                max_tokens=700,
                temperature=0,
                system=_SYSTEM_PROMPT,
                messages=[{"role": "user", "content": prompt}],
            )
            text_parts = [block.text for block in response.content if getattr(block, "type", "") == "text"]
            return _safe_json_loads("\n".join(text_parts))
        except Exception:
            return None


class GeminiProvider(BaseProvider):
    name = "gemini"

    def __init__(self):
        super().__init__()
        self.api_key = os.getenv("GEMINI_API_KEY", "")
        self.model = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
        self._model = None

    def is_available(self) -> bool:
        if not self.api_key:
            self.unavailable_reason = "manca GEMINI_API_KEY"
            return False
        try:
            import google.generativeai as genai
        except ImportError:
            self.unavailable_reason = "pacchetto google-generativeai non installato"
            return False
        genai.configure(api_key=self.api_key)
        self._model = genai.GenerativeModel(self.model)
        return True

    def extract_event(self, candidate, project) -> Optional[dict]:
        if not self._model and not self.is_available():
            return None
        prompt = f"{_SYSTEM_PROMPT}\n\n{_build_prompt(candidate, project)}"
        try:
            response = self._model.generate_content(prompt)
            return _safe_json_loads(getattr(response, "text", "") or "{}")
        except Exception:
            return None


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
Sei un estrattore di eventi. Restituisci solo JSON valido.
Decidi se il contenuto descrive un evento pubblico con data reale.
Campi JSON attesi:
is_event, title, short_description, start_date, end_date, time, municipality, venue, category, subcategory, organizer, image_url.
Usa date ISO YYYY-MM-DD. Se un campo manca, restituisci stringa vuota.
""".strip()


def _build_prompt(candidate, project) -> str:
    payload = {
        "project": {
            "theme": project.theme,
            "categories": project.categories,
            "known_municipalities": project.known_municipalities,
        },
        "source": {
            "name": candidate.source.name,
            "type": candidate.source.type,
            "area": candidate.source.area,
            "discovery_only": candidate.discovery_only,
        },
        "candidate": {
            "title": candidate.title,
            "text": candidate.text[:4000],
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
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    match = re.search(r"\{.*\}", text, flags=re.DOTALL)
    if not match:
        return None

    try:
        return json.loads(match.group(0))
    except json.JSONDecodeError:
        return None
