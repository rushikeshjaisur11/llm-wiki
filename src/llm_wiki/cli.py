import shutil
from pathlib import Path
import typer
from rich.console import Console
from rich.prompt import Prompt, Confirm

app = typer.Typer(help="LLM Wiki Command Line Interface")
console = Console()


def strip_frontmatter(content: str) -> tuple[dict, str]:
    """Parse YAML frontmatter block; return (meta_dict, body)."""
    if not content.startswith("---"):
        return {}, content
    end = content.find("\n---", 3)
    if end == -1:
        return {}, content
    fm_block = content[3:end].strip()
    body = content[end + 4:].lstrip("\n")
    meta: dict = {}
    for line in fm_block.splitlines():
        if ":" in line:
            k, _, v = line.partition(":")
            meta[k.strip()] = v.strip()
    return meta, body


def collect_skills(repo_skills: Path, vault_tool: str, agent: str) -> list[dict]:
    """Return list of {name, description, body} for all applicable skills."""
    skills = []

    def _add_dir(skill_dir: Path) -> None:
        if not skill_dir.is_dir():
            return
        name = skill_dir.name
        if name == "vault-setup" and agent != "claude":
            return
        skill_file = skill_dir / "SKILL.md"
        if not skill_file.exists():
            return
        raw = skill_file.read_text(encoding="utf-8")
        meta, body = strip_frontmatter(raw)
        skills.append({
            "name": name,
            "description": meta.get("description", ""),
            "body": body,
        })

    core_dir = repo_skills / "core"
    if core_dir.exists():
        for d in sorted(core_dir.iterdir()):
            _add_dir(d)

    if vault_tool == "obsidian":
        obsidian_dir = repo_skills / "extras" / "obsidian"
        if obsidian_dir.exists():
            for d in sorted(obsidian_dir.iterdir()):
                _add_dir(d)

    return skills


def install_per_file(skills: list[dict], dest_base: Path, agent: str) -> None:
    """Write one file per skill with agent-appropriate frontmatter."""
    for skill in skills:
        name = skill["name"]
        desc = skill["description"]
        body = skill["body"]

        if agent == "claude":
            d = dest_base / name
            d.mkdir(parents=True, exist_ok=True)
            fm = f"---\nname: {name}\ndescription: {desc}\n---\n\n"
            (d / "SKILL.md").write_text(fm + body, encoding="utf-8")
        elif agent == "cursor":
            dest_base.mkdir(parents=True, exist_ok=True)
            fm = f"---\ndescription: {desc}\n---\n\n"
            (dest_base / f"{name}.mdc").write_text(fm + body, encoding="utf-8")
        elif agent == "windsurf":
            dest_base.mkdir(parents=True, exist_ok=True)
            fm = f"---\ndescription: {desc}\ntrigger: agent_requested\n---\n\n"
            (dest_base / f"{name}.md").write_text(fm + body, encoding="utf-8")


def install_combined(skills: list[dict], dest_file: Path, agent: str) -> None:
    """Write all skills into a single combined file."""
    agent_intros = {
        "copilot": "These are custom slash-command skills for GitHub Copilot in this vault.",
        "codex": "These are custom slash-command skills for OpenAI Codex in this vault.",
        "gemini": "These are custom slash-command skills for Gemini CLI in this vault.",
    }
    lines = ["# LLM Wiki\n", f"{agent_intros.get(agent, '')}\n"]
    for skill in skills:
        lines.append(f"\n## /{skill['name']}\n")
        lines.append(skill["body"].strip() + "\n")
    dest_file.parent.mkdir(parents=True, exist_ok=True)
    dest_file.write_text("\n".join(lines), encoding="utf-8")


def patch_placeholders(base: Path, vault_path: str, scripts_path: str, exts: tuple = ("*.md", "*.mdc")) -> None:
    for ext in exts:
        for f in base.rglob(ext):
            content = f.read_text(encoding="utf-8")
            content = content.replace("{{VAULT}}", vault_path)
            content = content.replace("{{SCRIPTS}}", scripts_path)
            f.write_text(content, encoding="utf-8")


