from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

console = Console()

RISK_COLORS = {
    "safe": "green",
    "low": "cyan",
    "medium": "yellow",
    "high": "red",
    "critical": "bold red",
    "pending": "dim",
}


def print_skill_card(skill: dict) -> None:
    risk = skill["security"]["level"]
    score = skill["security"]["score"]
    color = RISK_COLORS.get(risk, "white")

    header = Text()
    header.append(skill["name"], style="bold")
    header.append(f"  v{skill.get('version', '?')}", style="dim")
    header.append(f"  by {skill['author']}", style="dim")

    console.print(Panel(
        f"{skill['description']}\n\n"
        f"[bold]Security:[/bold] [{color}]{risk}[/{color}] (score: {score}/100)\n"
        f"[bold]Tags:[/bold] {', '.join(skill.get('tags', []))}\n"
        f"[bold]Downloads:[/bold] {skill['downloads']:,}  [bold]Stars:[/bold] {skill['stars']:,}",
        title=header,
        border_style=color,
    ))


def print_security_summary(skill: dict) -> None:
    risk = skill["security"]["level"]
    score = skill["security"]["score"]
    color = RISK_COLORS.get(risk, "white")
    findings = skill["security"].get("findings", [])

    console.print(f"\n[bold]Security Summary[/bold] — [{color}]{risk.upper()}[/{color}] ({score}/100)")
    if findings:
        for f in findings:
            sev_color = RISK_COLORS.get(f["severity"], "white")
            console.print(f"  [{sev_color}][{f['severity'].upper()}][/{sev_color}] {f['title']}")
            if f.get("recommendation"):
                console.print(f"    → {f['recommendation']}", style="dim")
    else:
        console.print("  No findings.", style="dim")


def print_install_success(slug: str, install_dir: str | None = None) -> None:
    msg = f"Skill '{slug}' installed successfully!"
    if install_dir:
        msg += f"\nLocation: {install_dir}"
    console.print(Panel(msg, title="Installed", border_style="green"))


def print_skills_table(skills: list[dict]) -> None:
    table = Table(title="Skills", show_lines=False)
    table.add_column("Name", style="bold")
    table.add_column("Risk", justify="center")
    table.add_column("Score", justify="right")
    table.add_column("Downloads", justify="right")
    table.add_column("Stars", justify="right")
    table.add_column("Tags")

    for s in skills:
        risk = s["security"]["level"]
        color = RISK_COLORS.get(risk, "white")
        table.add_row(
            s["name"],
            f"[{color}]{risk}[/{color}]",
            str(s["security"]["score"]),
            f"{s['downloads']:,}",
            f"{s['stars']:,}",
            ", ".join(s.get("tags", [])[:3]),
        )

    console.print(table)


def print_error(message: str) -> None:
    console.print(f"[bold red]Error:[/bold red] {message}")
