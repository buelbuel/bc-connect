#!/usr/bin/env python3

import click
import subprocess
import sys
from datetime import datetime
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt

console = Console()


def run_bankconnect():
    try:
        subprocess.run([sys.executable, "bankconnect/main.py"], check=True)
    except subprocess.CalledProcessError:
        console.print("[red]Error running bankconnect[/red]")
    except KeyboardInterrupt:
        console.print("\n[yellow]Bankconnect terminated by user.[/yellow]")


def run_fava(beancount_file):
    try:
        subprocess.run(["fava", beancount_file], check=True)
    except subprocess.CalledProcessError:
        console.print("[red]Error running fava. Is it installed?[/red]")
        console.print("[yellow]Try: pip install fava[/yellow]")
    except KeyboardInterrupt:
        console.print("\n[yellow]Fava server terminated by user.[/yellow]")


def check_beancount_file(file_path):
    """Validate beancount file syntax"""
    try:
        result = subprocess.run(
            ["bean-check", file_path],
            capture_output=True,
            text=True,
            check=True
        )
        console.print("[green]No errors found![/green]")
    except subprocess.CalledProcessError as e:
        console.print("[red]Errors found:[/red]")
        console.print(e.stderr)


def import_transactions():
    """Import transactions using bean-extract"""
    try:
        # First identify the files
        result = subprocess.run(
            ["bean-identify", "lib/import_config.py", "downloads"],
            capture_output=True,
            text=True
        )

        if not result.stdout.strip():
            console.print(
                "[yellow]No files to import in downloads directory[/yellow]")
            return

        # Extract the transactions
        result = subprocess.run(
            ["bean-extract", "lib/import_config.py", "downloads"],
            capture_output=True,
            text=True
        )

        if result.stdout.strip():
            filename = f"ledgers/imported_{
                datetime.now().strftime('%Y%m%d')}.beancount"
            with open(filename, 'w') as f:
                f.write(result.stdout)
            console.print(f"[green]Transactions imported to {
                          filename}[/green]")
    except subprocess.CalledProcessError as e:
        console.print("[red]Error during import:[/red]")
        console.print(e.stderr)


@click.command()
@click.option('--fava', is_flag=True, help='Run Fava web interface')
@click.option('--bank', is_flag=True, help='Run bank connection tool')
@click.option('--file', default='ledgers/main.beancount', help='Beancount file for Fava')
@click.option('--check', is_flag=True, help='Check beancount file syntax')
@click.option('--import', 'import_', is_flag=True, help='Import new transactions')
def main(fava, bank, file, check, import_):
    """Beancount Tools CLI"""
    if not any([fava, bank, check, import_]):
        options = [
            "Run Bank Connection Tool",
            "Run Fava",
            "Check Beancount File",
            "Import Transactions",
            "Exit"
        ]
        while True:
            console.print(Panel("[bold blue]Choose an option[/bold blue]"))
            for idx, option in enumerate(options, 1):
                console.print(f"[green]{idx}[/green] {option}")

            choice = Prompt.ask("Enter your choice", choices=[
                                str(i) for i in range(1, len(options) + 1)])

            if choice == "1":
                run_bankconnect()
            elif choice == "2":
                run_fava(file)
            elif choice == "3":
                check_beancount_file(file)
            elif choice == "4":
                import_transactions()
            else:
                break
    else:
        if bank:
            run_bankconnect()
        if fava:
            run_fava(file)
        if check:
            check_beancount_file(file)
        if import_:
            import_transactions()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        console.print("\n[yellow]Program terminated by user.[/yellow]")
        exit(0)
