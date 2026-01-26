"""CLI application for OuraCLI."""

from enum import Enum
from typing import Any, Literal

import typer

from ouracli.client import OuraClient
from ouracli.date_parser import parse_date_range
from ouracli.formatters import format_output
from ouracli.llm_help import show_llm_help

app = typer.Typer(
    help=(
        "CLI tool for accessing Oura Ring data.\n"
        "💡 LLMs/agents: run 'ouracli --ai-help' for detailed usage guidance."
    ),
    context_settings={"help_option_names": ["-h", "--help"]},
)


@app.callback(invoke_without_command=True)
def main_callback(
    ctx: typer.Context,
    ai_help: bool = typer.Option(
        False,
        "--ai-help",
        is_eager=True,
        help="Show comprehensive usage guide for LLMs/agents and exit.",
    ),
    ai_help_format: Literal["markdown", "json"] = typer.Option(
        "markdown",
        "--ai-help-format",
        help="Format for --ai-help output (markdown or json)",
        show_choices=True,
        case_sensitive=False,
    ),
) -> None:
    """CLI tool for accessing Oura Ring data."""
    # If --ai-help requested, emit dashdash-spec help and exit early
    if ai_help:
        typer.echo(show_llm_help(format_type=ai_help_format))
        raise typer.Exit()

    # If no command was invoked, show help
    if ctx.invoked_subcommand is None:
        typer.echo(ctx.get_help())
        raise typer.Exit()


class OutputFormat(str, Enum):
    """Output format options."""

    TREE = "tree"
    JSON = "json"
    DATAFRAME = "dataframe"
    MARKDOWN = "markdown"
    HTML = "html"


def get_output_format(
    json_flag: bool,
    tree_flag: bool,
    markdown_flag: bool,
    dataframe_flag: bool,
    html_flag: bool,
) -> str:
    """Determine output format from flags. Tree is default."""
    format_flags = [
        (json_flag, "json"),
        (tree_flag, "tree"),
        (markdown_flag, "markdown"),
        (dataframe_flag, "dataframe"),
        (html_flag, "html"),
    ]
    active_flags = [fmt for flag, fmt in format_flags if flag]

    if len(active_flags) > 1:
        raise typer.BadParameter(
            "Only one format flag can be specified at a time: "
            "--json, --tree, --markdown, --dataframe, or --html"
        )

    return active_flags[0] if active_flags else "tree"


def create_format_options() -> tuple[
    typer.models.OptionInfo,
    typer.models.OptionInfo,
    typer.models.OptionInfo,
    typer.models.OptionInfo,
    typer.models.OptionInfo,
]:
    """Create standard format option flags for commands."""
    return (
        typer.Option(False, "--json", help="Output as JSON"),
        typer.Option(False, "--tree", help="Output as tree (default)"),
        typer.Option(False, "--markdown", help="Output as markdown"),
        typer.Option(False, "--dataframe", help="Output as dataframe"),
        typer.Option(False, "--html", help="Output as HTML"),
    )


def execute_data_command(
    date_range: str,
    fetch_func: Any,
    output_format: str,
    wrap_key: str | None = None,
) -> None:
    """Execute a standard data fetching command.

    Args:
        date_range: Date range string to parse
        fetch_func: Client method to fetch data (receives start_date, end_date)
        output_format: Format for output
        wrap_key: Optional key to wrap list results for markdown/html
    """
    client = OuraClient()
    start_date, end_date = parse_date_range(date_range)
    data = fetch_func(client, start_date, end_date)
    result = data.get("data", [])

    # Wrap in dict with category key for proper heading in markdown/html
    if wrap_key and output_format in ("markdown", "html") and isinstance(result, list):
        result = {wrap_key: result}

    output = format_output(result, output_format)
    typer.echo(output)


@app.command()
def activity(
    date_range: str = typer.Argument("today", help="Date range (e.g., 'today', '7 days')"),
    json_flag: bool = typer.Option(False, "--json", help="Output as JSON"),
    tree_flag: bool = typer.Option(False, "--tree", help="Output as tree (default)"),
    markdown_flag: bool = typer.Option(False, "--markdown", help="Output as markdown"),
    dataframe_flag: bool = typer.Option(False, "--dataframe", help="Output as dataframe"),
    html_flag: bool = typer.Option(False, "--html", help="Output as HTML"),
) -> None:
    """Get daily activity data."""
    output_format = get_output_format(
        json_flag, tree_flag, markdown_flag, dataframe_flag, html_flag
    )
    execute_data_command(
        date_range,
        lambda c, s, e: c.get_daily_activity(s, e),
        output_format,
        "activity",
    )


