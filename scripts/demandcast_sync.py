r"""Compare the data sources of the list with those of DemandCast.

Every data source that DemandCast retrieves should be in the list, with
the same identifier, and the two should agree where they state the same
fact. DemandCast describes each source in a YAML file of its folder
``retrievals/electricity_demand_data_sources/``; only the fields that
the list also has are read: the licence (whether the data can be
redistributed, and the page of the terms) and the entities (country,
subdivision, first and last day).

Each difference is a finding: a divergence, or a note. DemandCast is
the source of truth for the facts that both state, since its checks
verify its data more often: a divergence is resolved in the list,
unless DemandCast is outdated. Nothing fails: the divergences
are reported in an issue, and on pull requests as warnings. A
divergence that is deliberate is listed, with its reason, in
``data/demandcast_differences.yaml``, and reported as accepted.

Usage::

    python scripts/demandcast_sync.py --demandcast DIR --output DIR
    python scripts/demandcast_sync.py --demandcast DIR --output DIR \\
        --base-data BASE_DATA_DIR
"""

from __future__ import annotations

import argparse
import dataclasses
import datetime as dt
import json
import logging
import sys
from pathlib import Path
from typing import Annotated, Literal

import yaml
from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    StringConstraints,
    ValidationError,
)

import registry
from registry import DATA_DIR, RegistryError, Source, StrictModel

Check = Literal[
    "source",
    "entity",
    "subdivision",
    "years",
    "licence",
    "licence_url",
    "backlog",
    "accepted",
]
Severity = Literal["divergence", "note"]
DIFFERENCES_FILE = DATA_DIR / "demandcast_differences.yaml"
REPORT_NAME = "demandcast_sync_report"
COMMENT_MARKER = "<!-- demandcast-sync -->"

logger = logging.getLogger(__name__)


class SyncError(Exception):
    """Invalid files of DemandCast or of the accepted differences."""


class LenientModel(BaseModel):
    """Model that ignores the fields it does not have."""

    model_config = ConfigDict(extra="ignore", frozen=True)


class DemandCastLicence(LenientModel):
    """Licence of a data source of DemandCast.

    Attributes
    ----------
    redistribute : bool
        Whether DemandCast can redistribute the data.
    url : str
        Page with the terms of use.
    """

    redistribute: bool
    url: str


class DemandCastEntity(LenientModel):
    """Country or subdivision of a data source of DemandCast.

    Attributes
    ----------
    country_code : str
        ISO 3166-1 alpha-3 code of the country.
    subdivision_code, subdivision_name : str or None
        Code and name of the subdivision, or None for the country.
    start_date : date
        First day with data.
    end_date : date or "today"
        Last day with data, or "today" if the data is still updated.
    """

    country_code: str
    subdivision_code: str | None = None
    subdivision_name: str | None = None
    start_date: dt.date
    end_date: dt.date | Literal["today"]

    @property
    def label(self) -> str:
        """Country code, and subdivision code after a dash."""
        return _label(self.country_code, self.subdivision_code)


class DemandCastSource(LenientModel):
    """Data source of DemandCast, with the fields that the list has.

    Attributes
    ----------
    licence : DemandCastLicence
        Terms of use of the data.
    entities : list of DemandCastEntity
        Countries and subdivisions with data.
    """

    licence: DemandCastLicence
    entities: list[DemandCastEntity]


class Difference(StrictModel):
    """Deliberate divergence between the list and DemandCast.

    Attributes
    ----------
    source : str
        Identifier of the data source.
    check : str
        Check of the divergence, such as "licence" or "years".
    entity : str or None
        Country code, and subdivision code after a dash, for the checks
        of an entity.
    reason : str
        Why the two repositories differ.
    """

    source: str
    check: Check
    entity: str | None = None
    reason: Annotated[str, StringConstraints(min_length=1)]


