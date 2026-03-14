from __future__ import annotations

from pathlib import Path

import typer

from autoscholar.analysis import assess_idea
from autoscholar.citation import build_shortlist, run_correction, run_prescreen, run_search, write_bibtex
from autoscholar.citation.config import CitationRulesConfig, IdeaEvaluationConfig, RecommendationConfig, SearchConfig
from autoscholar.io import read_json, read_json_list, read_json_model, read_jsonl, read_yaml
from autoscholar.models import (
    ClaimRecord,
    IdeaAssessmentRecord,
    QueryRecord,
    QueryReviewRecord,
    RecommendationCorrectionRecord,
    SearchFailureRecord,
    SearchResultRecord,
    SelectedCitationRecord,
    WorkspaceManifest,
    export_json_schemas,
)
from autoscholar.reporting import render_report
from autoscholar.workspace import Workspace, dump_manifest, workspace_summary

app = typer.Typer(help="AutoScholar v2 unified CLI.")
workspace_app = typer.Typer(help="Workspace management.")
citation_app = typer.Typer(help="Citation workflow commands.")
idea_app = typer.Typer(help="Idea analysis workflow commands.")
report_app = typer.Typer(help="Report rendering commands.")
schema_app = typer.Typer(help="JSON schema export commands.")

app.add_typer(workspace_app, name="workspace")
app.add_typer(citation_app, name="citation")
app.add_typer(idea_app, name="idea")
app.add_typer(report_app, name="report")
app.add_typer(schema_app, name="schema")


def _load_workspace(path: Path) -> Workspace:
    return Workspace.load(path)


def _load_search_config(workspace: Workspace) -> SearchConfig:
    return SearchConfig.model_validate(read_yaml(workspace.require_path("configs", "search")))


def _load_recommendation_config(workspace: Workspace) -> RecommendationConfig:
    return RecommendationConfig.model_validate(read_yaml(workspace.require_path("configs", "recommendation")))


def _load_rules(workspace: Workspace) -> CitationRulesConfig:
    return CitationRulesConfig.model_validate(read_yaml(workspace.require_path("configs", "citation_rules")))


def _load_idea_config(workspace: Workspace) -> IdeaEvaluationConfig:
    return IdeaEvaluationConfig.model_validate(read_yaml(workspace.require_path("configs", "idea_evaluation")))


@workspace_app.command("init")
def workspace_init(
    target_dir: Path,
    template: str = typer.Option(..., "--template", help="citation-paper or idea-evaluation"),
    reports_lang: str = typer.Option("zh", "--reports-lang", help="zh or en"),
) -> None:
    workspace = Workspace.init(
        root=target_dir,
        template=template,  # type: ignore[arg-type]
        reports_lang=reports_lang,  # type: ignore[arg-type]
    )
    typer.echo(f"Initialized workspace: {workspace.root}")
    typer.echo(dump_manifest(workspace).strip())


