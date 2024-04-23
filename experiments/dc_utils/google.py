import os
import re

from serpapi import GoogleSearch

# Do not allow too many results as those could become
# quite imprecise
MAX_GOOGLE_RESULTS_TO_CHECK = 3


SIRET_MATCHER = re.compile(
    "SIRET.*([0-9]{3}[\s\.\-]{0,1}[0-9]{3}[\s\.\-]{0,1}[0-9]{3}[\s\.\-]{0,1}[0-9]{5})",
    re.IGNORECASE,
)


GOOGLE_SEARCH_PARAMS = {
    "api_key": os.environ.get("SERPAPI_API_KEY"),
    "engine": "google",
    "location": "Paris, Paris, Ile-de-France, France",
    "google_domain": "google.fr",
    "gl": "fr",
    "hl": "fr",
    "device": "desktop",
}


def _clean_siret(value):
    return value.replace(" ", "").replace("-", "").replace(".", "")


def _re_match(value):
    match = SIRET_MATCHER.search(value)
    if match:
        return _clean_siret(match.group(1))


def _print(s):
    if os.environ.get("DEBUG"):
        print(s)


def search_siret(email):
    params = GOOGLE_SEARCH_PARAMS.copy()
    params.update({"q": f"quel est le SIRET de {email} ?"})
    search = GoogleSearch(params)
    results = search.get_dict()
    if "answer_box" in results:
        if "contents" in results["answer_box"]:
            answer_grid = results["answer_box"]["contents"]["table"]
            try:
                for topic, value in answer_grid:
                    siret = _re_match(f"SIRET {topic}")
                    if siret:
                        yield _clean_siret(siret)
                        return
                    siret = _re_match(f"SIRET {value}")
                    if siret:
                        yield _clean_siret(siret)
                        return
                else:
                    _print(f"! no answer_grid result for email={email}")
            except ValueError:
                _print(f"! no answer_grid result for email={email}")
        elif "snippet" in results["answer_box"]:
            siret = _re_match(results["answer_box"]["snippet"])
            if siret:
                yield _clean_siret(siret)
                return
            _print(f"! no answer_snippet result for email={email}")
        else:
            _print(f"! no answer_box result for email={email}")

    for rank in range(0, MAX_GOOGLE_RESULTS_TO_CHECK):
        try:
            snippet = results["organic_results"][rank]["snippet"]
        except KeyError:
            _print(f"! no snippet result for email={email}")
            continue

        _print(f"> google rank={rank} email={email} snippet={snippet}")
        siret = _re_match(snippet)
        if siret:
            yield _clean_siret(siret)
            break
    else:
        _print(f"! no match found for email={email}")
