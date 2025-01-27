import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import filedialog, messagebox
import threading
import pandas as pd
import yfinance as yf
import time

class SymbolAggregationGUI:
    def __init__(self, root):
        root.title("Symbol Aggregation Tool")
        root.geometry("900x600")

        # Main frame
        main_frame = ttk.Frame(root, bootstyle="dark")
        main_frame.pack(expand=True, fill="both", padx=10, pady=10)

        # Sidebar with buttons
        sidebar = ttk.Frame(main_frame, width=200, bootstyle="dark")
        sidebar.pack(side="left", fill="y", padx=5, pady=5)

        button_style = {"bootstyle": "info outline", "padding": (15, 10), "width": 15}
        
        ttk.Button(sidebar, text="Scrape", **button_style, command=self.show_scrape).pack(pady=20)
        ttk.Button(sidebar, text="Upload", **button_style, command=self.show_upload).pack(pady=20)
        ttk.Button(sidebar, text="Look Up", **button_style, command=self.show_lookup).pack(pady=20)

        # Content area
        self.content_frame = ttk.Frame(main_frame, bootstyle="secondary")
        self.content_frame.pack(side="right", expand=True, fill="both", padx=5, pady=5)

        self.content_label = ttk.Label(self.content_frame, text="Select an option to view input fields", font=("Arial", 12))
        self.content_label.pack(pady=20)

        # Output area spanning across the bottom
        output_frame = ttk.Frame(root, bootstyle="dark")
        output_frame.pack(side="bottom", fill="x", padx=10, pady=5)

        ttk.Label(output_frame, text="Output", font=("Arial", 14), bootstyle="light").pack(anchor="nw", padx=10, pady=5)

        self.output_text = tk.Text(output_frame, height=5, font=("Courier", 12), bg="#2c3e50", fg="white", wrap="word")
        self.output_text.pack(expand=True, fill="both", padx=10, pady=10)
        self.output_text.insert("end", "Output will be displayed here...")

    def show_scrape(self):
        self.clear_content()
        ttk.Label(self.content_frame, text="Select Index:", font=("Arial", 12)).pack(pady=5)
        self.index_var = ttk.Combobox(self.content_frame, values=["S&P 500", "NASDAQ 100", "Dow Jones"], bootstyle="info")
        self.index_var.pack(pady=5)
        ttk.Button(self.content_frame, text="Scrape Data", bootstyle="success", command=self.upload_symbol_script).pack(pady=5)

    def show_upload(self):
        self.clear_content()
        ttk.Label(self.content_frame, text="Upload Excel File:", font=("Arial", 12)).pack(pady=5)
        self.file_entry = ttk.Entry(self.content_frame, width=40, bootstyle="light")
        self.file_entry.pack(pady=5)
        ttk.Button(self.content_frame, text="Browse", bootstyle="primary", command=self.upload_file).pack(pady=5)

    def show_lookup(self):
        self.clear_content()
        ttk.Label(self.content_frame, text="Enter Stock Symbol:", font=("Arial", 12)).pack(pady=5)
        self.symbol_entry = ttk.Entry(self.content_frame, width=30, bootstyle="light")
        self.symbol_entry.pack(pady=5)

    def clear_content(self):
        for widget in self.content_frame.winfo_children():
            widget.destroy()

    def upload_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx")])
        if file_path:
            self.file_entry.delete(0, "end")
            self.file_entry.insert(0, file_path)

    def upload_symbol_script(self):
        file_path = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx")])
        if not file_path:
            messagebox.showerror("Error", "Please select an Excel file.")
            return
        
        output_path = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel files", "*.xlsx")])
        if not output_path:
            self.update_output("File save canceled.")
            return
        
        self.update_output("Starting data upload...")
        threading.Thread(target=self.run_upload_symbol_script, args=(file_path, "Sheet1", "2001-01-01", "2024-12-31", output_path)).start()

    def run_upload_symbol_script(self, file_path, sheetname, start_date, end_date, output_file_path):
        new_sorting_df = pd.read_excel(file_path, sheet_name=sheetname)
        symbols = new_sorting_df['Symbol'].dropna().unique()

        market_index = '^GSPC'
        market_data = yf.download(market_index, start=start_date, end=end_date)
        market_data.index = market_data.index.tz_localize(None)
        market_returns = market_data['Close'].pct_change().dropna()

        results = []
        for index, symbol in enumerate(symbols):
            data = fetch_stock_data(symbol, market_returns, start_date, end_date)
            if data:
                results.append(data)
            self.update_output(f"Processing {index + 1}/{len(symbols)}: {symbol}")
            time.sleep(1)

        results_df = pd.DataFrame(results)
        updated_new_sorting_df = new_sorting_df.merge(results_df, on='Symbol', how='left')

        with pd.ExcelWriter(output_file_path, engine='openpyxl') as writer:
            updated_new_sorting_df.to_excel(writer, sheet_name=sheetname, index=False)

        self.update_output(f"Updated file saved to {output_path}")

    def update_output(self, message):
        self.output_text.insert("end", f"{message}\n")
        self.output_text.see("end")

if __name__ == "__main__":
    root = ttk.Window(themename="darkly")  # Using modern dark theme
    app = SymbolAggregationGUI(root)
    root.mainloop()
