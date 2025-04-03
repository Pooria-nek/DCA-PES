import pandas as pd
import tkinter as tk
from tkinter import filedialog, ttk, messagebox, simpledialog
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from scipy.signal import argrelextrema, find_peaks
import scipy.stats

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
        self.plot_dropdown = ttk.Combobox(root, textvariable=self.plot_type, values=["Line Plot", "Scatter Plot", "Decline Curve"])
        self.plot_dropdown.pack(pady=5)

        # Button to visualize data
        self.btn_plot = tk.Button(root, text="Visualize Data", command=self.visualize_data, font=("Arial", 12))
        self.btn_plot.pack(pady=10)

        self.start_date = None
        self.end_date = None
        self.count_date = None

        self.df = None  # Data frame
        self.cdf = None  # clean Data frame
        self.pdf = None  # peaks of Data frame
        self.dc = None  # Decline Curves

        # self.maxpoints = []
        # self.minpoints = []
        self.minima = []
        self.maxima = []
        self.peaks = []

    def load_csv(self):
        file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if not file_path:
            return
        
        try:
            self.df = pd.read_csv(file_path)
            self.cdf = self.df.copy()
            
            # Remove minima from the second column (if applicable)
            if len(self.cdf.columns) > 1:
                y_col = self.cdf.columns[1]
                self.cdf[y_col] = self.removeMinima(self.cdf[y_col], factor=1.2)
                # self.df = self.removeOutliers(self.df, y_col, zScoreThreshhold=3.5)
            
            
            self.show_data_preview()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load file: {e}")

    #%% Removes outliers and fills missing data with interpolation
    def removeMinima(self, data, factor):
        if data.empty:
            return data    
        if data.isnull().all():
            return data
        A = -data.diff()
        threshholdDiff = (A[A > 0]).median(skipna=True)
        M = -data
        indices = find_peaks(M, prominence=threshholdDiff * factor)[0]
        data.iloc[indices] = np.nan
        # print(f"Indices of minima: {indices}")
        self.minima = indices
        print(f"Minima: {self.minima}")
        return data.interpolate()
    
    # def removeOutliers(df, fieldName,zScoreThreshhold):
    #     #remove outliers in oil production
    #     if df.empty:
    #         return df
    #     df=df.replace({np.nan:0})
    #     df=df[(np.abs(scipy.stats.zscore(df[fieldName])) < zScoreThreshhold)]
    #     #plotProductionData(df, 'Outliers removed')
        
    #     # replace 0 values with nan
    #     df=df.replace({0: np.nan})
    #     return df

    def findPeaks(self, data):
        """ Find peaks in the data. """
        M = pd.concat([pd.Series([0]), data])    
        M = M.to_numpy()    
        ### IMPORTANT ### order should be defined by user
        indices = argrelextrema(M, np.greater, order=6)
        indices = np.asarray(indices) - 1
        indices = indices.flatten()
        self.peaks = indices
        print(f"Peaks: {self.peaks}")
        return indices

    def show_data_preview(self):
        """ Display first few rows in the treeview (table) and highlight peak positions. """
        if self.df is None or self.df.empty:
            return
        
        # Clear existing data
        self.tree.delete(*self.tree.get_children())

        # Set column names
        self.tree["columns"] = ["Index"] + list(self.df.columns)
        self.tree["show"] = "headings"

        # Add column headings
        self.tree.heading("Index", text="Index")
        self.tree.column("Index", anchor="center", width=50)
        for col in self.df.columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, anchor="center", width=100)

        # Add rows (show first 1000 rows)
        for idx, row in self.df.head(1000).iterrows():
            self.tree.insert("", "end", values=[idx] + list(row))

        # Highlight peak positions in the second column (if applicable)
        if len(self.df.columns) > 1:
            y_col = self.df.columns[1]
            peaks = self.findPeaks(self.df[y_col])
            for peak in self.peaks:
                self.tree.item(self.tree.get_children()[peak], tags=("peak",))

        for minima in self.minima:
            self.tree.item(self.tree.get_children()[minima], tags=("minima",))

        # Add tag styling for peaks
        self.tree.tag_configure("peak", background="lightblue")
        self.tree.tag_configure("minima", background="#FF6666")

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

        self.start_date = self.df[col1].iloc[0]
        self.end_date = self.df[col1].iloc[-1]
        self.count_date = len(self.df[col1])

        print(f"Start Date: {self.start_date}")
        print(f"End Date: {self.end_date}")
        print(f"Count Date: {self.count_date}")

        plt.figure(figsize=(8, 5))
        
        if plot_type == "Line Plot":
            # Plot line graph for both original and cleaned data
            self.plot_line(col1, col2)
            print(self.df)

        elif plot_type == "Scatter Plot":
            # Plot scatter graph
            self.plot_scatter(col1, col2)
            print(self.df)
            # sns.scatterplot(data=self.df, x=col1, y=col2)
            # plt.title("Scatter Plot")

        elif plot_type == "Decline Curve":
            self.plot_decline_curve(col1, col2)
            print(self.df)

        else:
            messagebox.showerror("Error", "Invalid plot type selected.")
            return

        plt.show()

    def plot_line(self, x_col, y_col):
        """ Plot line graph. """
        plt.plot(self.df[x_col], self.df[y_col], marker="o", linestyle="-", label="Original Data")
        plt.plot(self.cdf[x_col], self.cdf[y_col], marker="o", linestyle="-", color="green", label="Cleaned Data")
        plt.legend()
        plt.xticks(rotation=60)
        plt.tight_layout()
        # plt.grid()
        # plt.axhline(0, color='black', lw=0.5, ls='--')
        # plt.axvline(0, color='black', lw=0.5, ls='--')
        # plt.fill_between(self.df[x_col], self.df[y_col], color="lightblue", alpha=0.5)
        # plt.fill_between(self.cdf[x_col], self.cdf[y_col], color="lightgreen", alpha=0.5)
        plt.xlabel(x_col)
        plt.ylabel(y_col)
        plt.title("Line Plot")

    def plot_scatter(self, x_col, y_col):
        """ Plot scatter graph. """
        plt.scatter(self.df[x_col], self.df[y_col], marker="o")
        plt.xlabel(x_col)
        plt.ylabel(y_col)
        plt.title("Scatter Plot")

    def plot_histogram(self, x_col):
        """ Plot histogram. """
        plt.hist(self.df[x_col], bins=30, alpha=0.7)
        plt.xlabel(x_col)
        plt.ylabel("Frequency")
        plt.title("Histogram")

    def plot_decline_curve(self, x_col, y_col):
        """ Plot Decline Curves in green color. """

        # Generate dates from start_date to end_date
        date_range = pd.date_range(start=self.start_date, end=self.end_date, periods=self.count_date)
        
        # Create random data for x_col
        x_data = self.df[x_col]

        # Create a decline curve for y_col
        # Assuming exponential decline for demonstration purposes
        start_value = self.df[y_col].iloc[0]

        # Prompt user to input decline rate
        decline_rate = simpledialog.askfloat("Input", "Enter decline rate:", minvalue=0.0, maxvalue=1.0)
        if decline_rate is None:
            return

        y_data = start_value * np.exp(-decline_rate * np.arange(self.count_date))
        
        # Create DataFrame with generated data
        self.dc = pd.DataFrame({x_col: x_data, y_col: y_data})

        print(self.dc)

        plt.plot(self.df[x_col], self.df[y_col], marker="o", linestyle="-", label="Original Data")
        plt.plot(self.dc[x_col], self.dc[y_col], marker="o", linestyle="-", color="green", label="Decline Curve")
        plt.legend()
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.xlabel(x_col)
        plt.ylabel(y_col)
        plt.title("Decline Curve")
        plt.legend()

# Run the application
if __name__ == "__main__":
    root = tk.Tk()
    app = CSVVisualizerApp(root)
    root.mainloop()