class Differences(StrictModel):
    """Content of the file of accepted differences.

    Attributes
    ----------
    differences : list of Difference
        The deliberate divergences.
    """

    differences: list[Difference] = Field(default_factory=list)


@dataclasses.dataclass(frozen=True)
class Finding:
    """Difference between the list and DemandCast.

    Attributes
    ----------
    source : str
        Identifier of the data source.
    check : str
        What differs: the presence of the source, an entity, the name
        of a subdivision, the years, the licence or the page of the
        terms; "backlog" for a source that DemandCast does not retrieve,
        and "accepted" for an accepted difference that is not found.
    entity : str or None
        Country code, and subdivision code after a dash.
    message : str
        Description of the difference.
    severity : {"divergence", "note"}
        Whether one of the repositories should change, or it is only
        information.
    accepted : str or None
        Reason of the accepted difference that matches the finding.
    """

    source: str
    check: Check
    entity: str | None
    message: str
    severity: Severity
    accepted: str | None = None

    @property
    def key(self) -> tuple[str, str, str | None]:
        """Source, check and entity, which identify the finding."""
        return (self.source, self.check, self.entity)

    @property
    def is_open(self) -> bool:
        """Whether it is a divergence that is not accepted."""
        return self.severity == "divergence" and self.accepted is None


def _label(country_code: str, subdivision_code: str | None) -> str:
    """Return the label of an entity.

    Parameters
    ----------
    country_code : str
        Code of the country.
    subdivision_code : str or None
        Code of the subdivision.

    Returns
    -------
    str
        The country code, and the subdivision code after a dash.
    """
    if subdivision_code is None:
        return country_code
    return f"{country_code}-{subdivision_code}"


def read_demandcast(directory: Path) -> dict[str, DemandCastSource]:
    """Read the YAML files of the data sources of DemandCast.

    Parameters
    ----------
    directory : Path
        Folder ``retrievals/electricity_demand_data_sources`` of
        DemandCast.

    Returns
    -------
    dict
        The sources, by identifier.

    Raises
    ------
    SyncError
        If the folder has no YAML file, or a file lacks the fields that
        are compared.
    """
    sources: dict[str, DemandCastSource] = {}
    problems = []
    for path in sorted(directory.glob("*.yaml")):
        try:
            content = yaml.safe_load(path.read_text(encoding="utf-8"))
            sources[path.stem] = DemandCastSource.model_validate(content)
        except (yaml.YAMLError, ValidationError) as e:
            problems.append(f"{path.name}: {e}")
    if problems:
        raise SyncError("\n".join(problems))
    if not sources:
        raise SyncError(f"{directory} has no YAML file of a data source")
    return sources


def read_differences(path: Path) -> list[Difference]:
    """Read the accepted differences.

    Parameters
    ----------
    path : Path
        File of the accepted differences.

    Returns
    -------
    list of Difference
        The accepted differences, or none if the file does not exist.

    Raises
    ------
    SyncError
        If the file is invalid.
    """
    if not path.exists():
        return []
    try:
        content = yaml.safe_load(path.read_text(encoding="utf-8"))
        return Differences.model_validate(content or {}).differences
    except (yaml.YAMLError, ValidationError) as e:
        raise SyncError(f"{path.name}: {e}") from e


