from __future__ import annotations

import json
import os
from pathlib import Path

import typer

from autoscholar.analysis import assess_idea
from autoscholar.citation import build_shortlist, run_correction, run_prescreen, run_search, write_bibtex
from autoscholar.citation.config import CitationRulesConfig, IdeaEvaluationConfig, RecommendationConfig, SearchConfig
from autoscholar.io import read_json, read_json_list, read_json_model, read_jsonl, read_yaml
from autoscholar.models import (
    ClaimRecord,
    EvidenceMapRecord,
    IdeaAssessmentRecord,
    QueryRecord,
    QueryReviewRecord,
    RecommendationCorrectionRecord,
    ReportValidationBundleRecord,
    SearchFailureRecord,
    SearchResultRecord,
    SelectedCitationRecord,
    WorkspaceManifest,
    export_json_schemas,
)
from autoscholar.reporting import build_evidence_map, render_report, validate_report
from autoscholar.utils import pdf_to_text
from autoscholar.workspace import Workspace, dump_manifest, workspace_summary
from autoscholar.integrations import SemanticScholarClient

app = typer.Typer(help="AutoScholar v2 unified CLI.")
workspace_app = typer.Typer(help="Workspace management.")
citation_app = typer.Typer(help="Citation workflow commands.")
idea_app = typer.Typer(help="Idea analysis workflow commands.")
report_app = typer.Typer(help="Report rendering commands.")
schema_app = typer.Typer(help="JSON schema export commands.")
semantic_app = typer.Typer(help="Low-level Semantic Scholar API commands.")
util_app = typer.Typer(help="Utility commands.")

app.add_typer(workspace_app, name="workspace")
app.add_typer(citation_app, name="citation")
app.add_typer(idea_app, name="idea")
app.add_typer(report_app, name="report")
app.add_typer(schema_app, name="schema")
app.add_typer(semantic_app, name="semantic")
app.add_typer(util_app, name="util")


def _load_workspace(path: Path) -> Workspace:
    return Workspace.load(path)


def _dump_json(payload: object) -> None:
    typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))


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

    for path, model in (
        (workspace.require_path("artifacts", "evidence_map"), EvidenceMapRecord),
        (workspace.require_path("artifacts", "report_validation"), ReportValidationBundleRecord),
    ):
        try:
            if path.exists():
                payload = read_json(path)
                if payload:
                    read_json_model(path, model)
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
    config = _load_idea_config(workspace)
    assessment = assess_idea(workspace, config)
    build_evidence_map(workspace, config)
    typer.echo(f"Idea assessment complete. recommendation={assessment.recommendation}")


@report_app.command("render")
def report_render(
    workspace_dir: Path = typer.Option(..., "--workspace"),
    kind: str = typer.Option(..., "--kind", help="prescreen, shortlist, feasibility, or deep-dive"),
) -> None:
    normalized_kind = "deep-dive" if kind == "deep-dive" else kind
    path = render_report(_load_workspace(workspace_dir), normalized_kind)
    typer.echo(f"Wrote report: {path}")


@report_app.command("validate")
def report_validate(
    workspace_dir: Path = typer.Option(..., "--workspace"),
    kind: str = typer.Option(..., "--kind", help="feasibility or deep-dive"),
) -> None:
    normalized_kind = "deep-dive" if kind == "deep-dive" else kind
    if normalized_kind not in {"feasibility", "deep-dive"}:
        raise typer.BadParameter("kind must be feasibility or deep-dive")
    workspace = _load_workspace(workspace_dir)
    record = validate_report(workspace, normalized_kind, _load_idea_config(workspace))
    typer.echo(f"Report validation passed={record.passed}")
    for issue in record.issues:
        typer.echo(f"- {issue.level}: {issue.code}: {issue.message}")
    if not record.passed:
        raise typer.Exit(code=1)


@schema_app.command("export")
def schema_export(output_dir: Path = typer.Option(..., "--output-dir")) -> None:
    written = export_json_schemas(output_dir)
    for path in written:
        typer.echo(f"Wrote: {path}")


@util_app.command("pdf-to-text")
def util_pdf_to_text(
    input_pdf: Path,
    output_txt: Path | None = typer.Option(None, "--output"),
) -> None:
    output_path = pdf_to_text(input_pdf, output_txt)
    typer.echo(f"Wrote text: {output_path}")


@semantic_app.command("paper")
def semantic_paper(
    paper_id: str,
    fields: str = typer.Option("paperId,title,authors,year,abstract", "--fields"),
    timeout: float | None = typer.Option(None, "--timeout"),
) -> None:
    with SemanticScholarClient(timeout=timeout) as client:
        _dump_json(client.get_paper(paper_id, fields=fields, timeout=timeout))


