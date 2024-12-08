#!/usr/bin/env python3
from classes.comdirect_api import ComdirectAPI
from classes.deutschebank_api import DeutscheBankAPI
from utils.output import print_to_stdout, save_to_csv, save_to_pdf, display_data
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, IntPrompt
from rich.table import Table
import json

console = Console()


def display_menu(title, options):
    """Display a menu with rich formatting"""
    console.print(Panel(f"[bold blue]{title}[/bold blue]"))
    table = Table(show_header=False, box=None)
    for idx, option in enumerate(options, 1):
        table.add_row(f"[green]{idx}[/green]", option)
    console.print(table)


def choose_account(accounts):
    """Choose an account from the list of accounts"""
    if isinstance(accounts, dict) and 'values' in accounts:
        try:
            accounts_list = json.loads(accounts['values']) if isinstance(
                accounts['values'], str) else accounts['values']

            console.print("\n[bold]Available accounts:[/bold]")
            table = Table(show_header=True)
            table.add_column("Number", style="green")
            table.add_column("Account Type", style="blue")
            table.add_column("IBAN", style="yellow")

            for i, account in enumerate(accounts_list, 1):
                table.add_row(
                    str(i),
                    account['accountType']['text'],
                    account['iban']
                )

            console.print(table)

            while True:
                choice = IntPrompt.ask(
                    "\nEnter the number of the account", show_choices=False)
                index = choice - 1
                if 0 <= index < len(accounts_list):
                    return accounts_list[index]['accountId']
                console.print("[red]Invalid choice. Please try again.[/red]")
        except Exception as e:
            console.print(f"[red]Error processing accounts: {e}[/red]")
            return None
    return None


def choose_output_format(data, bank_type):
    """Choose an output format for the data"""
    output_options = ["Print to stdout", "Save as CSV",
                      "Save as PDF", "Display as Table"]
    display_menu("Choose an output format", output_options)

    output_choice = Prompt.ask(
        "Enter your choice", choices=["1", "2", "3", "4"])

    if output_choice == '1':
        print_to_stdout(data)
    elif output_choice == '2':
        filename = Prompt.ask("Enter CSV file name")
        if not filename.endswith('.csv'):
            filename += '.csv'
        save_to_csv(data, filename, bank_type)
    elif output_choice == '3':
        filename = Prompt.ask("Enter PDF file name")
        if not filename.endswith('.pdf'):
            filename += '.pdf'
        save_to_pdf(data, filename)
    elif output_choice == '4':
        display_data(data, bank_type)


def main():
    try:
        while True:
            bank_options = ["Comdirect", "Deutsche Bank", "Exit"]
            display_menu("Choose a bank", bank_options)

            bank_choice = Prompt.ask(
                "Enter your choice", choices=["1", "2", "3"])

            bank_type = None
            if bank_choice == '1':
                bank = ComdirectAPI()
                bank_type = 'COMDIRECT'
            elif bank_choice == '2':
                bank = DeutscheBankAPI()
                bank_type = 'DEUTSCHEBANK'
            elif bank_choice == '3':
                console.print("[yellow]Exiting...[/yellow]")
                break

            while True:
                action_options = [
                    "Get Accounts",
                    "Get Transactions",
                    "Get All Balances",
                    "Get Account Balance",
                    "Back to Bank Selection"
                ]
                display_menu("Choose an action", action_options)

                action_choice = Prompt.ask("Enter your choice", choices=[
                    "1", "2", "3", "4", "5"])

                if action_choice in ['1', '2', '3', '4']:
                    with console.status("[bold green]Authenticating...") as status:
                        bank.authenticate()
                        status.update(
                            "[bold green]Waiting for TAN confirmation...")
                        status.stop()

                        if action_choice == '1':
                            accounts = bank.get_accounts()
                            status.update(
                                "[bold green]Accounts retrieved successfully!")
                            status.stop()
                            choose_output_format(accounts, bank_type)

                        elif action_choice == '2':
                            accounts = bank.get_accounts()
                            status.update(
                                "[bold green]Accounts retrieved successfully!")
                            status.stop()

                            account_id = choose_account(accounts)
                            if account_id:
                                from_date = Prompt.ask(
                                    "Enter from date (YYYY-MM-DD) or press Enter for all transactions"
                                ).strip()
                                from_date = from_date if from_date else None

                                status.update(
                                    "[bold green]Retrieving transactions...")
                                status.stop()

                                transactions = bank.get_transactions(
                                    account_id, from_date)
                                status.update(
                                    "[bold green]Transactions retrieved successfully!")
                                status.stop()

                                choose_output_format(transactions, bank_type)
                            else:
                                console.print(
                                    "[red]No valid account selected.[/red]")

                        elif action_choice == '3':
                            balances = bank.get_all_balances()
                            status.update(
                                "[bold green]Balances retrieved successfully!")
                            status.stop()

                            choose_output_format(balances, bank_type)

                        elif action_choice == '4':
                            accounts = bank.get_accounts()
                            status.update(
                                "[bold green]Accounts retrieved successfully!")
                            status.stop()

                            account_id = choose_account(accounts)
                            if account_id:
                                status.update(
                                    "[bold green]Retrieving balance...")
                                balance = bank.get_account_balance(account_id)
                                status.update(
                                    "[bold green]Balance retrieved successfully!")
                                status.stop()

                                choose_output_format(balance, bank_type)
                            else:
                                console.print(
                                    "[red]No valid account selected.[/red]")

                elif action_choice == '5':
                    break

    except KeyboardInterrupt:
        console.print("\n[yellow]Program terminated by user.[/yellow]")
        exit(0)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        console.print("\n[yellow]Program terminated by user.[/yellow]")
        exit(0)