def _compare_years(
    source_id: str,
    entity: DemandCastEntity,
    periods: list[registry.Entity],
) -> list[Finding]:
    """Compare the years of an entity in the two repositories.

    Parameters
    ----------
    source_id : str
        Identifier of the data source.
    entity : DemandCastEntity
        The entity in DemandCast.
    periods : list of Entity
        The entries of the entity in the list.

    Returns
    -------
    list of Finding
        A divergence if the years of DemandCast are outside those of
        the list, or if only one of them says the data is still updated.

    Notes
    -----
    The years of DemandCast can be fewer than those of the list, since
    a retriever may use only part of a series. A last day of DemandCast
    in the current year agrees with "present" in the list. The days of
    DemandCast are in UTC, and many series start with a few days of the
    year before their first full year, so a first day in December
    counts in the next year, and a last day in January in the year
    before.
    """
    first = entity.start_date.year + (entity.start_date.month == 12)
    last = (
        None
        if entity.end_date == "today"
        else entity.end_date.year - (entity.end_date.month == 1)
    )
    start = min(p.start for p in periods)
    ends = [p.end for p in periods]
    end: int | Literal["present"] = (
        "present"
        if "present" in ends
        else max(e for e in ends if e != "present")
    )
    problems = []
    if first < start:
        problems.append(f"DemandCast starts in {first}, the list in {start}")
    if last is None and end != "present":
        problems.append(
            f"DemandCast retrieves until today, the list ends in {end}"
        )
    elif (
        last is not None
        and end == "present"
        and last < registry.current_year()
    ):
        problems.append(f"the list says present, DemandCast ends in {last}")
    elif last is not None and end != "present" and last > end:
        problems.append(f"DemandCast ends in {last}, the list in {end}")
    if not problems:
        return []
    return [
        Finding(
            source=source_id,
            check="years",
            entity=entity.label,
            message="; ".join(problems),
            severity="divergence",
        )
    ]


def _compare_entities(
    source_id: str, source: Source, demandcast: DemandCastSource
) -> list[Finding]:
    """Compare the entities of a source in the two repositories.

    Parameters
    ----------
    source_id : str
        Identifier of the data source.
    source : Source
        The source in the list.
    demandcast : DemandCastSource
        The source in DemandCast.

    Returns
    -------
    list of Finding
        The entities of DemandCast missing from the list, the
        subdivisions named differently and the years that differ.
    """
    periods: dict[str, list[registry.Entity]] = {}
    for listed_entity in source.entities:
        label = _label(
            listed_entity.country_code, listed_entity.subdivision_code
        )
        periods.setdefault(label, []).append(listed_entity)

    findings = []
    for entity in demandcast.entities:
        listed = periods.get(entity.label)
        if listed is None:
            findings.append(
                Finding(
                    source=source_id,
                    check="entity",
                    entity=entity.label,
                    message=f"DemandCast retrieves {entity.label}, which "
                    "the list does not have",
                    severity="divergence",
                )
            )
            continue
        name = listed[0].subdivision_name
        if (
            entity.subdivision_name is not None
            and entity.subdivision_name != name
        ):
            findings.append(
                Finding(
                    source=source_id,
                    check="subdivision",
                    entity=entity.label,
                    message=f"named {entity.subdivision_name!r} in "
                    f"DemandCast and {name!r} in the list",
                    severity="divergence",
                )
            )
        findings += _compare_years(source_id, entity, listed)
    return findings


def _compare_licence(
    source_id: str, source: Source, demandcast: DemandCastSource
) -> list[Finding]:
    """Compare the licence of a source in the two repositories.

    Parameters
    ----------
    source_id : str
        Identifier of the data source.
    source : Source
        The source in the list.
    demandcast : DemandCastSource
        The source in DemandCast.

    Returns
    -------
    list of Finding
        A divergence if DemandCast redistributes data that the list
        calls restricted, or does not redistribute data that the list
        calls open, and a note if they link different pages of terms.

    Notes
    -----
    Data under a non-commercial licence can be redistributed for
    non-commercial uses, so it agrees with either choice of DemandCast.
    The pages of the terms are compared without a trailing slash.
    """
    findings = []
    category = source.licence.category
    redistribute = demandcast.licence.redistribute
    if (redistribute and category == "restricted") or (
        not redistribute and category == "open"
    ):
        allowed = "allows" if redistribute else "does not allow"
        findings.append(
            Finding(
                source=source_id,
                check="licence",
                entity=None,
                message=f"DemandCast {allowed} redistributing the data, "
                f"and the list says {category} ({source.licence.name})",
                severity="divergence",
            )
        )
    if demandcast.licence.url.rstrip("/") != source.licence.url.rstrip("/"):
        findings.append(
            Finding(
                source=source_id,
                check="licence_url",
                entity=None,
                message=f"the terms are {demandcast.licence.url} in "
                f"DemandCast and {source.licence.url} in the list",
                severity="note",
            )
        )
    return findings


