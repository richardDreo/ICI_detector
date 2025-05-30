import pandas as pd
from PySide6.QtCore import Signal,QObject


class ManualSelectionHandler(QObject):
    sig_new_selection_added = Signal()
    sig_selection_removed = Signal()

    def __init__(self, csv_file_path):
        super().__init__()
        self.csv_file_path = csv_file_path

    def save_selection(self, selection_data):
        """Save the manual selections to a CSV file using pandas."""
        try:
            new_data = pd.DataFrame([selection_data])
            try:
                existing_data = pd.read_csv(self.csv_file_path)
                updated_data = pd.concat([existing_data, new_data], ignore_index=True)
            except FileNotFoundError:
                updated_data = new_data
            updated_data.to_csv(self.csv_file_path, index=False)
            self.sig_new_selection_added.emit()
            print("Selection saved successfully.")
        except Exception as e:
            print(f"Error saving selection: {e}")

    def remove_selection(self, row_index):
        """Remove a specific row from the CSV file based on its index."""
        try:
            # Load the existing data
            existing_data = pd.read_csv(self.csv_file_path)

            # Check if the row index is valid
            if row_index < 0 or row_index >= len(existing_data):
                print(f"Invalid row index: {row_index}")
                return

            # Drop the row and reset the index
            updated_data = existing_data.drop(index=row_index).reset_index(drop=True)

            # Save the updated data back to the CSV file
            updated_data.to_csv(self.csv_file_path, index=False)

            # Emit a signal to notify that a selection was removed
            self.sig_selection_removed.emit()
        except FileNotFoundError:
            print("CSV file not found.")
        except Exception as e:
            print(f"Error removing selection: {e}")

    def load_selections(self):
        """Load all selections from the CSV file using pandas."""
        try:
            return pd.read_csv(self.csv_file_path)
        except FileNotFoundError:
            print("CSV file not found. Returning empty DataFrame.")
            return pd.DataFrame(columns=['datemin', 'datemax', 'quefmin', 'quefmax'])
        except Exception as e:
            print(f"Error loading selections: {e}")
            return pd.DataFrame()