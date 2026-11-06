"""Tests of the check of the links, with a fake network."""

from __future__ import annotations

import datetime as dt
import json
import shutil
from typing import TYPE_CHECKING, Any

import pytest

import check_links
import registry
from check_links import Answer, LinkError, Result
from conftest import entity, source, write_source

if TYPE_CHECKING:
    from pathlib import Path

    from registry import Source

CHECKED_AT = dt.datetime(2026, 11, 2, 4, 41, tzinfo=dt.UTC)


class Fetcher:
    """Fake fetcher that answers each link with a given answer.

    Parameters
    ----------
    answers : dict
        For each link, the HTTP status or the `Answer` to return, or the
        exception to raise, or a list of them for successive requests.
    catch_all : str, optional
        Fingerprint of the page of the other links, as on a website that
        answers every path with the same page. By default, the other
        links answer 200 with a page of their own.
    """

    def __init__(
        self,
        answers: dict[str, Any],
        catch_all: str | None = None,
    ) -> None:
        self.answers = {
            url: list(a) if isinstance(a, list) else [a]
            for url, a in answers.items()
        }
        self.catch_all = catch_all
        self.requested: list[str] = []

    def __call__(self, url: str) -> Answer:
        """Return the answer to a link, or raise its exception.

        Parameters
        ----------
        url : str
            The link.

        Returns
        -------
        Answer
            The answer.

        Notes
        -----
        The requests of missing pages are not recorded.
        """
        if "link-check-" not in url:
            self.requested.append(url)
        default = Answer(200, self.catch_all or url)
        answers = self.answers.get(url, [default])
        answer = answers.pop(0) if len(answers) > 1 else answers[0]
        if isinstance(answer, Exception):
            raise answer
        if isinstance(answer, int):
            return Answer(answer, url)
        assert isinstance(answer, Answer)
        return answer


@pytest.fixture
def sources(data_dir: Path) -> dict[str, Source]:
    """Load the sources of the data folder of the tests.

    Parameters
    ----------
    data_dir : Path
        Data folder of the tests.

    Returns
    -------
    dict
        The sources, by identifier.
    """
    return registry.load_sources(data_dir)


def test_collect_links_lists_every_use(sources: dict[str, Source]) -> None:
    """List the pages, licences and entity pages and their uses."""
    assert check_links.collect_links(sources) == {
        "https://example.org/data": [
            "entsoe: page",
            "sonelgaz: page",
            "tepco: page",
        ],
        "https://example.org/terms": ["entsoe: licence"],
        "https://example.org/a|b(c)": ["entsoe: JPN"],
        "https://example.org/licence": [
            "sonelgaz: licence",
            "tepco: licence",
        ],
    }


@pytest.mark.parametrize(
    ("answer", "status", "detail"),
    [
        (200, "ok", "HTTP 200"),
        (302, "ok", "HTTP 302"),
        (403, "blocked", "HTTP 403"),
        (429, "blocked", "HTTP 429"),
        (400, "broken", "HTTP 400"),
        (404, "broken", "HTTP 404"),
        (503, "unreachable", "HTTP 503"),
        (LinkError("timed out"), "unreachable", "timed out"),
    ],
)
def test_check_link_classifies_the_answer(
    answer: int | Exception, status: str, detail: str
) -> None:
    """Classify a link by the status of its answer."""
    fetch = Fetcher({"https://x.org": answer})
    result = check_links.check_link("https://x.org", ["a: page"], fetch)
    assert (result.status, result.detail) == (status, detail)


def test_unreachable_link_is_tried_again() -> None:
    """Request again a link whose server could not be reached."""
    fetch = Fetcher({"https://x.org": [LinkError("reset"), 200]})
    result = check_links.check_link("https://x.org", [], fetch)
    assert result.status == "ok"
    assert fetch.requested == ["https://x.org", "https://x.org"]


def test_catch_all_website_is_unverifiable() -> None:
    """Tell apart the links of a website that answers any path alike."""
    links = {"https://spa.org/data": ["a: page"], "https://spa.org/": ["a: x"]}
    results = check_links.check_links(links, Fetcher({}, catch_all="shell"))
    status = {r.url: (r.status, r.detail) for r in results}
    assert status["https://spa.org/data"] == (
        "unverifiable",
        "HTTP 200, but the website answers a missing page with the same page",
    )
    assert status["https://spa.org/"] == ("ok", "HTTP 200")


def test_other_page_of_a_catch_all_website_is_ok() -> None:
    """Accept a page that differs from that of a missing page."""
    links = {"https://spa.org/data": ["a: page"]}
    fetch = Fetcher({"https://spa.org/data": Answer(200, "data")}, "shell")
    assert check_links.check_links(links, fetch)[0].status == "ok"


def test_certificate_verified_only_by_a_browser() -> None:
    """Report a page read without verifying its certificate."""
    fetch = Fetcher({"https://x.org/p": Answer(200, "p", verified=False)})
    result = check_links.check_link("https://x.org/p", [], fetch)
    assert result.status == "unverifiable"
    assert "certificate" in result.detail