@app.command()
def sleep(
    date_range: str = typer.Argument("today", help="Date range (e.g., 'today', '7 days')"),
    json_flag: bool = typer.Option(False, "--json", help="Output as JSON"),
    tree_flag: bool = typer.Option(False, "--tree", help="Output as tree (default)"),
    markdown_flag: bool = typer.Option(False, "--markdown", help="Output as markdown"),
    dataframe_flag: bool = typer.Option(False, "--dataframe", help="Output as dataframe"),
    html_flag: bool = typer.Option(False, "--html", help="Output as HTML"),
) -> None:
    """Get daily sleep data."""
    output_format = get_output_format(
        json_flag, tree_flag, markdown_flag, dataframe_flag, html_flag
    )
    execute_data_command(date_range, lambda c, s, e: c.get_daily_sleep(s, e), output_format)


@app.command()
def readiness(
    date_range: str = typer.Argument("today", help="Date range (e.g., 'today', '7 days')"),
    json_flag: bool = typer.Option(False, "--json", help="Output as JSON"),
    tree_flag: bool = typer.Option(False, "--tree", help="Output as tree (default)"),
    markdown_flag: bool = typer.Option(False, "--markdown", help="Output as markdown"),
    dataframe_flag: bool = typer.Option(False, "--dataframe", help="Output as dataframe"),
    html_flag: bool = typer.Option(False, "--html", help="Output as HTML"),
) -> None:
    """Get daily readiness data."""
    output_format = get_output_format(
        json_flag, tree_flag, markdown_flag, dataframe_flag, html_flag
    )
    execute_data_command(date_range, lambda c, s, e: c.get_daily_readiness(s, e), output_format)


@app.command()
def spo2(
    date_range: str = typer.Argument("today", help="Date range (e.g., 'today', '7 days')"),
    json_flag: bool = typer.Option(False, "--json", help="Output as JSON"),
    tree_flag: bool = typer.Option(False, "--tree", help="Output as tree (default)"),
    markdown_flag: bool = typer.Option(False, "--markdown", help="Output as markdown"),
    dataframe_flag: bool = typer.Option(False, "--dataframe", help="Output as dataframe"),
    html_flag: bool = typer.Option(False, "--html", help="Output as HTML"),
) -> None:
    """Get daily SpO2 data."""
    output_format = get_output_format(
        json_flag, tree_flag, markdown_flag, dataframe_flag, html_flag
    )
    execute_data_command(date_range, lambda c, s, e: c.get_daily_spo2(s, e), output_format)


@app.command()
def stress(
    date_range: str = typer.Argument("today", help="Date range (e.g., 'today', '7 days')"),
    json_flag: bool = typer.Option(False, "--json", help="Output as JSON"),
    tree_flag: bool = typer.Option(False, "--tree", help="Output as tree (default)"),
    markdown_flag: bool = typer.Option(False, "--markdown", help="Output as markdown"),
    dataframe_flag: bool = typer.Option(False, "--dataframe", help="Output as dataframe"),
    html_flag: bool = typer.Option(False, "--html", help="Output as HTML"),
) -> None:
    """Get daily stress data."""
    output_format = get_output_format(
        json_flag, tree_flag, markdown_flag, dataframe_flag, html_flag
    )
    execute_data_command(date_range, lambda c, s, e: c.get_daily_stress(s, e), output_format)


@app.command()
def heartrate(
    date_range: str = typer.Argument("today", help="Date range (e.g., 'today', '7 days')"),
    json_flag: bool = typer.Option(False, "--json", help="Output as JSON"),
    tree_flag: bool = typer.Option(False, "--tree", help="Output as tree (default)"),
    markdown_flag: bool = typer.Option(False, "--markdown", help="Output as markdown"),
    dataframe_flag: bool = typer.Option(False, "--dataframe", help="Output as dataframe"),
    html_flag: bool = typer.Option(False, "--html", help="Output as HTML"),
) -> None:
    """Get heart rate time series data."""
    output_format = get_output_format(
        json_flag, tree_flag, markdown_flag, dataframe_flag, html_flag
    )
    # Heartrate endpoint uses datetime format, not just dates
    execute_data_command(
        date_range,
        lambda c, s, e: c.get_heartrate(f"{s}T00:00:00", f"{e}T23:59:59"),
        output_format,
    )


@app.command()
def workout(
    date_range: str = typer.Argument("today", help="Date range (e.g., 'today', '7 days')"),
    json_flag: bool = typer.Option(False, "--json", help="Output as JSON"),
    tree_flag: bool = typer.Option(False, "--tree", help="Output as tree (default)"),
    markdown_flag: bool = typer.Option(False, "--markdown", help="Output as markdown"),
    dataframe_flag: bool = typer.Option(False, "--dataframe", help="Output as dataframe"),
    html_flag: bool = typer.Option(False, "--html", help="Output as HTML"),
) -> None:
    """Get workout data."""
    output_format = get_output_format(
        json_flag, tree_flag, markdown_flag, dataframe_flag, html_flag
    )
    execute_data_command(date_range, lambda c, s, e: c.get_workouts(s, e), output_format)


