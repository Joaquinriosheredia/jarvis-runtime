import logging

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich import box

from jarvis.config import OLLAMA_MODEL, OPENAI_MODEL
from jarvis.router import route
from jarvis.memory import save_memory, get_recent_memories
from jarvis.cost import get_usage_summary

logging.basicConfig(level=logging.WARNING)

app = typer.Typer(
    name="jarvis",
    help="Jarvis Runtime — local-first AI assistant",
    add_completion=False,
)
console = Console()


def _source_badge(source: str) -> Text:
    if source == "local":
        return Text(f"⚡ LOCAL · {OLLAMA_MODEL}", style="bold green")
    return Text(f"☁  CLOUD · {OPENAI_MODEL}", style="bold yellow")


@app.command()
def ask(prompt: str = typer.Argument(..., help="Pregunta o tarea para Jarvis")):
    """Envía un prompt a Jarvis y recibe una respuesta."""
    try:
        with console.status("[bold cyan]Thinking...[/bold cyan]", spinner="dots"):
            result = route(prompt)
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        raise typer.Exit(code=1)

    console.print(_source_badge(result.source))
    console.print(
        Panel(
            result.response,
            title="[bold white]Response[/bold white]",
            border_style="cyan",
            box=box.ROUNDED,
            padding=(1, 2),
        )
    )

    cost_color = "green" if result.estimated_cost == 0 else "yellow"
    console.print("[dim]─────────────────────────────────[/dim]")
    console.print(f"[dim]Latency:[/dim]  [white]{result.latency}s[/white]")
    console.print(f"[dim]Tokens: [/dim]  [white]~{result.tokens_approx}[/white]")
    console.print(f"[dim]Cost:   [/dim]  [{cost_color}]${result.estimated_cost:.5f}[/{cost_color}]")
    console.print(f"[dim]Reason: [/dim]  [italic dim]{result.reason}[/italic dim]")

    save_memory(
        prompt=prompt,
        response=result.response,
        source=result.source,
        latency=result.latency,
        cost=result.estimated_cost,
    )


@app.command()
def history(limit: int = typer.Option(10, help="Número de entradas a mostrar")):
    """Muestra las últimas interacciones guardadas."""
    memories = get_recent_memories(limit)
    if not memories:
        console.print("[dim]Sin historial todavía.[/dim]")
        return

    for m in memories:
        source_style = "green" if m["source"] == "local" else "yellow"
        console.print(f"[dim]{m['timestamp']}[/dim]  [{source_style}]{m['source']}[/{source_style}]")
        console.print(f"  [bold]Q:[/bold] {m['prompt'][:120]}")
        console.print(f"  [dim]A:[/dim] {m['response'][:120]}…")
        console.print()


@app.command()
def usage():
    """Muestra el resumen de uso y costes acumulados."""
    summary = get_usage_summary()

    table = Table(title="Jarvis — Resumen de uso", box=box.SIMPLE_HEAVY, show_header=True)
    table.add_column("Fuente", style="bold")
    table.add_column("Tokens", justify="right")
    table.add_column("Coste (USD)", justify="right")

    for source, data in summary["by_source"].items():
        color = "green" if source == "local" else "yellow"
        table.add_row(
            f"[{color}]{source}[/{color}]",
            str(data["tokens"]),
            f"${data['cost_usd']:.5f}",
        )

    console.print(table)
    console.print(f"\n[dim]Total requests:[/dim] {summary['total_requests']}")
    console.print(f"[dim]Total tokens:  [/dim] {summary['total_tokens']}")
    console.print(f"[dim]Total cost:    [/dim] [yellow]${summary['total_cost_usd']:.5f}[/yellow]")


if __name__ == "__main__":
    app()