def run_installation():
    console.print("\n[bold cyan]Welcome to the LLM-Wiki Configurator[/bold cyan]")

    vault_path_input = Prompt.ask(
        "What is the absolute path to your new vault?",
        default=str(Path.cwd().resolve())
    )
    vault_path = Path(vault_path_input).resolve().as_posix()

    agent = Prompt.ask(
        "Which coding agent are you using?",
        choices=["claude", "cursor", "copilot", "codex", "windsurf", "gemini"],
        default="claude"
    )

    if agent not in ("copilot", "codex"):
        is_global = Confirm.ask("Install globally (recommended)? No = locally (vault-only)", default=True)
    else:
        is_global = False

    vault_tool = Prompt.ask(
        "Which vault tool do you use?",
        choices=["obsidian", "foam", "logseq", "markdown"],
        default="markdown"
    )

    home = Path.home()
    vault_dir = Path(vault_path)

    # Resolve destinations
    if agent == "claude":
        dest_base = (home / ".claude" / "skills") if is_global else (vault_dir / ".claude" / "skills")
        scripts_base = dest_base
    elif agent == "cursor":
        dest_base = (home / ".cursor" / "rules") if is_global else (vault_dir / ".cursor" / "rules")
        scripts_base = dest_base
    elif agent == "windsurf":
        dest_base = (home / ".windsurf" / "rules") if is_global else (vault_dir / ".windsurf" / "rules")
        scripts_base = dest_base
    elif agent == "copilot":
        dest_base = vault_dir / ".github"
        scripts_base = vault_dir
    elif agent == "codex":
        dest_base = vault_dir
        scripts_base = vault_dir
    elif agent == "gemini":
        dest_base = (home / ".gemini") if is_global else vault_dir
        scripts_base = dest_base

    pkg_dir = Path(__file__).parent.resolve()
    repo_skills = pkg_dir / "skills"

    if not repo_skills.exists():
        console.print(f"[bold red]Error: Skills directory not found at {repo_skills}[/bold red]")
        raise typer.Exit(1)

    console.print(f"\nInstalling to [green]{dest_base}[/green]...")

    skills = collect_skills(repo_skills, vault_tool, agent)

    # Install skills
    if agent in ("claude", "cursor", "windsurf"):
        install_per_file(skills, dest_base, agent)
    elif agent == "copilot":
        install_combined(skills, dest_base / "copilot-instructions.md", agent)
    elif agent == "codex":
        install_combined(skills, dest_base / "AGENTS.md", agent)
    elif agent == "gemini":
        install_combined(skills, dest_base / "GEMINI.md", agent)

    # Copy python search tools
    wiki_dest = scripts_base / "_wiki"
    wiki_dest.mkdir(parents=True, exist_ok=True)
    wiki_src = repo_skills / "_wiki"
    if wiki_src.exists():
        for py_file in wiki_src.glob("*.py"):
            shutil.copy2(py_file, wiki_dest)

    (wiki_dest / ".vault_path").write_text(vault_path, encoding="utf-8")

    # Patch placeholders
    scripts_path = wiki_dest.as_posix()
    patch_placeholders(dest_base, vault_path, scripts_path)

    # Global context injection
    if is_global:
        if agent == "claude":
            claude_md = home / ".claude" / "CLAUDE.md"
            claude_md.parent.mkdir(parents=True, exist_ok=True)
            append_txt = f"\n## My Personal Context\nAt the start of every session, read {vault_path}/CLAUDE.md for context about who I am, my work, and my conventions.\n"
            with open(claude_md, "a", encoding="utf-8") as f:
                f.write(append_txt)
        elif agent == "cursor":
            ctx_file = home / ".cursor" / "rules" / "llm-wiki-context.mdc"
            ctx_file.parent.mkdir(parents=True, exist_ok=True)
            ctx_file.write_text(
                f"---\ndescription: LLM Wiki vault context\n---\n\nVault root: `{vault_path}`\nScripts: `{scripts_path}`\n",
                encoding="utf-8"
            )
        elif agent == "windsurf":
            ctx_file = home / ".windsurf" / "rules" / "llm-wiki-context.md"
            ctx_file.parent.mkdir(parents=True, exist_ok=True)
            ctx_file.write_text(
                f"---\ndescription: LLM Wiki vault context\ntrigger: agent_requested\n---\n\nVault root: `{vault_path}`\nScripts: `{scripts_path}`\n",
                encoding="utf-8"
            )

    console.print(f"[bold green]Done. Skills installed to {dest_base}[/bold green]")

    next_steps = {
        "claude":    "Run [bold]/vault-setup[/bold] in Claude Code to build your folders.",
        "cursor":    "Open Cursor and type [bold]@ingest[/bold] to add sources.",
        "windsurf":  "Skills installed — use [bold]@ingest[/bold] in Windsurf.",
        "copilot":   "Skills loaded into [bold].github/copilot-instructions.md[/bold] — ask Copilot to ingest or query.",
        "codex":     "Skills loaded into [bold]AGENTS.md[/bold] — run Codex in this vault.",
        "gemini":    "Skills loaded — ask Gemini to ingest or query.",
    }
    console.print(f"\n[magenta]Next Step:[/magenta] {next_steps[agent]}")


@app.callback(invoke_without_command=True)
def main(
    install: bool = typer.Option(False, "--install", help="Run the installation wizard to wire up skills")
):
    """
    LLM Wiki Command Line Interface.
    \nRun 'llm-wiki --install' to setup the skills on your machine.
    """
    if install:
        run_installation()
    else:
        console.print("[yellow]Use 'llm-wiki --install' to install llm-wiki skills, or 'llm-wiki --help' for more info.[/yellow]")


if __name__ == "__main__":
    app()