@app.command()
def session(
    date_range: str = typer.Argument("today", help="Date range (e.g., 'today', '7 days')"),
    json_flag: bool = typer.Option(False, "--json", help="Output as JSON"),
    tree_flag: bool = typer.Option(False, "--tree", help="Output as tree (default)"),
    markdown_flag: bool = typer.Option(False, "--markdown", help="Output as markdown"),
    dataframe_flag: bool = typer.Option(False, "--dataframe", help="Output as dataframe"),
    html_flag: bool = typer.Option(False, "--html", help="Output as HTML"),
) -> None:
    """Get session data."""
    output_format = get_output_format(
        json_flag, tree_flag, markdown_flag, dataframe_flag, html_flag
    )
    execute_data_command(date_range, lambda c, s, e: c.get_sessions(s, e), output_format)


@app.command()
def tag(
    date_range: str = typer.Argument("today", help="Date range (e.g., 'today', '7 days')"),
    json_flag: bool = typer.Option(False, "--json", help="Output as JSON"),
    tree_flag: bool = typer.Option(False, "--tree", help="Output as tree (default)"),
    markdown_flag: bool = typer.Option(False, "--markdown", help="Output as markdown"),
    dataframe_flag: bool = typer.Option(False, "--dataframe", help="Output as dataframe"),
    html_flag: bool = typer.Option(False, "--html", help="Output as HTML"),
) -> None:
    """Get tag data."""
    output_format = get_output_format(
        json_flag, tree_flag, markdown_flag, dataframe_flag, html_flag
    )
    execute_data_command(date_range, lambda c, s, e: c.get_tags(s, e), output_format)


@app.command()
def rest_mode(
    date_range: str = typer.Argument("today", help="Date range (e.g., 'today', '7 days')"),
    json_flag: bool = typer.Option(False, "--json", help="Output as JSON"),
    tree_flag: bool = typer.Option(False, "--tree", help="Output as tree (default)"),
    markdown_flag: bool = typer.Option(False, "--markdown", help="Output as markdown"),
    dataframe_flag: bool = typer.Option(False, "--dataframe", help="Output as dataframe"),
    html_flag: bool = typer.Option(False, "--html", help="Output as HTML"),
) -> None:
    """Get rest mode periods."""
    output_format = get_output_format(
        json_flag, tree_flag, markdown_flag, dataframe_flag, html_flag
    )
    execute_data_command(date_range, lambda c, s, e: c.get_rest_mode_periods(s, e), output_format)


@app.command()
def personal_info(
    json_flag: bool = typer.Option(False, "--json", help="Output as JSON"),
    tree_flag: bool = typer.Option(False, "--tree", help="Output as tree (default)"),
    markdown_flag: bool = typer.Option(False, "--markdown", help="Output as markdown"),
    dataframe_flag: bool = typer.Option(False, "--dataframe", help="Output as dataframe"),
    html_flag: bool = typer.Option(False, "--html", help="Output as HTML"),
) -> None:
    """Get personal information."""
    output_format = get_output_format(
        json_flag, tree_flag, markdown_flag, dataframe_flag, html_flag
    )
    client = OuraClient()
    data = client.get_personal_info()
    output = format_output(data, output_format)
    typer.echo(output)


@app.command(name="all")
def get_all(
    date_range: str = typer.Argument("today", help="Date range (e.g., 'today', '7 days')"),
    json_flag: bool = typer.Option(False, "--json", help="Output as JSON"),
    tree_flag: bool = typer.Option(False, "--tree", help="Output as tree (default)"),
    markdown_flag: bool = typer.Option(False, "--markdown", help="Output as markdown"),
    dataframe_flag: bool = typer.Option(False, "--dataframe", help="Output as dataframe"),
    html_flag: bool = typer.Option(False, "--html", help="Output as HTML"),
    by_day_flag: bool = typer.Option(
        True,
        "--by-day/--by-method",
        help="Group data by day (default) or by method",
    ),
) -> None:
    """Get all available data."""
    output_format = get_output_format(
        json_flag, tree_flag, markdown_flag, dataframe_flag, html_flag
    )
    client = OuraClient()
    start_date, end_date = parse_date_range(date_range)
    data = client.get_all_data(start_date, end_date)
    output = format_output(data, output_format, by_day=by_day_flag)
    typer.echo(output)


def main() -> None:
    """Main entry point for the CLI."""
    app()


if __name__ == "__main__":
    main()
