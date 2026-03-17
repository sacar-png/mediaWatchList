import typer
from rich.console import Console
from rich.table import Table
import json
from datetime import datetime
from typing import Optional
from collections import Counter

app = typer.Typer(help="🎥 Simplest Media Watchlist CLI")
console = Console()
DATA_FILE = "watchlist.json"

def load_data():
    try:
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

def get_next_id(data):
    return max((item["id"] for item in data), default=0) + 1

status_colors = {
    "planned": "yellow",
    "watching": "cyan",
    "completed": "green",
    "dropped": "red",
    "on_hold": "magenta"
}

@app.command()
def add(
    title: str = typer.Argument(..., help="Title of the movie/series/book etc."),
    media_type: str = typer.Option("movie", "--type", help="movie, series, book, game, anime, podcast"),
    status: str = typer.Option("planned", "--status", help="planned, watching, completed, dropped, on_hold")
):
    """Add a new item to your watchlist."""
    data = load_data()
    entry = {
        "id": get_next_id(data),
        "title": title,
        "media_type": media_type,
        "status": status,
        "rating": None,
        "progress": None,
        "added_date": datetime.now().isoformat()
    }
    data.append(entry)
    save_data(data)
    console.print(f"[bold green]✅ Added:[/] {title} ({media_type}) — Status: {status}")

@app.command()
def list(
    status: Optional[str] = typer.Option(None, "--status"),
    media_type: Optional[str] = typer.Option(None, "--type")
):
    """Show all (or filtered) items in a beautiful table."""
    data = load_data()
    filtered = [
        item for item in data
        if (not status or item["status"] == status) and
           (not media_type or item["media_type"] == media_type)
    ]
    if not filtered:
        console.print("[yellow]No items found.[/]")
        return

    table = Table(title="🎥 Your Media Watchlist", show_lines=True)
    table.add_column("ID", justify="right", style="cyan")
    table.add_column("Title")
    table.add_column("Type")
    table.add_column("Status")
    table.add_column("Rating")
    table.add_column("Progress")

    for item in filtered:
        color = status_colors.get(item["status"], "white")
        rating = f"{item['rating']}/10" if item["rating"] else "-"
        progress = item["progress"] or "-"
        table.add_row(
            str(item["id"]),
            item["title"],
            item["media_type"],
            f"[{color}]{item['status']}[/{color}]",
            rating,
            progress
        )
    console.print(table)

@app.command()
def update(
    item_id: int = typer.Argument(..., help="ID from the list command"),
    status: Optional[str] = typer.Option(None, "--status"),
    rating: Optional[float] = typer.Option(None, "--rating", help="1.0 to 10.0"),
    progress: Optional[str] = typer.Option(None, "--progress", help="e.g. S02E05 or 45%")
):
    """Update status, rating, or progress of an item."""
    data = load_data()
    for item in data:
        if item["id"] == item_id:
            if status:
                item["status"] = status
            if rating is not None:
                item["rating"] = round(rating, 1)
            if progress is not None:
                item["progress"] = progress
            item["updated_date"] = datetime.now().isoformat()
            save_data(data)
            console.print(f"[bold blue]✅ Updated item #{item_id}[/]")
            return
    console.print(f"[red]❌ Item #{item_id} not found.[/]")

@app.command()
def delete(
    item_id: int = typer.Argument(..., help="ID from the list command")
):
    """Delete an item by ID."""
    data = load_data()
    new_data = [item for item in data if item["id"] != item_id]
    if len(new_data) == len(data):
        console.print(f"[red]❌ Item #{item_id} not found.[/]")
        return
    save_data(new_data)
    console.print(f"[bold red]🗑️  Deleted item #{item_id}[/]")

@app.command()
def stats():
    """Show quick statistics."""
    data = load_data()
    if not data:
        console.print("[yellow]No items yet. Add some![/]")
        return
    status_count = Counter(item["status"] for item in data)
    table = Table(title="📊 Watchlist Stats")
    table.add_column("Status")
    table.add_column("Count", justify="right")
    for st, count in status_count.items():
        color = status_colors.get(st, "white")
        table.add_row(f"[{color}]{st}[/{color}]", str(count))
    console.print(table)
    console.print(f"[bold]Total items:[/] {len(data)}")

if __name__ == "__main__":
    app()