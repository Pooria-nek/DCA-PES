import pandas as pd
import tkinter as tk
from tkinter import filedialog, ttk, messagebox
import matplotlib.pyplot as plt
import seaborn as sns

class CSVVisualizerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("CSV Data Visualizer")
        self.root.geometry("700x500")

        # File selection button
        self.btn_open = tk.Button(root, text="Select CSV File", command=self.load_csv, font=("Arial", 12))
        self.btn_open.pack(pady=10)

        # Table to display data preview
        self.tree = ttk.Treeview(root)
        self.tree.pack(expand=True, fill="both", padx=10, pady=10)

        # Dropdown for selecting plot type
        self.plot_type = tk.StringVar(value="Line Plot")
        self.plot_dropdown = ttk.Combobox(root, textvariable=self.plot_type, values=["Line Plot", "Scatter Plot", "Histogram"])
        self.plot_dropdown.pack(pady=5)

        # Button to visualize data
        self.btn_plot = tk.Button(root, text="Visualize Data", command=self.visualize_data, font=("Arial", 12))
        self.btn_plot.pack(pady=10)

        self.df = None  # Data storage

    def load_csv(self):
        file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if not file_path:
            return
        
        try:
            self.df = pd.read_csv(file_path)
            self.show_data_preview()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load file: {e}")

    def show_data_preview(self):
        """ Display first few rows in the treeview (table). """
        if self.df is None or self.df.empty:
            return
        
        # Clear existing data
        self.tree.delete(*self.tree.get_children())

        # Set column names
        self.tree["columns"] = list(self.df.columns)
        self.tree["show"] = "headings"

        # Add column headings
        for col in self.df.columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, anchor="center", width=100)

        # Add rows (show first 10 rows)
        for _, row in self.df.head(1000).iterrows():
            self.tree.insert("", "end", values=list(row))

    def visualize_data(self):
        """ Generate plots based on selected type. """
        if self.df is None or self.df.empty:
            messagebox.showerror("Error", "No data loaded!")
            return

        plot_type = self.plot_type.get()
        
        # Select the first two columns if they exist
        if len(self.df.columns) < 2:
            messagebox.showerror("Error", "CSV must have at least two columns to visualize.")
            return
        
        col1, col2 = self.df.columns[:2]  # Use first two columns

        plt.figure(figsize=(8, 5))
        
        if plot_type == "Line Plot":
            plt.plot(self.df[col1], self.df[col2], marker="o", linestyle="-")
            plt.xlabel(col1)
            plt.ylabel(col2)
            plt.title("Line Plot")

        elif plot_type == "Scatter Plot":
            sns.scatterplot(data=self.df, x=col1, y=col2)
            plt.title("Scatter Plot")

        elif plot_type == "Histogram":
            sns.histplot(self.df[col1], bins=20, kde=True)
            plt.title("Histogram")

        plt.show()

# Run the application
if __name__ == "__main__":
    root = tk.Tk()
    app = CSVVisualizerApp(root)
    root.mainloop()