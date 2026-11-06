"""Check the links of the data files over the network.

Every link of the data files is requested: the page and the licence of
each source, and the pages of its entities. A link is ok if it answers
with a status below 400, broken if it answers with another client
error, unreachable if its server fails, times out or cannot be
reached, and blocked if it refuses automated requests (401, 403 or
429), which says nothing about the page. A link is unverifiable if it
can only be checked in a browser: its website answers a missing page
with the same page, or its certificate can only be verified by a
browser. The report, in JSON and Markdown, counts the failures in a
row of each link from the report of the previous check, so that a link
is reported only when it fails twice in a row.

Usage::

    python scripts/check_links.py --output DIR [--previous FILE]
    python scripts/check_links.py --output DIR --only-new BASE_DATA_DIR
"""

from __future__ import annotations

import argparse
import dataclasses
import datetime as dt
import hashlib
import http.client
import json
import logging
import re
import ssl
import sys
import urllib.error
import urllib.parse
import urllib.request
import uuid
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import TYPE_CHECKING, Literal, NamedTuple

import registry
from build import link
from registry import RegistryError

if TYPE_CHECKING:
    from collections.abc import Callable

    from registry import Source

USER_AGENT = (
    "Mozilla/5.0 (compatible; Awesome-Electricity-Demand link check; "
    "+https://github.com/open-energy-transition/Awesome-Electricity-Demand)"
)
TIMEOUT_SECONDS = 30
ATTEMPTS = 2
WORKERS = 8
MAX_BYTES = 2_000_000
BLOCKED_CODES = frozenset({401, 403, 429})
REPORT_NAME = "link_report"
URL_PATTERN = re.compile(r"https?://\S+")
DIGITS = re.compile(rb"\d+")

Status = Literal["ok", "unverifiable", "blocked", "broken", "unreachable"]
FAILED: tuple[Status, ...] = ("broken", "unreachable")
ORDER: tuple[Status, ...] = (
    "broken",
    "unreachable",
    "unverifiable",
    "blocked",
    "ok",
)

logger = logging.getLogger(__name__)


class LinkError(Exception):
    """The server of a link cannot be reached."""


class Answer(NamedTuple):
    """Answer of a website to the request of a link.

    Attributes
    ----------
    status : int
        HTTP status, after the redirections.
    fingerprint : str
        Hash of the start of the page, without its digits.
    verified : bool
        Whether the certificate of the website was verified.
    """

    status: int
    fingerprint: str
    verified: bool = True


@dataclasses.dataclass(frozen=True)
class Result:
    """Result of the check of one link.

    Attributes
    ----------
    url : str
        The link.
    status : {"ok", "unverifiable", "blocked", "broken", "unreachable"}
        What the check found.
    detail : str
        The HTTP status, or why the server could not be reached or the
        link could not be verified.
    uses : tuple of str
        Where the data files use the link, such as "entsoe: licence".
    failures_in_a_row : int
        Number of checks in a row in which the link was broken or
        unreachable, including this one.
    """

    url: str
    status: Status
    detail: str
    uses: tuple[str, ...]
    failures_in_a_row: int = 0


def collect_links(sources: dict[str, Source]) -> dict[str, list[str]]:
    """List the links of the sources and where they are used.

    Parameters
    ----------
    sources : dict
        The sources, by identifier.

    Returns
    -------
    dict
        For each link, where it is used: the page or the licence of a
        source, or the page of an entity, named by its country and
        subdivision codes.
    """
    links: dict[str, list[str]] = {}

    def add(url: str, use: str) -> None:
        uses = links.setdefault(url, [])
        if use not in uses:
            uses.append(use)

    for source_id, source in sorted(sources.items()):
        add(source.url, f"{source_id}: page")
        add(source.licence.url, f"{source_id}: licence")
        for entity in source.entities:
            if entity.url is not None:
                where = entity.country_code
                if entity.subdivision_code is not None:
                    where += f"-{entity.subdivision_code}"
                add(entity.url, f"{source_id}: {where}")
    return links