def compare(
    sources: dict[str, Source], demandcast: dict[str, DemandCastSource]
) -> list[Finding]:
    """Compare the sources of the list with those of DemandCast.

    Parameters
    ----------
    sources : dict
        The sources of the list, by identifier.
    demandcast : dict
        The sources of DemandCast, by identifier.

    Returns
    -------
    list of Finding
        Every difference, by source.
    """
    findings = []
    for source_id in sorted(set(sources) | set(demandcast)):
        source = sources.get(source_id)
        theirs = demandcast.get(source_id)
        if source is None:
            findings.append(
                Finding(
                    source=source_id,
                    check="source",
                    entity=None,
                    message="DemandCast retrieves this source, which the "
                    "list does not have",
                    severity="divergence",
                )
            )
        elif theirs is None:
            findings.append(
                Finding(
                    source=source_id,
                    check="backlog",
                    entity=None,
                    message=f"DemandCast does not retrieve {source.name} "
                    f"yet (access: {source.access})",
                    severity="note",
                )
            )
        else:
            findings += _compare_entities(source_id, source, theirs)
            findings += _compare_licence(source_id, source, theirs)
    return findings


def apply_differences(
    findings: list[Finding], differences: list[Difference]
) -> list[Finding]:
    """Mark the findings that are accepted differences.

    Parameters
    ----------
    findings : list of Finding
        The findings of the comparison.
    differences : list of Difference
        The accepted differences.

    Returns
    -------
    list of Finding
        The findings, with the reason of the accepted ones, and a note
        for each accepted difference that is no longer found.
    """
    reasons = {(d.source, d.check, d.entity): d.reason for d in differences}
    found = {f.key for f in findings}
    marked = [
        dataclasses.replace(f, accepted=reasons[f.key])
        if f.key in reasons
        else f
        for f in findings
    ]
    for d in differences:
        if (d.source, d.check, d.entity) not in found:
            entity = f" {d.entity}" if d.entity else ""
            marked.append(
                Finding(
                    source=d.source,
                    check="accepted",
                    entity=d.entity,
                    message=f"the accepted difference ({d.check}{entity}) "
                    "is no longer found: remove it from "
                    "demandcast_differences.yaml",
                    severity="note",
                )
            )
    return marked


def introduced(
    findings: list[Finding], base: list[Finding]
) -> tuple[list[Finding], list[Finding]]:
    """Compare the open divergences with those of the base data.

    Parameters
    ----------
    findings : list of Finding
        The findings with the data of a pull request.
    base : list of Finding
        The findings with the data of its base branch.

    Returns
    -------
    added : list of Finding
        The open divergences that the pull request adds.
    resolved : list of Finding
        The open divergences that the pull request resolves.
    """
    now = {(f.key, f.message): f for f in findings if f.is_open}
    before = {(f.key, f.message): f for f in base if f.is_open}
    added = [f for k, f in now.items() if k not in before]
    resolved = [f for k, f in before.items() if k not in now]
    return added, resolved


def _row(finding: Finding) -> str:
    """Return the row of a finding in a Markdown table.

    Parameters
    ----------
    finding : Finding
        The finding.

    Returns
    -------
    str
        The source, the entity, the check and the message.
    """
    cells = [
        f"`{finding.source}`",
        finding.entity or "",
        finding.check,
        finding.message,
    ]
    if finding.accepted is not None:
        cells.append(finding.accepted)
    return "| " + " | ".join(c.replace("|", "\\|") for c in cells) + " |"


