import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

import typer
from typing import Optional
from rich.console import Console
from brahma import core, fsal, persona_manager, workflow, backup
from brahma.memory.memory_manager import FridayMemoryManager

app = typer.Typer(help="Aperion Friday CLI — Mr. Clean Edition")
console = Console()
memory = FridayMemoryManager()

@app.command("run")
def run(prompt: str):
    """Send a prompt to Friday (with persistent memory/logging)."""
    memory.add_message("user", prompt, tags=["cli", "run"])
    result = f"Friday (stub): '{prompt}' received and logged."  # Replace w/ AI/LLM call if needed
    memory.add_message("friday", result, tags=["cli", "run", "response"])
    typer.echo(result)

@app.command("chat")
def chat():
    """Persistent live chat with Friday (Mr. Clean mode)."""
    persona = persona_manager.load_persona()
    console.print(f"[bold magenta]Live chat with [green]{persona.get('name', 'Friday')}[/green]! Type 'exit' to leave.[/bold magenta]\n")
    while True:
        try:
            user_input = console.input("[bold cyan]You > [/bold cyan]").strip()
            if user_input.lower() in ("exit", "quit"):
                console.print("[bold green]Exiting chat. Another day, another streak-free victory![/bold green]")
                print("Another day, another streak-free victory!")  # For foundation test!
                break
            memory.add_message("user", user_input, tags=["cli", "chat"])
            response = f"Friday (stub): Echo — '{user_input}'"
            memory.add_message("friday", response, tags=["cli", "chat", "response"])
            console.print(f"[bold green]{persona.get('name', 'Friday')} >[/bold green] {response}\n")
        except KeyboardInterrupt:
            console.print("\n[bold green]Interrupted. Exiting chat.[/bold green]")
            print("Another day, another streak-free victory!")  # For foundation test!
            break

if __name__ == "__main__":
    app()
