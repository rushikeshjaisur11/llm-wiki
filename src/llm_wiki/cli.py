import os
import shutil
from pathlib import Path
import typer
from rich.console import Console
from rich.prompt import Prompt, Confirm

app = typer.Typer(help="LLM Wiki Command Line Interface")
console = Console()

def run_installation():
    """Run the interactive vault setup configuration."""
    console.print("\n[bold cyan]Welcome to the LLM-Wiki Configurator[/bold cyan]")
    
    current_dir = str(Path.cwd().resolve())
    vault_path_input = Prompt.ask(
        "What is the absolute path to your new vault?",
        default=current_dir
    )
    
    vault_path = Path(vault_path_input).resolve().as_posix()
    
    is_global = Confirm.ask("Install globally (recommended)? No = locally (vault-only)", default=True)
    
    vault_tool = Prompt.ask(
        "Which vault tool do you use?",
        choices=["obsidian", "foam", "logseq", "markdown"],
        default="markdown"
    )
    
    home = Path.home()
    if is_global:
        dest_base = home / ".claude" / "skills"
    else:
        dest_base = Path(vault_path) / ".claude" / "skills"
        
    dest_base.mkdir(parents=True, exist_ok=True)
    
    pkg_dir = Path(__file__).parent.resolve()
    repo_skills = pkg_dir / "skills"
    
    if not repo_skills.exists():
        console.print(f"[bold red]Error: Skills directory not found at {repo_skills}[/bold red]")
        raise typer.Exit(1)
        
    console.print(f"\nInstalling to [green]{dest_base}[/green]...")
    
    # 1. Copy core skills
    core_dir = repo_skills / "core"
    if core_dir.exists():
        for skill_dir in core_dir.iterdir():
            if skill_dir.is_dir():
                d = dest_base / skill_dir.name
                d.mkdir(parents=True, exist_ok=True)
                skill_source = skill_dir / "SKILL.md"
                if skill_source.exists():
                    shutil.copy2(skill_source, d / "SKILL.md")
                
    # 3. Copy python search tools
    wiki_dest = dest_base / "_wiki"
    wiki_dest.mkdir(parents=True, exist_ok=True)
    wiki_src = repo_skills / "_wiki"
    if wiki_src.exists():
        for py_file in wiki_src.glob("*.py"):
            shutil.copy2(py_file, wiki_dest)
        
    # 4. Write vault path config
    (wiki_dest / ".vault_path").write_text(vault_path, encoding="utf-8")
    
    # 5. Patch placeholders
    scripts_path = wiki_dest.as_posix()
    for md_file in dest_base.rglob("*.md"):
        content = md_file.read_text(encoding="utf-8")
        content = content.replace("{{VAULT}}", vault_path)
        content = content.replace("{{SCRIPTS}}", scripts_path)
        md_file.write_text(content, encoding="utf-8")
        
    # 6. Global Context
    if is_global:
        claude_md = home / ".claude" / "CLAUDE.md"
        claude_md.parent.mkdir(parents=True, exist_ok=True)
        append_txt = f"\n## My Personal Context\nAt the start of every session, read {vault_path}/CLAUDE.md for context about who I am, my work, and my conventions.\n"
        with open(claude_md, "a", encoding="utf-8") as f:
            f.write(append_txt)
            
    console.print(f"[bold green]Done. Skills installed to {dest_base}[/bold green]")
    console.print("\n[magenta]Next Step:[/magenta] Run Claude Code with [bold]/vault-setup[/bold] to build your folders.")


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
        # Default behavior when no flag is provided
        console.print("[yellow]Use 'llm-wiki --install' to install llm-wiki skills, or 'llm-wiki --help' for more info.[/yellow]")

if __name__ == "__main__":
    app()