def _grouped(findings: list[Finding]) -> list[Finding]:
    """Group the missing entities of each source in one finding.

    Parameters
    ----------
    findings : list of Finding
        The findings.

    Returns
    -------
    list of Finding
        The findings, with one finding for the entities of each source
        that the list lacks, in the place of the first of them.

    Notes
    -----
    The grouping is only for reading: the findings stay one per entity
    in the JSON report and in the accepted differences.
    """
    missing: dict[str, list[str]] = {}
    for f in findings:
        if f.check == "entity" and f.accepted is None and f.entity:
            missing.setdefault(f.source, []).append(f.entity)
    grouped = []
    done: set[str] = set()
    for f in findings:
        entities = missing.get(f.source, [])
        if f.check != "entity" or f.accepted is not None or not entities:
            grouped.append(f)
        elif f.source in done:
            continue
        elif len(entities) == 1:
            grouped.append(f)
            done.add(f.source)
        else:
            grouped.append(
                dataclasses.replace(
                    f,
                    entity=", ".join(entities),
                    message=f"DemandCast retrieves {len(entities)} entities "
                    "that the list does not have",
                )
            )
            done.add(f.source)
    return grouped


def _table(findings: list[Finding], accepted: bool = False) -> list[str]:
    """Return a Markdown table of findings.

    Parameters
    ----------
    findings : list of Finding
        The findings.
    accepted : bool, default False
        Whether to add the column of the reasons of acceptance.

    Returns
    -------
    list of str
        The lines of the table.
    """
    header = "| Source | Entity | Check | Difference |"
    rule = "| --- | --- | --- | --- |"
    if accepted:
        header += " Reason |"
        rule += " --- |"
    return [header, rule, *(_row(f) for f in _grouped(findings))]


def report_markdown(findings: list[Finding], checked_at: dt.datetime) -> str:
    """Write the report of a comparison in Markdown.

    Parameters
    ----------
    findings : list of Finding
        The findings of the comparison.
    checked_at : datetime
        Time of the comparison.

    Returns
    -------
    str
        The open divergences, the accepted ones and the notes.
    """
    open_ = [f for f in findings if f.is_open]
    accepted = [f for f in findings if f.accepted is not None]
    notes = [f for f in findings if f.severity == "note"]
    lines = [
        "## Sync with DemandCast",
        "",
        (
            f"Compared on {checked_at:%Y-%m-%d %H:%M} UTC: {len(open_)} "
            f"open divergences, {len(accepted)} accepted, {len(notes)} "
            "notes."
        ),
    ]
    if open_:
        lines += ["", "### Open divergences", "", *_table(open_)]
    if accepted:
        lines += [
            "",
            "### Accepted differences",
            "",
            *_table(accepted, accepted=True),
        ]
    if notes:
        lines += ["", "### Notes", "", *_table(notes)]
    return "\n".join(lines) + "\n"


def comment_markdown(
    added: list[Finding], resolved: list[Finding]
) -> str | None:
    """Write the comment of a pull request about its divergences.

    Parameters
    ----------
    added : list of Finding
        The divergences that the pull request adds.
    resolved : list of Finding
        The divergences that it resolves.

    Returns
    -------
    str or None
        The comment, or None if the pull request changes no divergence.
    """
    if not added and not resolved:
        return None
    lines = [COMMENT_MARKER, "### Sync with DemandCast", ""]
    if added:
        lines += [
            (
                "This pull request adds divergences from the data sources "
                "of DemandCast, which is the source of truth for the facts "
                "that both state. Align the list with DemandCast; if "
                "DemandCast is outdated, merge and fix it there, and the "
                "`demandcast-sync` issue will track the divergence until "
                "then. If a divergence is deliberate, add it with a reason "
                "to `data/demandcast_differences.yaml`."
            ),
            "",
            *_table(added),
        ]
    if resolved:
        lines += [
            "",
            "This pull request resolves these divergences:",
            "",
            *_table(resolved),
        ]
    return "\n".join(lines) + "\n"