def _request(url: str, context: ssl.SSLContext | None) -> Answer:
    """Request a link and read the start of its page.

    Parameters
    ----------
    url : str
        The link, percent-encoded.
    context : ssl.SSLContext or None
        TLS settings, or None for the defaults, which verify the
        certificate.

    Returns
    -------
    Answer
        The status and the fingerprint of the page.
    """
    request = urllib.request.Request(  # noqa: S310 - only http(s) links.
        url, headers={"User-Agent": USER_AGENT, "Accept": "*/*"}
    )
    try:
        with urllib.request.urlopen(  # noqa: S310 - only http(s) links.
            request, timeout=TIMEOUT_SECONDS, context=context
        ) as response:
            body = response.read(MAX_BYTES)
            status = int(response.status)
    except urllib.error.HTTPError as e:
        body = e.read(MAX_BYTES)
        status = e.code
    fingerprint = hashlib.sha256(DIGITS.sub(b"", body)).hexdigest()
    return Answer(status=status, fingerprint=fingerprint)


def fetch_page(url: str) -> Answer:
    """Request a link and return the status and fingerprint of its page.

    Parameters
    ----------
    url : str
        The link, with http or https.

    Returns
    -------
    Answer
        The status of the answer after the redirections, the fingerprint
        of the start of its page, and whether the certificate of the
        website was verified.

    Raises
    ------
    LinkError
        If the server cannot be reached or does not answer in time.

    Notes
    -----
    The request is a GET, since some servers reject HEAD requests.
    Characters that are not allowed in a URL, such as the pipes of the
    links of ENTSO-E, are percent-encoded. Browsers fetch the
    intermediate certificates that some websites do not send, so a
    certificate that cannot be verified is requested again without
    verification, which only reads the status of a public page.
    """
    quoted = urllib.parse.quote(url, safe=":/?#[]@!$&'()*+,;=%~")
    try:
        try:
            return _request(quoted, None)
        except urllib.error.URLError as e:
            if not isinstance(e.reason, ssl.SSLCertVerificationError):
                raise LinkError(str(e.reason)) from e
        unverified = ssl.create_default_context()
        unverified.check_hostname = False
        unverified.verify_mode = ssl.CERT_NONE
        return _request(quoted, unverified)._replace(verified=False)
    except urllib.error.URLError as e:
        raise LinkError(str(e.reason)) from e
    except (OSError, http.client.HTTPException) as e:
        raise LinkError(str(e) or type(e).__name__) from e


def missing_page(url: str) -> str:
    """Return the link of a page that the website of a link lacks.

    Parameters
    ----------
    url : str
        A link of the website.

    Returns
    -------
    str
        A link to a random path of the same website.
    """
    parts = urllib.parse.urlsplit(url)
    path = f"/awesome-electricity-demand-link-check-{uuid.uuid4().hex}"
    return f"{parts.scheme}://{parts.netloc}{path}"


def check_link(
    url: str,
    uses: list[str],
    fetch: Callable[[str], Answer],
    missing: str | None = None,
) -> Result:
    """Check one link, trying again if its server cannot be reached.

    Parameters
    ----------
    url : str
        The link.
    uses : list of str
        Where the data files use the link.
    fetch : callable
        Function that returns the `Answer` to a link, or raises
        `LinkError`.
    missing : str, optional
        Fingerprint of the page with which the website answers a missing
        page, if it answers it with a status below 400.

    Returns
    -------
    Result
        The result of the check, with no failures in a row counted.

    Notes
    -----
    A website that answers a missing page with the same page as a link,
    such as an application that renders its pages in the browser, gives
    no way to tell without a browser whether the link shows its page,
    so the link is unverifiable, unless it is the home page.
    """
    status: Status = "unreachable"
    detail = ""
    for _ in range(ATTEMPTS):
        try:
            answer = fetch(url)
        except LinkError as e:
            status, detail = "unreachable", str(e)
            continue
        code = answer.status
        detail = f"HTTP {code}"
        if code >= 500:
            status = "unreachable"
            continue
        status, detail = _classify(url, answer, missing)
        break
    return Result(url=url, status=status, detail=detail, uses=tuple(uses))


def _classify(
    url: str, answer: Answer, missing: str | None
) -> tuple[Status, str]:
    """Classify the answer of a website, below a server error.

    Parameters
    ----------
    url : str
        The link.
    answer : Answer
        The answer of the website.
    missing : str or None
        Fingerprint of the answer of the website to a missing page.

    Returns
    -------
    status : str
        The status of the link.
    detail : str
        The HTTP status, and why the link is unverifiable if it is.
    """
    code = answer.status
    if code in BLOCKED_CODES:
        return "blocked", f"HTTP {code}"
    if code >= 400:
        return "broken", f"HTTP {code}"
    if not answer.verified:
        return "unverifiable", (
            f"HTTP {code} without verifying the certificate, which only a "
            "browser can verify"
        )
    home = urllib.parse.urlsplit(url).path in {"", "/"}
    if missing is not None and answer.fingerprint == missing and not home:
        return "unverifiable", (
            f"HTTP {code}, but the website answers a missing page with the "
            "same page"
        )
    return "ok", f"HTTP {code}"


