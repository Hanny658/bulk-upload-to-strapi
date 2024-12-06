import tkinter as tk
from tkinter import filedialog, messagebox
import pandas as pd
import requests
import json
from datetime import datetime


def convert_to_serializable(value):
    """
    Convert non-serializable objects like datetime to a JSON-serializable format.
    """
    if isinstance(value, (datetime, pd.Timestamp)):
        return value.isoformat()  # Convert to ISO 8601 string format
    return value


def upload_to_strapi(file_path, endpoint, api_key):
    try:
        # Read the Excel file
        df = pd.read_excel(file_path)
        # Get column names
        columns = df.columns.tolist()

        for index, row in df.iterrows():
            # Skip rows where the first column is empty
            if pd.isna(row[columns[0]]):
                continue

            # Create JSON data and request payload
            json_data = {
                col: str(convert_to_serializable(row[col])) if not pd.isna(row[col]) else None
                for col in columns
            }

            payload = {"data": json_data}

            # Upload data to Strapi
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            }
            response = requests.post(endpoint, headers=headers, data=json.dumps(payload))

            if response.status_code not in [200, 201]:      # 200 for Strapi 4.x, 201 for strapi 5.x
                print(f"Failed to upload row {index + 1}: {response.status_code} - {response.text}")
            else:
                print(f"Successfully uploaded row {index + 1}")

        messagebox.showinfo("Success", "Data uploaded successfully!")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {str(e)}")


def browse_file():
    file_path = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx *.xls")])
    if file_path:
        file_entry.delete(0, tk.END)
        file_entry.insert(0, file_path)


def start_upload():
    file_path = file_entry.get()
    endpoint = endpoint_entry.get()
    api_key = api_key_entry.get()

    if not file_path or not endpoint or not api_key:
        messagebox.showwarning("Missing Information", "Please provide all the required information.")
        return

    upload_to_strapi(file_path, endpoint, api_key)


# Create the GUI
root = tk.Tk()
root.title("Strapi Excel Bulk Uploader (Free of plugins!)")

tk.Label(root, text="Excel File:").grid(row=0, column=0, padx=10, pady=5, sticky="e")
file_entry = tk.Entry(root, width=40)
file_entry.grid(row=0, column=1, padx=10, pady=5)
browse_button = tk.Button(root, text="Browse", command=browse_file)
browse_button.grid(row=0, column=2, padx=10, pady=5)

tk.Label(root, text="Strapi Endpoint:").grid(row=1, column=0, padx=10, pady=5, sticky="e")
endpoint_entry = tk.Entry(root, width=50)
endpoint_entry.grid(row=1, column=1, columnspan=2, padx=10, pady=5)

tk.Label(root, text="API Key:").grid(row=2, column=0, padx=10, pady=5, sticky="e")
api_key_entry = tk.Entry(root, width=50, show="*")
api_key_entry.grid(row=2, column=1, columnspan=2, padx=10, pady=5)

upload_button = tk.Button(root, text="Upload", command=start_upload)
upload_button.grid(row=3, column=1, pady=10)

root.mainloop()