@workspace_app.command("doctor")
def workspace_doctor(workspace_dir: Path = typer.Option(..., "--workspace")) -> None:
    workspace = _load_workspace(workspace_dir)
    issues = workspace.doctor()
    for loader in (
        lambda: WorkspaceManifest.model_validate(read_yaml(workspace.root / "workspace.yaml")),
        lambda: SearchConfig.model_validate(read_yaml(workspace.require_path("configs", "search"))),
        lambda: RecommendationConfig.model_validate(read_yaml(workspace.require_path("configs", "recommendation"))),
        lambda: CitationRulesConfig.model_validate(read_yaml(workspace.require_path("configs", "citation_rules"))),
        lambda: IdeaEvaluationConfig.model_validate(read_yaml(workspace.require_path("configs", "idea_evaluation"))),
    ):
        try:
            loader()
        except Exception as exc:
            issues.append(str(exc))

    for path, model in (
        (workspace.require_path("artifacts", "claims"), ClaimRecord),
        (workspace.require_path("artifacts", "queries"), QueryRecord),
        (workspace.require_path("artifacts", "search_results_raw"), SearchResultRecord),
        (workspace.require_path("artifacts", "search_results_deduped"), SearchResultRecord),
        (workspace.require_path("artifacts", "search_failures"), SearchFailureRecord),
        (workspace.require_path("artifacts", "recommendation_corrections"), RecommendationCorrectionRecord),
        (workspace.require_path("artifacts", "selected_citations"), SelectedCitationRecord),
    ):
        try:
            if path.exists() and path.read_text(encoding="utf-8").strip():
                read_jsonl(path, model)
        except Exception as exc:
            issues.append(str(exc))

    try:
        query_reviews_path = workspace.require_path("artifacts", "query_reviews")
        if query_reviews_path.exists():
            read_json_list(query_reviews_path, "query_reviews", QueryReviewRecord)
    except Exception as exc:
        issues.append(str(exc))

    idea_assessment_path = workspace.require_path("artifacts", "idea_assessment")
    try:
        if idea_assessment_path.exists():
            payload = read_json(idea_assessment_path)
            if payload:
                read_json_model(idea_assessment_path, IdeaAssessmentRecord)
    except Exception as exc:
        issues.append(str(exc))

    summary = workspace_summary(workspace)
    typer.echo(f"Workspace: {summary['root']}")
    typer.echo(f"Type: {summary['workspace_type']}")
    typer.echo(f"Report language: {summary['report_language']}")
    if issues:
        typer.echo("Issues:")
        for issue in issues:
            typer.echo(f"- {issue}")
        raise typer.Exit(code=1)
    typer.echo("Workspace is valid.")


@citation_app.command("search")
def citation_search(workspace_dir: Path = typer.Option(..., "--workspace")) -> None:
    workspace = _load_workspace(workspace_dir)
    success_count, failure_count = run_search(workspace, _load_search_config(workspace))
    typer.echo(f"Search complete. success={success_count} failure={failure_count}")


@citation_app.command("prescreen")
def citation_prescreen(workspace_dir: Path = typer.Option(..., "--workspace")) -> None:
    workspace = _load_workspace(workspace_dir)
    reviews = run_prescreen(workspace, _load_rules(workspace))
    typer.echo(f"Prescreen complete. query_reviews={len(reviews)}")


@citation_app.command("correct")
def citation_correct(workspace_dir: Path = typer.Option(..., "--workspace")) -> None:
    workspace = _load_workspace(workspace_dir)
    records = run_correction(
        workspace=workspace,
        rules=_load_rules(workspace),
        config=_load_recommendation_config(workspace),
    )
    typer.echo(f"Correction complete. triggered_claims={len(records)}")


@citation_app.command("shortlist")
def citation_shortlist(workspace_dir: Path = typer.Option(..., "--workspace")) -> None:
    workspace = _load_workspace(workspace_dir)
    records = build_shortlist(workspace, _load_rules(workspace))
    typer.echo(f"Shortlist complete. claims={len(records)}")


@citation_app.command("bib")
def citation_bib(workspace_dir: Path = typer.Option(..., "--workspace")) -> None:
    workspace = _load_workspace(workspace_dir)
    entry_count, _ = write_bibtex(workspace)
    typer.echo(f"Wrote BibTeX entries: {entry_count}")


@idea_app.command("assess")
def idea_assess(workspace_dir: Path = typer.Option(..., "--workspace")) -> None:
    workspace = _load_workspace(workspace_dir)
    assessment = assess_idea(workspace, _load_idea_config(workspace))
    typer.echo(f"Idea assessment complete. recommendation={assessment.recommendation}")


@report_app.command("render")
def report_render(
    workspace_dir: Path = typer.Option(..., "--workspace"),
    kind: str = typer.Option(..., "--kind", help="prescreen, shortlist, feasibility, or deep-dive"),
) -> None:
    normalized_kind = "deep-dive" if kind == "deep-dive" else kind
    path = render_report(_load_workspace(workspace_dir), normalized_kind)
    typer.echo(f"Wrote report: {path}")


@schema_app.command("export")
def schema_export(output_dir: Path = typer.Option(..., "--output-dir")) -> None:
    written = export_json_schemas(output_dir)
    for path in written:
        typer.echo(f"Wrote: {path}")


if __name__ == "__main__":
    app()
