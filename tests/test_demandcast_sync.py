"""Tests of the comparison of the list with DemandCast."""

from __future__ import annotations

import datetime as dt
import json
import shutil
from typing import TYPE_CHECKING, Any

import pytest
import yaml

import demandcast_sync as sync
import registry
from conftest import entity, source, write_source

if TYPE_CHECKING:
    from pathlib import Path

CHECKED_AT = dt.datetime(2026, 11, 3, 5, 13, tzinfo=dt.UTC)


def dc_entity(**changes: Any) -> dict[str, Any]:
    """Return an entity of a DemandCast source, with fields changed.

    Parameters
    ----------
    **changes
        Fields to change or add.

    Returns
    -------
    dict
        The entity, as in a YAML file of DemandCast.
    """
    values: dict[str, Any] = {
        "country_name": "Algeria",
        "country_code": "DZA",
        "start_date": dt.date(2010, 1, 1),
        "end_date": dt.date(2019, 12, 31),
    }
    return values | changes


def write_dc(
    directory: Path,
    source_id: str,
    entities: list[dict[str, Any]],
    redistribute: bool = True,
    url: str = "https://example.org/licence",
) -> None:
    """Write the YAML file of a DemandCast source.

    Parameters
    ----------
    directory : Path
        Folder of the YAML files of DemandCast.
    source_id : str
        Identifier of the source.
    entities : list of dict
        Entities of the source.
    redistribute : bool, default True
        Whether DemandCast redistributes the data.
    url : str, default "https://example.org/licence"
        Page of the terms of use.
    """
    content = {
        "licence": {
            "redistribute": redistribute,
            "terms": "Terms.",
            "url": url,
        },
        "compiled": False,
        "entities": entities,
    }
    directory.mkdir(exist_ok=True)
    (directory / f"{source_id}.yaml").write_text(
        yaml.safe_dump(content, allow_unicode=True), encoding="utf-8"
    )


@pytest.fixture
def dc_dir(tmp_path: Path) -> Path:
    """Write DemandCast sources that agree with the test data.

    Parameters
    ----------
    tmp_path : Path
        Temporary folder of the test.

    Returns
    -------
    Path
        Folder of the YAML files of DemandCast.

    Notes
    -----
    DemandCast has ``sonelgaz`` and ``tepco``, which agree with the
    list, and not ``entsoe``, which is in the backlog.
    """
    directory = tmp_path / "demandcast"
    write_dc(directory, "sonelgaz", [dc_entity()])
    write_dc(
        directory,
        "tepco",
        [
            dc_entity(
                country_name="Japan",
                country_code="JPN",
                subdivision_code="Kantō",
                subdivision_name="Kantō",
                start_date=dt.date(2016, 4, 1),
                end_date="today",
            )
        ],
    )
    return directory


def findings(data_dir: Path, dc_dir: Path) -> list[sync.Finding]:
    """Compare the data folder of a test with its DemandCast folder.

    Parameters
    ----------
    data_dir : Path
        Data folder of the list.
    dc_dir : Path
        Folder of the YAML files of DemandCast.

    Returns
    -------
    list of Finding
        The findings, with the accepted differences of the data folder.
    """
    return sync._findings(data_dir, sync.read_demandcast(dc_dir))


def test_agreeing_sources_have_only_notes(
    data_dir: Path, dc_dir: Path
) -> None:
    """Report only the backlog when the two repositories agree."""
    result = findings(data_dir, dc_dir)
    assert [(f.source, f.check) for f in result] == [("entsoe", "backlog")]
    assert result[0].severity == "note"


def test_missing_source_is_a_divergence(data_dir: Path, dc_dir: Path) -> None:
    """Report a source of DemandCast that the list lacks."""
    write_dc(dc_dir, "isone", [dc_entity()])
    result = [f for f in findings(data_dir, dc_dir) if f.source == "isone"]
    assert [(f.check, f.severity) for f in result] == [
        ("source", "divergence")
    ]


def test_missing_entity_and_subdivision_name(
    data_dir: Path, dc_dir: Path
) -> None:
    """Report a missing entity and a subdivision named differently."""
    write_dc(
        dc_dir,
        "tepco",
        [
            dc_entity(
                country_code="JPN",
                subdivision_code="Kantō",
                subdivision_name="Kanto",
                start_date=dt.date(2016, 4, 1),
                end_date="today",
            ),
            dc_entity(country_code="JPN", subdivision_code="Kansai"),
        ],
    )
    result = {
        (f.check, f.entity) for f in findings(data_dir, dc_dir) if f.is_open
    }
    assert result == {("subdivision", "JPN-Kantō"), ("entity", "JPN-Kansai")}


