import os

import httpx
from furl import furl
from tenacity import retry, retry_if_exception, stop_after_attempt, wait_fixed
from tenacity.wait import wait_base


class retry_if_http_429_error(retry_if_exception):
    def __init__(self):
        def is_http_429_error(exception):
            return isinstance(exception, httpx.ReadTimeout) or (
                isinstance(exception, httpx.HTTPStatusError)
                and exception.response.status_code == 429
            )

        super().__init__(predicate=is_http_429_error)


class wait_for_retry_after_header(wait_base):
    def __init__(self, fallback):
        self.fallback = fallback

    def __call__(self, retry_state):
        exc = retry_state.outcome.exception()
        if isinstance(exc, httpx.HTTPStatusError):
            retry_after = exc.response.headers.get("Retry-After")
            try:
                return int(retry_after)
            except (TypeError, ValueError):
                pass
        return self.fallback(retry_state)


@retry(
    retry=retry_if_http_429_error(),
    wait=wait_for_retry_after_header(fallback=wait_fixed(1)),
    stop=stop_after_attempt(10),
)
def fetch_company(siren):
    f = furl(os.environ["API_ENTREPRISE_BASE_URL"])
    f.path /= "search"
    f.add({"q": siren})
    response = httpx.get(f.url)
    response.raise_for_status()
    data = response.json()

    if data["total_results"] == 0:
        # FIXME(vperron): Ce cas devrait etre enregistré dans les erreurs sur le modèle
        print(f"! api_entreprise {siren=} not found")
        return None
    elif data["total_results"] > 1:
        # Never happened.
        print(f"! api_entreprise {siren=} found multiple results")
        return None

    return data["results"][0]