def warning_commands(added: list[Finding], data_dir: Path) -> list[str]:
    """Return the workflow commands that annotate the added divergences.

    Parameters
    ----------
    added : list of Finding
        The divergences that a pull request adds.
    data_dir : Path
        Data folder of the pull request.

    Returns
    -------
    list of str
        One warning per divergence, on the data file of its source if
        the pull request has it.
    """
    lines = []
    for finding in added:
        path = data_dir / "sources" / f"{finding.source}.yaml"
        where = f" file=data/sources/{path.name}," if path.exists() else " "
        text = f"{finding.source} {finding.entity or ''}: {finding.message}"
        text = text.replace("%", "%25").replace("\n", "%0A")
        lines.append(f"::warning{where}title=Sync with DemandCast::{text}")
    return lines


def write_report(
    findings: list[Finding],
    directory: Path,
    checked_at: dt.datetime,
    comment: str | None = None,
) -> None:
    """Write the report of a comparison, and the comment of a PR.

    Parameters
    ----------
    findings : list of Finding
        The findings of the comparison.
    directory : Path
        Folder of the report, created if needed.
    checked_at : datetime
        Time of the comparison.
    comment : str, optional
        Comment of the pull request, written to ``comment.md``.
    """
    directory.mkdir(parents=True, exist_ok=True)
    data = {
        "checked_at": checked_at.isoformat(timespec="seconds"),
        "findings": [
            dataclasses.asdict(f) | {"open": f.is_open} for f in findings
        ],
    }
    (directory / f"{REPORT_NAME}.json").write_text(
        json.dumps(data, ensure_ascii=False, indent=1) + "\n",
        encoding="utf-8",
    )
    (directory / f"{REPORT_NAME}.md").write_text(
        report_markdown(findings, checked_at), encoding="utf-8"
    )
    if comment is not None:
        (directory / "comment.md").write_text(comment, encoding="utf-8")


def _findings(
    data_dir: Path, demandcast: dict[str, DemandCastSource]
) -> list[Finding]:
    """Compare a data folder of the list with DemandCast.

    Parameters
    ----------
    data_dir : Path
        Data folder of the list.
    demandcast : dict
        The sources of DemandCast, by identifier.

    Returns
    -------
    list of Finding
        The findings, with the accepted differences of the folder.
    """
    sources = registry.load_sources(data_dir)
    differences = read_differences(data_dir / DIFFERENCES_FILE.name)
    return apply_differences(compare(sources, demandcast), differences)


def main(argv: list[str] | None = None) -> int:
    """Compare the list with DemandCast and write the report.

    Parameters
    ----------
    argv : list of str, optional
        Arguments of the command, by default those of the process.

    Returns
    -------
    int
        1 if a data file is invalid, 0 otherwise, also when the two
        repositories diverge.
    """
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--demandcast",
        type=Path,
        required=True,
        help="folder of the YAML files of the data sources of DemandCast",
    )
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--data", type=Path, default=DATA_DIR)
    parser.add_argument(
        "--base-data",
        type=Path,
        help="data folder of the base branch of a pull request",
    )
    args = parser.parse_args(argv)

    try:
        demandcast = read_demandcast(args.demandcast)
        findings = _findings(args.data, demandcast)
    except (RegistryError, SyncError) as e:
        logger.error("Invalid files:\n%s", e)  # noqa: TRY400
        return 1

    comment = None
    if args.base_data is not None:
        try:
            base = _findings(args.base_data, demandcast)
        except (RegistryError, SyncError):
            logger.info("The base data cannot be compared: all is new.")
            base = []
        added, resolved = introduced(findings, base)
        comment = comment_markdown(added, resolved)
        for line in warning_commands(added, args.data):
            sys.stdout.write(line + "\n")

    write_report(findings, args.output, dt.datetime.now(dt.UTC), comment)
    open_ = sum(f.is_open for f in findings)
    logger.info("%d findings, %d open divergences.", len(findings), open_)
    return 0


if __name__ == "__main__":
    sys.exit(main())