@pytest.mark.parametrize(
    ("start", "end", "message"),
    [
        (dt.date(2009, 5, 1), dt.date(2019, 1, 1), "starts in 2009"),
        (dt.date(2010, 1, 1), dt.date(2020, 6, 30), "ends in 2020"),
        (dt.date(2010, 1, 1), "today", "until today, the list ends in 2019"),
        (dt.date(2012, 1, 1), dt.date(2015, 1, 1), None),
        (dt.date(2009, 12, 30), dt.date(2020, 1, 2), None),
        (dt.date(2009, 11, 30), dt.date(2019, 1, 2), "starts in 2009"),
        (dt.date(2010, 1, 1), dt.date(2020, 2, 1), "ends in 2020"),
    ],
)
def test_years_of_demandcast_within_the_list(
    data_dir: Path,
    dc_dir: Path,
    start: dt.date,
    end: dt.date | str,
    message: str | None,
) -> None:
    """Accept fewer years in DemandCast, and report more."""
    write_dc(dc_dir, "sonelgaz", [dc_entity(start_date=start, end_date=end)])
    result = [f for f in findings(data_dir, dc_dir) if f.check == "years"]
    if message is None:
        assert result == []
    else:
        assert len(result) == 1
        assert message in result[0].message


def test_present_agrees_with_an_end_this_year(
    data_dir: Path, dc_dir: Path
) -> None:
    """Accept a last day in the current year for "present"."""
    end = dt.date(registry.current_year(), 3, 31)
    write_dc(
        dc_dir,
        "tepco",
        [
            dc_entity(
                country_code="JPN",
                subdivision_code="Kantō",
                subdivision_name="Kantō",
                start_date=dt.date(2016, 4, 1),
                end_date=end,
            )
        ],
    )
    assert not [f for f in findings(data_dir, dc_dir) if f.check == "years"]
    write_dc(
        dc_dir,
        "tepco",
        [
            dc_entity(
                country_code="JPN",
                subdivision_code="Kantō",
                subdivision_name="Kantō",
                start_date=dt.date(2016, 4, 1),
                end_date=dt.date(2020, 6, 30),
            )
        ],
    )
    result = [f for f in findings(data_dir, dc_dir) if f.check == "years"]
    assert "the list says present, DemandCast ends in 2020" in (
        result[0].message
    )


@pytest.mark.parametrize(
    ("redistribute", "category", "divergence"),
    [
        (True, "open", False),
        (True, "non-commercial", False),
        (True, "restricted", True),
        (False, "open", True),
        (False, "non-commercial", False),
        (False, "restricted", False),
    ],
)
def test_licence(
    data_dir: Path,
    dc_dir: Path,
    redistribute: bool,
    category: str,
    divergence: bool,
) -> None:
    """Report a redistribution that contradicts the licence category."""
    write_source(
        data_dir,
        "sonelgaz",
        source(
            [entity()],
            licence={
                "name": "Terms",
                "url": "https://example.org/licence",
                "category": category,
            },
        ),
    )
    write_dc(dc_dir, "sonelgaz", [dc_entity()], redistribute=redistribute)
    result = [f for f in findings(data_dir, dc_dir) if f.check == "licence"]
    assert bool(result) == divergence


def test_licence_url_note_ignores_trailing_slash(
    data_dir: Path, dc_dir: Path
) -> None:
    """Note different pages of terms, but not a trailing slash."""
    write_dc(
        dc_dir, "sonelgaz", [dc_entity()], url="https://example.org/licence/"
    )
    assert not [
        f for f in findings(data_dir, dc_dir) if f.check == "licence_url"
    ]
    write_dc(
        dc_dir, "sonelgaz", [dc_entity()], url="https://example.org/other"
    )
    result = [
        f for f in findings(data_dir, dc_dir) if f.check == "licence_url"
    ]
    assert [f.severity for f in result] == ["note"]


