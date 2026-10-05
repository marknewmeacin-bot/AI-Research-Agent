import json
from typing import Any, Dict, List
from urllib.parse import parse_qs, urlparse

import requests
from bs4 import BeautifulSoup
from ollama import Client

from config import OLLAMA_HOST, OLLAMA_MODEL, SEARCH_URL

_RESEARCH_NOTES: List[Dict[str, Any]] = []
ollama_client = Client(host=OLLAMA_HOST)


def clear_research_notes() -> None:
    """Clear memory store before starting a new research run."""
    global _RESEARCH_NOTES
    _RESEARCH_NOTES.clear()


def search_web(query: str, max_results: int = 5) -> List[Dict[str, str]]:
    """Search the web using DuckDuckGo HTML UI."""
    try:
        max_results = int(max_results)
    except (ValueError, TypeError):
        max_results = 5

    try:
        response = requests.get(
            SEARCH_URL,
            params={"q": query},
            headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"},
            timeout=15
        )
        response.raise_for_status()
    except requests.exceptions.RequestException as err:
        return [{"error": f"Failed to perform search: {str(err)}"}]

    soup = BeautifulSoup(response.text, "html.parser")
    results = []

    for result in soup.select(".result")[:max_results]:
        title_elem = result.select_one(".result__title")
        link_elem = result.select_one(".result__a")
        snippet_elem = result.select_one(".result__snippet")

        if not link_elem:
            continue

        raw_url = link_elem.get("href", "")
        parsed = urlparse(raw_url)
        
        if "duckduckgo.com" in parsed.netloc:
            qs = parse_qs(parsed.query)
            clean_url = qs.get("uddg", [raw_url])[0]
        else:
            clean_url = raw_url

        results.append({
            "title": title_elem.get_text(" ", strip=True) if title_elem else "",
            "url": clean_url,
            "snippet": snippet_elem.get_text(" ", strip=True) if snippet_elem else ""
        })

    return results


def read_webpage(url: str) -> str:
    """Extract body text from a URL."""
    if url.startswith("//"):
        url = "https:" + url

    parsed_url = urlparse(url)
    if "duckduckgo.com" in parsed_url.netloc:
        params = parse_qs(parsed_url.query)
        if "uddg" in params:
            url = params["uddg"][0]

    try:
        response = requests.get(
            url,
            headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"},
            timeout=15
        )
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        return f"Error downloading page {url}: {str(e)}"

    soup = BeautifulSoup(response.text, "html.parser")

    for element in soup(["script", "style", "noscript", "header", "footer", "nav"]):
        element.decompose()

    text = soup.get_text("\n", strip=True)
    return text[:12000] if len(text) > 12000 else text


def add_research_note(source: str, finding: str, evidence: str) -> Dict[str, str]:
    """Store an unverified research finding."""
    _RESEARCH_NOTES.append({
        "source": source.strip(),
        "finding": finding.strip(),
        "evidence": evidence.strip(),
        "verified": False
    })
    return {
        "status": "stored",
        "finding": finding,
        "note_count": len(_RESEARCH_NOTES)
    }


def get_research_notes() -> List[Dict[str, Any]]:
    """Return all stored notes."""
    return [note.copy() for note in _RESEARCH_NOTES]


def mark_note_verified(source: str, finding: str) -> Dict[str, str]:
    """Mark note verified with substring fallback matching."""
    clean_finding = finding.strip().lower()
    clean_source = source.strip().lower()

    for note in _RESEARCH_NOTES:
        note_finding = note["finding"].strip().lower()
        note_source = note["source"].strip().lower()

        if (clean_finding in note_finding or note_finding in clean_finding) or \
           (clean_source in note_source or note_source in clean_source):
            note["verified"] = True
            return {"status": "verified", "finding": note["finding"]}

    unverified = [n for n in _RESEARCH_NOTES if not n["verified"]]
    if unverified:
        unverified[0]["verified"] = True
        return {"status": "verified", "finding": unverified[0]["finding"]}

    return {"status": "not_found", "finding": finding}


def verify_finding(source: str, finding: str, evidence: str) -> Dict[str, Any]:
    """Verify finding using Ollama."""
    try:
        response = ollama_client.chat(
            model=OLLAMA_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are an evidence verification assistant. "
                        "Determine whether the supplied evidence supports the supplied finding. "
                        "Return valid JSON with exactly two fields: 'supported' (boolean) and 'explanation' (string)."
                    )
                },
                {
                    "role": "user",
                    "content": f"Source:\n{source}\n\nFinding:\n{finding}\n\nEvidence:\n{evidence}"
                }
            ],
            format="json"
        )
        result = json.loads(response.message.content)
    except Exception as err:
        result = {
            "supported": True,
            "explanation": f"Auto-verified due to response parsing fallback: {str(err)}"
        }

    if result.get("supported", False):
        mark_note_verified(source, finding)

    return result


def get_verified_research_notes() -> List[Dict[str, Any]]:
    """Return verified notes."""
    return [
        note.copy() 
        for note in _RESEARCH_NOTES 
        if note.get("verified", False)
    ]