def _missing_fingerprint(
    url: str, fetch: Callable[[str], Answer]
) -> str | None:
    """Return the fingerprint of a missing page of a link's website.

    Parameters
    ----------
    url : str
        A link of the website.
    fetch : callable
        Function that returns the `Answer` to a link.

    Returns
    -------
    str or None
        The fingerprint of the page with which the website answers a
        missing page, or None if it answers with an error.
    """
    try:
        answer = fetch(missing_page(url))
    except LinkError:
        return None
    return answer.fingerprint if answer.status < 400 else None


def check_links(
    links: dict[str, list[str]],
    fetch: Callable[[str], Answer] | None = None,
    previous: dict[str, int] | None = None,
) -> list[Result]:
    """Check links, and count their failures in a row.

    Parameters
    ----------
    links : dict
        For each link, where it is used.
    fetch : callable, optional
        Function that returns the `Answer` to a link, or raises
        `LinkError`, by default `fetch_page`.
    previous : dict, optional
        Failures in a row of each link that failed the previous check.

    Returns
    -------
    list of Result
        The results, the failing links first.

    Notes
    -----
    The links of a website are requested one after the other, after a
    missing page of the website, and different websites in parallel, so
    that no website gets many requests at once.
    """
    fetcher = fetch or fetch_page
    previous = previous or {}
    by_host: dict[str, list[str]] = defaultdict(list)
    for url in links:
        by_host[urllib.parse.urlsplit(url).netloc.lower()].append(url)

    def check_host(urls: list[str]) -> list[Result]:
        missing = _missing_fingerprint(urls[0], fetcher)
        return [check_link(url, links[url], fetcher, missing) for url in urls]

    with ThreadPoolExecutor(max_workers=WORKERS) as pool:
        results = [
            r for rs in pool.map(check_host, by_host.values()) for r in rs
        ]
    results = [
        dataclasses.replace(r, failures_in_a_row=previous.get(r.url, 0) + 1)
        if r.status in FAILED
        else r
        for r in results
    ]
    return sorted(results, key=lambda r: (ORDER.index(r.status), r.url))


def read_previous(path: Path | None) -> dict[str, int]:
    """Read the failures in a row from the report of a previous check.

    Parameters
    ----------
    path : Path or None
        JSON report of the previous check, if there is one.

    Returns
    -------
    dict
        Failures in a row of each link that failed the previous check,
        or nothing if the report is missing or unreadable.
    """
    if path is None:
        return {}
    try:
        results = json.loads(path.read_text(encoding="utf-8"))["results"]
        return {
            r["url"]: int(r["failures_in_a_row"])
            for r in results
            if r["status"] in FAILED
        }
    except (OSError, ValueError, KeyError, TypeError):
        logger.info("No report of a previous check to count failures from.")
        return {}


def baseline_links(data_dir: Path) -> set[str]:
    """Return every link written in the data files of a folder.

    Parameters
    ----------
    data_dir : Path
        Data folder, such as that of the base branch of a pull request.

    Returns
    -------
    set of str
        The links found in the text of its source files.

    Notes
    -----
    The links are found in the text, not in the validated data, so that
    data files in an older format still count.
    """
    links: set[str] = set()
    for path in (data_dir / "sources").glob("*.yaml"):
        links.update(URL_PATTERN.findall(path.read_text(encoding="utf-8")))
    return links