def test_accepted_differences(data_dir: Path, dc_dir: Path) -> None:
    """Mark accepted differences, and note those no longer found."""
    write_dc(dc_dir, "sonelgaz", [dc_entity(start_date=dt.date(2005, 1, 1))])
    (data_dir / "demandcast_differences.yaml").write_text(
        yaml.safe_dump(
            {
                "differences": [
                    {
                        "source": "sonelgaz",
                        "check": "years",
                        "entity": "DZA",
                        "reason": "The list has the published years only.",
                    },
                    {
                        "source": "tepco",
                        "check": "licence",
                        "reason": "Resolved since.",
                    },
                ]
            }
        ),
        encoding="utf-8",
    )
    result = findings(data_dir, dc_dir)
    years = next(f for f in result if f.check == "years")
    assert years.accepted == "The list has the published years only."
    assert not years.is_open
    stale = next(f for f in result if f.check == "accepted")
    assert stale.source == "tepco"
    assert "no longer found" in stale.message


def test_invalid_differences_file(data_dir: Path) -> None:
    """Reject an accepted difference without a reason."""
    path = data_dir / "demandcast_differences.yaml"
    path.write_text(
        "differences:\n  - source: x\n    check: years\n", encoding="utf-8"
    )
    with pytest.raises(sync.SyncError, match="reason"):
        sync.read_differences(path)


def test_report_groups_missing_entities(data_dir: Path, dc_dir: Path) -> None:
    """Write the missing entities of a source in one row."""
    write_dc(
        dc_dir,
        "sonelgaz",
        [dc_entity(), *(dc_entity(subdivision_code=c) for c in "ABC")],
    )
    text = sync.report_markdown(findings(data_dir, dc_dir), CHECKED_AT)
    assert (
        "| `sonelgaz` | DZA-A, DZA-B, DZA-C | entity | DemandCast retrieves "
        "3 entities that the list does not have |"
    ) in text
    assert text.count("DZA-A") == 1


def test_pull_request_comment_and_annotations(
    data_dir: Path, dc_dir: Path, tmp_path: Path
) -> None:
    """Comment on the divergences that a pull request changes."""
    base = tmp_path / "base"
    shutil.copytree(data_dir, base)
    write_dc(dc_dir, "sonelgaz", [dc_entity(start_date=dt.date(2005, 1, 1))])
    write_source(data_dir, "sonelgaz", source([entity(start=2005)]))
    write_source(
        data_dir, "tepco", source([entity(country_code="JPN")], name="TEPCO")
    )
    output = tmp_path / "report"
    code = sync.main(
        [
            "--demandcast",
            str(dc_dir),
            "--output",
            str(output),
            "--data",
            str(data_dir),
            "--base-data",
            str(base),
        ]
    )
    assert code == 0
    comment = (output / "comment.md").read_text(encoding="utf-8")
    assert comment.startswith(sync.COMMENT_MARKER)
    assert "adds divergences" in comment
    assert "| `tepco` | JPN-Kantō | entity |" in comment
    assert "resolves these divergences" in comment
    assert "| `sonelgaz` | DZA | years |" in comment
    report = json.loads(
        (output / "demandcast_sync_report.json").read_text("utf-8")
    )
    assert any(f["open"] for f in report["findings"])


def test_annotations_point_to_the_data_file(data_dir: Path) -> None:
    """Annotate the data file of the source, if the PR has it."""
    added = [
        sync.Finding("tepco", "entity", "JPN-A", "missing", "divergence"),
        sync.Finding("isone", "source", None, "missing 100%", "divergence"),
    ]
    assert sync.warning_commands(added, data_dir) == [
        (
            "::warning file=data/sources/tepco.yaml,title=Sync with "
            "DemandCast::tepco JPN-A: missing"
        ),
        "::warning title=Sync with DemandCast::isone : missing 100%25",
    ]


def test_no_comment_without_changes() -> None:
    """Write no comment if a pull request changes no divergence."""
    assert sync.comment_markdown([], []) is None


def test_main_fails_on_invalid_demandcast_files(
    data_dir: Path, tmp_path: Path
) -> None:
    """Fail if the folder of DemandCast has no data source."""
    empty = tmp_path / "empty"
    empty.mkdir()
    code = sync.main(
        [
            "--demandcast",
            str(empty),
            "--output",
            str(tmp_path / "out"),
            "--data",
            str(data_dir),
        ]
    )
    assert code == 1


def test_read_demandcast_ignores_other_fields(dc_dir: Path) -> None:
    """Read only the fields that the list also has."""
    sources = sync.read_demandcast(dc_dir)
    assert sources["tepco"].entities[0].label == "JPN-Kantō"
    assert sources["tepco"].entities[0].end_date == "today"