def test_missing_page_is_on_the_same_website() -> None:
    """Request a random path of the website of the link."""
    url = check_links.missing_page("https://x.org/a/b?c=1")
    assert url.startswith("https://x.org/awesome-electricity-demand-")
    assert url != check_links.missing_page("https://x.org/a/b?c=1")


def test_check_links_counts_failures_in_a_row() -> None:
    """Add one to the failures in a row of the links that fail again."""
    links = {
        "https://a.org/gone": ["a: page"],
        "https://b.org/new-failure": ["b: page"],
        "https://c.org/fixed": ["c: page"],
        "https://d.org/blocked": ["d: page"],
    }
    fetch = Fetcher(
        {
            "https://a.org/gone": 404,
            "https://b.org/new-failure": LinkError("refused"),
            "https://d.org/blocked": 403,
        }
    )
    previous = {"https://a.org/gone": 2, "https://c.org/fixed": 1}
    results = check_links.check_links(links, fetch, previous)
    assert [(r.url, r.status, r.failures_in_a_row) for r in results] == [
        ("https://a.org/gone", "broken", 3),
        ("https://b.org/new-failure", "unreachable", 1),
        ("https://d.org/blocked", "blocked", 0),
        ("https://c.org/fixed", "ok", 0),
    ]


def test_read_previous(tmp_path: Path) -> None:
    """Read the failures in a row of the failed links of a report."""
    results = [
        Result("https://a.org", "broken", "HTTP 404", ("a: page",), 2),
        Result("https://b.org", "ok", "HTTP 200", ("b: page",)),
    ]
    check_links.write_report(results, tmp_path, CHECKED_AT)
    path = tmp_path / "link_report.json"
    assert check_links.read_previous(path) == {"https://a.org": 2}


@pytest.mark.parametrize("content", [None, "not json", '{"other": []}'])
def test_read_previous_without_report(
    tmp_path: Path, content: str | None
) -> None:
    """Count no failures without a valid previous report."""
    path = tmp_path / "link_report.json"
    if content is not None:
        path.write_text(content, encoding="utf-8")
    assert check_links.read_previous(path) == {}
    assert check_links.read_previous(None) == {}


def test_report_lists_failing_and_blocked_links(tmp_path: Path) -> None:
    """Write the failing links in a table and list the blocked ones."""
    results = [
        Result("https://a.org/x|y", "broken", "HTTP 400", ("a: ALB",), 2),
        Result("https://b.org", "blocked", "HTTP 403", ("b: licence",)),
        Result("https://d.org/x", "unverifiable", "same page", ("d: x",)),
        Result("https://c.org", "ok", "HTTP 200", ("c: page",)),
    ]
    check_links.write_report(results, tmp_path, CHECKED_AT)
    text = (tmp_path / "link_report.md").read_text(encoding="utf-8")
    assert "4 links, 1 ok, 1 failing (1 broken, 0 unreachable)" in text
    assert "1 unverifiable without a browser" in text
    assert "- [d.org/x](https://d.org/x) (d: x): same page" in text
    assert (
        "| [a.org/x\\|y](https://a.org/x%7Cy) | a: ALB | broken: HTTP 400 "
        "| 2 |"
    ) in text
    assert "- [b.org](https://b.org) (b: licence): HTTP 403" in text
    data = json.loads((tmp_path / "link_report.json").read_text("utf-8"))
    assert data["checked_at"] == "2026-11-02T04:41:00+00:00"


def test_main_checks_only_new_links(
    data_dir: Path,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Check only the links new to the base data, and warn of them."""
    base = tmp_path / "base"
    shutil.copytree(data_dir, base)
    write_source(
        data_dir,
        "sonelgaz",
        source([entity(url="https://example.org/new")]),
    )
    fetch = Fetcher({"https://example.org/new": 404})
    monkeypatch.setattr(check_links, "fetch_page", fetch)
    sources = registry.load_sources(data_dir)
    monkeypatch.setattr(registry, "load_sources", lambda: sources)
    output = tmp_path / "report"
    code = check_links.main(["--output", str(output), "--only-new", str(base)])
    assert code == 0
    assert fetch.requested == ["https://example.org/new"]
    assert capsys.readouterr().out == (
        "::warning file=data/sources/sonelgaz.yaml,title=Link check::"
        "https://example.org/new: broken (HTTP 404)\n"
    )
    assert "example.org/new" in (output / "link_report.md").read_text("utf-8")


def test_main_passes_when_old_links_fail(
    data_dir: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Succeed in the weekly check, whose failures go to an issue."""
    fetch = Fetcher({"https://example.org/terms": 404})
    monkeypatch.setattr(check_links, "fetch_page", fetch)
    sources = registry.load_sources(data_dir)
    monkeypatch.setattr(registry, "load_sources", lambda: sources)
    output = tmp_path / "report"
    assert check_links.main(["--output", str(output)]) == 0
    report = json.loads((output / "link_report.json").read_text("utf-8"))
    assert report["results"][0]["url"] == "https://example.org/terms"