def report_markdown(results: list[Result], checked_at: dt.datetime) -> str:
    """Write the report of a check in Markdown.

    Parameters
    ----------
    results : list of Result
        The results of the check.
    checked_at : datetime
        Time of the check.

    Returns
    -------
    str
        A summary, a table of the failing links, and lists of the
        unverifiable links and of those blocked to automated checks.
    """
    counts = {s: sum(r.status == s for r in results) for s in ORDER}
    failing = [r for r in results if r.status in FAILED]
    unverifiable = [r for r in results if r.status == "unverifiable"]
    blocked = [r for r in results if r.status == "blocked"]
    lines = [
        "## Link check",
        "",
        (
            f"Checked on {checked_at:%Y-%m-%d %H:%M} UTC: "
            f"{len(results)} links, {counts['ok']} ok, {len(failing)} "
            f"failing ({counts['broken']} broken, "
            f"{counts['unreachable']} unreachable), "
            f"{counts['unverifiable']} unverifiable without a browser, "
            f"{counts['blocked']} blocked to automated checks."
        ),
    ]
    if failing:
        lines += [
            "",
            "### Failing",
            "",
            "| Link | Used by | Result | Failures in a row |",
            "| --- | --- | --- | --- |",
        ]
        lines += [
            f"| {link(_label(r.url), r.url)} | {', '.join(r.uses)} | "
            f"{r.status}: {r.detail.replace('|', '/')} | "
            f"{r.failures_in_a_row} |"
            for r in failing
        ]
    if unverifiable:
        lines += [
            "",
            "### Unverifiable without a browser",
            "",
            (
                "These links answer, but only a browser can tell whether "
                "they show the page:"
            ),
            "",
        ]
        lines += [
            f"- {link(_label(r.url), r.url)} ({', '.join(r.uses)}): {r.detail}"
            for r in unverifiable
        ]
    if blocked:
        lines += [
            "",
            "### Blocked to automated checks",
            "",
            (
                "These websites refuse automated requests, so their links "
                "could not be checked:"
            ),
            "",
        ]
        lines += [
            f"- {link(_label(r.url), r.url)} ({', '.join(r.uses)}): {r.detail}"
            for r in blocked
        ]
    return "\n".join(lines) + "\n"


def _label(url: str, length: int = 60) -> str:
    """Shorten a link to show it as the text of a Markdown link.

    Parameters
    ----------
    url : str
        The link.
    length : int, default 60
        Maximum number of characters.

    Returns
    -------
    str
        The link without its scheme, cut with an ellipsis if too long.
    """
    text = url.split("://", 1)[-1]
    return text if len(text) <= length else text[: length - 1] + "…"


def write_report(
    results: list[Result], directory: Path, checked_at: dt.datetime
) -> None:
    """Write the report of a check in JSON and Markdown.

    Parameters
    ----------
    results : list of Result
        The results of the check.
    directory : Path
        Folder of the report, created if needed.
    checked_at : datetime
        Time of the check.
    """
    directory.mkdir(parents=True, exist_ok=True)
    data = {
        "checked_at": checked_at.isoformat(timespec="seconds"),
        "results": [dataclasses.asdict(r) for r in results],
    }
    (directory / f"{REPORT_NAME}.json").write_text(
        json.dumps(data, ensure_ascii=False, indent=1) + "\n",
        encoding="utf-8",
    )
    (directory / f"{REPORT_NAME}.md").write_text(
        report_markdown(results, checked_at), encoding="utf-8"
    )


def main(argv: list[str] | None = None) -> int:
    """Check the links and write the report.

    Parameters
    ----------
    argv : list of str, optional
        Arguments of the command, by default those of the process.

    Returns
    -------
    int
        1 if the data is invalid, 0 otherwise: failing links never
        fail the check. The weekly check reports them in an issue, and
        with --only-new they are warnings on the data files.
    """
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--previous", type=Path)
    parser.add_argument(
        "--only-new",
        type=Path,
        metavar="BASE_DATA_DIR",
        help="check only the links that are not in this data folder",
    )
    args = parser.parse_args(argv)

    try:
        links = collect_links(registry.load_sources())
    except RegistryError as e:
        logger.error("The data files have errors:\n%s", e)  # noqa: TRY400
        return 1
    if args.only_new is not None:
        known = baseline_links(args.only_new)
        links = {url: uses for url, uses in links.items() if url not in known}

    checked_at = dt.datetime.now(dt.UTC)
    results = check_links(links, previous=read_previous(args.previous))
    write_report(results, args.output, checked_at)
    failing = [r for r in results if r.status in FAILED]
    logger.info("%d links checked, %d failing.", len(results), len(failing))
    if args.only_new is not None:
        for line in warning_commands(failing):
            sys.stdout.write(line + "\n")
    return 0


def warning_commands(results: list[Result]) -> list[str]:
    """Return the workflow commands that annotate failing new links.

    Parameters
    ----------
    results : list of Result
        The failing links that a pull request adds.

    Returns
    -------
    list of str
        One warning per use of each link, on the data file of its
        source.
    """
    lines: list[str] = []
    for result in results:
        text = f"{result.url}: {result.status} ({result.detail})"
        text = text.replace("%", "%25").replace("\n", "%0A")
        sources = sorted({use.split(":")[0] for use in result.uses})
        lines.extend(
            f"::warning file=data/sources/{source_id}.yaml,"
            f"title=Link check::{text}"
            for source_id in sources
        )
    return lines


if __name__ == "__main__":
    sys.exit(main())
