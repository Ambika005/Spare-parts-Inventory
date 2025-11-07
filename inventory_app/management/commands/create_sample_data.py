from django.core.management.base import BaseCommand
from inventory_app.models import SparePart
import pandas as pd
import os


class Command(BaseCommand):
    help = 'Import spare parts data from Excel file'

    def add_arguments(self, parser):
        parser.add_argument(
            '--file',
            type=str,
            default='SpareParts_Inventory_500.xlsx',
            help='Excel file to import (default: SpareParts_Inventory_500.xlsx)'
        )

    def handle(self, *args, **options):
        file_path = options['file']
        
        # Check if file exists in current directory
        if not os.path.exists(file_path):
            # Try relative to Django project root
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
            file_path = os.path.join(base_dir, options['file'])
            
        if not os.path.exists(file_path):
            self.stdout.write(
                self.style.ERROR(f'Excel file not found: {options["file"]}')
            )
            return

        try:
            # Read Excel file
            df = pd.read_excel(file_path)
            
            self.stdout.write(f'Reading from: {file_path}')
            self.stdout.write(f'Found {len(df)} rows in Excel file')
            self.stdout.write(f'Columns: {list(df.columns)}')
            
            # Try to map columns (flexible mapping for different column names)
            column_mapping = {}
            for col in df.columns:
                col_lower = col.lower()
                if 'part' in col_lower and 'name' in col_lower:
                    column_mapping['part_name'] = col
                elif 'quantity' in col_lower or 'qty' in col_lower or 'stock' in col_lower:
                    column_mapping['quantity'] = col
                elif 'threshold' in col_lower or 'min' in col_lower or 'limit' in col_lower:
                    column_mapping['threshold'] = col
                elif 'supplier' in col_lower or 'vendor' in col_lower:
                    column_mapping['supplier'] = col
            
            self.stdout.write(f'Column mapping: {column_mapping}')
            
            created_count = 0
            updated_count = 0
            
            for index, row in df.iterrows():
                try:
                    # Extract data based on column mapping
                    part_name = str(row[column_mapping.get('part_name', df.columns[0])]).strip()
                    
                    # Skip empty rows
                    if not part_name or part_name.lower() in ['nan', 'none', '']:
                        continue
                    
                    # Get quantity (default to 0 if not found or invalid)
                    try:
                        quantity = int(float(row[column_mapping.get('quantity', df.columns[1])]))
                    except (ValueError, TypeError):
                        quantity = 0
                    
                    # Get threshold (default to 5 if not found or invalid)
                    try:
                        threshold = int(float(row[column_mapping.get('threshold', df.columns[2])]))
                    except (ValueError, TypeError):
                        threshold = 5
                    
                    # Get supplier (default to empty string if not found)
                    supplier = ''
                    if 'supplier' in column_mapping:
                        try:
                            supplier = str(row[column_mapping['supplier']]).strip()
                            if supplier.lower() in ['nan', 'none']:
                                supplier = ''
                        except:
                            supplier = ''
                    
                    # Create or update the spare part
                    part, created = SparePart.objects.get_or_create(
                        part_name=part_name,
                        defaults={
                            'quantity': quantity,
                            'threshold': threshold,
                            'supplier': supplier
                        }
                    )
                    
                    if created:
                        created_count += 1
                        self.stdout.write(
                            self.style.SUCCESS(f'Created: {part.part_name} (Qty: {quantity}, Threshold: {threshold})')
                        )
                    else:
                        # Update existing part
                        part.quantity = quantity
                        part.threshold = threshold
                        if supplier:
                            part.supplier = supplier
                        part.save()
                        updated_count += 1
                        self.stdout.write(
                            self.style.WARNING(f'Updated: {part.part_name} (Qty: {quantity}, Threshold: {threshold})')
                        )
                        
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(f'Error processing row {index + 1}: {str(e)}')
                    )
                    continue
            
            self.stdout.write(
                self.style.SUCCESS(f'\nImport complete! Created: {created_count}, Updated: {updated_count} parts.')
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error reading Excel file: {str(e)}')
            )
            self.stdout.write(
                self.style.ERROR('Make sure pandas and openpyxl are installed: pip install pandas openpyxl')
            )