@semantic_app.command("search")
def semantic_search(
    query: str,
    limit: int = typer.Option(5, "--limit"),
    fields: str = typer.Option("paperId,title,year,authors,url,abstract", "--fields"),
    endpoint: str = typer.Option("relevance", "--endpoint"),
    year: str | None = typer.Option(None, "--year"),
    sort: str | None = typer.Option(None, "--sort"),
    venue: str | None = typer.Option(None, "--venue"),
    timeout: float | None = typer.Option(None, "--timeout"),
) -> None:
    with SemanticScholarClient(timeout=timeout) as client:
        if endpoint == "bulk":
            payload = list(
                client.search_papers_bulk(
                    query=query,
                    fields=fields,
                    max_results=limit,
                    year=year,
                    sort=sort,
                    venue=venue,
                    timeout=timeout,
                )
            )
            _dump_json({"endpoint": endpoint, "query": query, "count": len(payload), "data": payload})
            return
        _dump_json(client.search_papers(query=query, limit=limit, fields=fields, timeout=timeout))


@semantic_app.command("recommend")
def semantic_recommend(
    paper_id: str,
    limit: int = typer.Option(5, "--limit"),
    fields: str = typer.Option("paperId,title,year,authors,url", "--fields"),
    timeout: float | None = typer.Option(None, "--timeout"),
) -> None:
    with SemanticScholarClient(timeout=timeout) as client:
        _dump_json(client.get_recommendations(paper_id=paper_id, limit=limit, fields=fields, timeout=timeout))


@semantic_app.command("citations")
def semantic_citations(
    paper_id: str,
    fields: str = typer.Option("paperId,title,year,authors,url", "--fields"),
    timeout: float | None = typer.Option(None, "--timeout"),
) -> None:
    with SemanticScholarClient(timeout=timeout) as client:
        _dump_json(client.get_paper_citations(paper_id=paper_id, fields=fields, timeout=timeout))


@semantic_app.command("references")
def semantic_references(
    paper_id: str,
    fields: str = typer.Option("paperId,title,year,authors,url", "--fields"),
    timeout: float | None = typer.Option(None, "--timeout"),
) -> None:
    with SemanticScholarClient(timeout=timeout) as client:
        _dump_json(client.get_paper_references(paper_id=paper_id, fields=fields, timeout=timeout))


@semantic_app.command("author-search")
def semantic_author_search(
    query: str,
    fields: str = typer.Option("authorId,name,url", "--fields"),
    timeout: float | None = typer.Option(None, "--timeout"),
) -> None:
    with SemanticScholarClient(timeout=timeout) as client:
        _dump_json(client.search_author(query=query, fields=fields, timeout=timeout))


@semantic_app.command("author")
def semantic_author(
    author_id: str,
    fields: str = typer.Option("authorId,name,url,paperCount,citationCount", "--fields"),
    timeout: float | None = typer.Option(None, "--timeout"),
) -> None:
    with SemanticScholarClient(timeout=timeout) as client:
        _dump_json(client.get_author(author_id=author_id, fields=fields, timeout=timeout))


@semantic_app.command("author-papers")
def semantic_author_papers(
    author_id: str,
    limit: int = typer.Option(20, "--limit"),
    fields: str = typer.Option("paperId,title,year,authors,url", "--fields"),
    timeout: float | None = typer.Option(None, "--timeout"),
) -> None:
    with SemanticScholarClient(timeout=timeout) as client:
        _dump_json(client.get_author_papers(author_id=author_id, limit=limit, fields=fields, timeout=timeout))


@semantic_app.command("download-pdf")
def semantic_download_pdf(
    paper_id: str,
    directory: Path = typer.Option(Path("papers"), "--directory"),
    timeout: float | None = typer.Option(None, "--timeout"),
) -> None:
    with SemanticScholarClient(timeout=timeout) as client:
        output_path = client.download_open_access_pdf(paper_id=paper_id, directory=directory, timeout=timeout)
    if output_path is None:
        typer.echo("No open access PDF was available.")
        raise typer.Exit(code=1)
    typer.echo(f"Downloaded PDF: {output_path}")


@semantic_app.command("smoke")
def semantic_smoke(
    query: str = typer.Option("medical image segmentation", "--query"),
    timeout: float = typer.Option(30.0, "--timeout"),
) -> None:
    if not os.environ.get("S2_API_KEY"):
        typer.echo("S2_API_KEY is not set; live smoke test skipped.")
        return

    with SemanticScholarClient(timeout=timeout) as client:
        search_payload = client.search_papers(
            query=query,
            limit=1,
            fields="paperId,title,year",
            timeout=timeout,
        )
        papers = search_payload.get("data", [])
        if not papers:
            typer.echo("Live smoke test failed: search returned no papers.")
            raise typer.Exit(code=1)
        paper_id = papers[0].get("paperId")
        if not paper_id:
            typer.echo("Live smoke test failed: top search result had no paperId.")
            raise typer.Exit(code=1)
        recommendations = client.get_recommendations(
            paper_id=paper_id,
            limit=1,
            fields="paperId,title,year",
            timeout=timeout,
        )

    _dump_json(
        {
            "query": query,
            "top_paper": papers[0],
            "recommendation_count": len(recommendations),
            "recommendations": recommendations,
        }
    )


if __name__ == "__main__":
    app()
