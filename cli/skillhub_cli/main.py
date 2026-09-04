from pathlib import Path

import typer
from rich.console import Console

from skillhub_cli import __version__
from skillhub_cli.api import SkillHubAPI
from skillhub_cli.display import (
    console,
    print_error,
    print_install_success,
    print_security_summary,
    print_skill_card,
    print_skills_table,
)

app = typer.Typer(
    name="skillhub",
    help="SkillHub CLI — discover, audit, and install AI Agent Skills",
    no_args_is_help=True,
)

SKILL_DIR = Path.home() / ".claude" / "skills"


def version_callback(value: bool) -> None:
    if value:
        console.print(f"skillhub-cli {__version__}")
        raise typer.Exit()


@app.callback()
def main(
    version: bool = typer.Option(False, "--version", "-V", callback=version_callback, is_eager=True),
) -> None:
    pass


@app.command()
def install(
    slug: str = typer.Argument(help="Skill slug to install"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Preview without installing"),
    api_url: str = typer.Option("http://localhost:8000/api/v1", "--api-url", envvar="SKILLHUB_API_URL"),
) -> None:
    """Install a skill from SkillHub."""
    api = SkillHubAPI(base_url=api_url)
    try:
        skill = api.get_skill(slug)
        print_security_summary(skill)

        risk = skill["security"]["level"]
        if risk in ("high", "critical"):
            console.print(f"\n[bold red]WARNING:[/bold red] This skill has a '{risk}' risk level.")
            confirm = typer.confirm("Are you sure you want to install it?")
            if not confirm:
                console.print("Installation cancelled.")
                raise typer.Exit()

        if dry_run:
            console.print(f"\n[bold]Dry run:[/bold] Would install '{slug}'")
            console.print(f"  Command: {skill.get('installCommand', f'skillhub install {slug}')}")
            raise typer.Exit()

        install_data = api.install_skill(slug)
        skill_md = install_data.get("skill_md")
        if skill_md:
            target = SKILL_DIR / slug
            target.mkdir(parents=True, exist_ok=True)
            (target / "CLAUDE.md").write_text(skill_md, encoding="utf-8")
            print_install_success(slug, str(target))
        else:
            print_install_success(slug)

    except typer.Exit:
        raise
    except Exception as e:
        print_error(str(e))
        raise typer.Exit(code=1)
    finally:
        api.close()


@app.command()
def uninstall(
    slug: str = typer.Argument(help="Skill slug to uninstall"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Preview without uninstalling"),
) -> None:
    """Uninstall a locally installed skill."""
    import shutil
    skill_dir = SKILL_DIR / slug
    if not skill_dir.exists():
        print_error(f"Skill '{slug}' is not installed.")
        raise typer.Exit(code=1)

    if dry_run:
        console.print(f"[bold]Dry run:[/bold] Would remove {skill_dir}")
        raise typer.Exit()

    shutil.rmtree(skill_dir)
    console.print(f"[green]Uninstalled[/green] skill '{slug}'.")


@app.command(name="list")
def list_installed() -> None:
    """List locally installed skills."""
    if not SKILL_DIR.exists():
        console.print("No skills installed yet.", style="dim")
        return

    installed = [d.name for d in SKILL_DIR.iterdir() if d.is_dir()]
    if not installed:
        console.print("No skills installed yet.", style="dim")
        return

    console.print("[bold]Installed skills:[/bold]")
    for name in sorted(installed):
        console.print(f"  • {name}")


@app.command()
def search(
    query: str = typer.Argument(help="Search query"),
    api_url: str = typer.Option("http://localhost:8000/api/v1", "--api-url", envvar="SKILLHUB_API_URL"),
) -> None:
    """Search for skills on SkillHub."""
    api = SkillHubAPI(base_url=api_url)
    try:
        result = api.search_skills(query)
        skills = result.get("data", [])
        if not skills:
            console.print(f"No skills found for '{query}'.")
            return
        print_skills_table(skills)
        total = result.get("meta", {}).get("total", len(skills))
        console.print(f"\nShowing {len(skills)} of {total} results.", style="dim")
    except Exception as e:
        print_error(str(e))
        raise typer.Exit(code=1)
    finally:
        api.close()


@app.command()
def audit(
    slug: str = typer.Argument(help="Skill slug to audit"),
    api_url: str = typer.Option("http://localhost:8000/api/v1", "--api-url", envvar="SKILLHUB_API_URL"),
) -> None:
    """Show full security audit report for a skill."""
    api = SkillHubAPI(base_url=api_url)
    try:
        skill = api.get_skill(slug)
        print_skill_card(skill)
        print_security_summary(skill)
    except Exception as e:
        print_error(str(e))
        raise typer.Exit(code=1)
    finally:
        api.close()


if __name__ == "__main__":
    app()
