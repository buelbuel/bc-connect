#!/usr/bin/env python3
import csv
import json
import os
from fpdf import FPDF


def print_to_stdout(data):
    """Print data to stdout using rich formatting"""
    from rich.json import JSON
    from rich.console import Console

    console = Console()
    console.print(JSON.from_data(data))


def save_to_csv(data, filename, bank_type=None):
    """Save data to CSV"""
    if not data:
        print("No data to save.")
        return

    filename = os.path.join('downloads', filename)

    try:
        if bank_type == 'COMDIRECT':
            if isinstance(data, dict) and 'values' in data:
                items = data['values']
            else:
                items = [data]

            flattened_data = []
            all_fields = set()

            for item in items:
                flat_item = {}
                for key, value in item.items():
                    if key == 'amount':
                        flat_item['amount_value'] = value.get('value')
                        flat_item['amount_unit'] = value.get('unit')
                        all_fields.add('amount_value')
                        all_fields.add('amount_unit')
                    elif key == 'transactionType':
                        flat_item['transactionType_key'] = value.get('key')
                        flat_item['transactionType_text'] = value.get('text')
                        all_fields.add('transactionType_key')
                        all_fields.add('transactionType_text')
                    elif isinstance(value, dict):
                        for nested_key, nested_value in value.items():
                            field_name = f"{key}_{nested_key}"
                            flat_item[field_name] = nested_value
                            all_fields.add(field_name)
                    else:
                        flat_item[key] = value
                        all_fields.add(key)
                flattened_data.append(flat_item)

            for item in flattened_data:
                for field in all_fields:
                    if field not in item:
                        item[field] = None
        else:
            flattened_data = data if isinstance(data, list) else [data]
            all_fields = set(
                flattened_data[0].keys()) if flattened_data else set()

        if flattened_data:
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=sorted(all_fields))
                writer.writeheader()
                for item in flattened_data:
                    writer.writerow(item)
            print(f"[green]Data saved to {filename}[/green]")
        else:
            print("[yellow]No data to write to CSV[/yellow]")

    except Exception as e:
        print(f"[red]Error saving to CSV: {e}[/red]")


def save_to_text(data, filename):
    filename = os.path.join('downloads', filename)

    with open(filename, 'w') as file:
        file.write(json.dumps(data, indent=2))


def save_to_pdf(data, filename):
    filename = os.path.join('downloads', filename)

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    for item in data:
        if isinstance(item, dict):
            for key, value in item.items():
                pdf.cell(200, 10, txt=f"{key}: {value}", ln=True)
            pdf.cell(200, 10, txt=" ", ln=True)
        else:
            pdf.cell(200, 10, txt=str(item), ln=True)
            pdf.cell(200, 10, txt=" ", ln=True)

    pdf.output(filename)


def display_data(data, bank_type=None):
    """Display data in a rich table format"""
    from rich.table import Table
    from rich.console import Console

    console = Console()

    if not data:
        console.print("[red]No data to display.[/red]")
        return

    try:
        # Process data similar to CSV logic
        if bank_type == 'COMDIRECT':
            if isinstance(data, dict) and 'values' in data:
                items = data['values']
            else:
                items = [data]
        else:
            items = data if isinstance(data, list) else [data]

        if not items:
            console.print("[yellow]No items to display[/yellow]")
            return

        # Create table
        table = Table(show_header=True, header_style="bold blue")

        # Flatten the first item to get all possible fields
        sample_item = items[0]
        all_fields = set()

        def flatten_dict(d, prefix=''):
            for key, value in d.items():
                if isinstance(value, dict):
                    if 'value' in value and 'unit' in value:
                        # Special handling for amount-like objects
                        field_name = f"{prefix}{key}" if prefix else key
                        all_fields.add(field_name)
                    else:
                        flatten_dict(value, f"{prefix}{
                                     key}_" if prefix else f"{key}_")
                else:
                    field_name = f"{prefix}{key}" if prefix else key
                    all_fields.add(field_name)

        if isinstance(sample_item, dict):
            flatten_dict(sample_item)

            # Add columns
            for field in sorted(all_fields):
                table.add_column(field)

            # Add rows
            for item in items:
                row_data = []
                for field in sorted(all_fields):
                    # Navigate nested structure
                    value = item
                    for part in field.split('_'):
                        if isinstance(value, dict):
                            if 'value' in value and 'unit' in value:
                                value = f"{value['value']} {value['unit']}"
                            else:
                                value = value.get(part, '')
                        else:
                            value = ''
                    row_data.append(str(value))
                table.add_row(*row_data)
        else:
            table.add_column("Value")
            for item in items:
                table.add_row(str(item))

        console.print(table)

    except Exception as e:
        console.print(f"[red]Error displaying data: {e}[/red]")
