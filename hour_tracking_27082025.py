# hour_tracker_gui.py (Final version with correct subfolder path)

import os
import csv
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import unicodedata

try:
    from tkcalendar import DateEntry
except ImportError:
    messagebox.showerror(
        "Missing Library",
        "The 'tkcalendar' library is required. Please install it by running:\n\npip install tkcalendar"
    )
    exit()

# --- Configuration & Core Logic ---
SUBJECT_OPTIONS = ["Technical Work", "Meetings", "Data Annotation", "Documentation", "Training Models"]
CSV_HEADER = ['name', 'date', 'hours', 'subject']

# --- MODIFIED: Build path relative to the script's location, not the working directory ---
# 1. Get the directory where the script itself is located.
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
# 2. Define the data folder name and join it with the script's directory.
DATA_FOLDER = os.path.join(SCRIPT_DIR, "hour_tracking_files")


def get_employee_filename(name):
    """Generates a safe, ASCII-only filename inside the data subfolder."""
    normalized_name = unicodedata.normalize('NFD', name)
    ascii_name = normalized_name.encode('ascii', 'ignore').decode('ascii')
    safe_filename_base = ascii_name.strip().replace(" ", "_").lower()
    filename = f"{safe_filename_base}_hours.csv"
    
    return os.path.join(DATA_FOLDER, filename)


# --- GUI Application ---
class HourTrackerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("AI Project Hour Tracker")
        self.root.geometry("950x900")
        self.root.minsize(800, 600)

        # Create the data subfolder on startup if it doesn't exist.
        # This will now use the correct, absolute path.
        os.makedirs(DATA_FOLDER, exist_ok=True)

        self.style = ttk.Style(self.root)
        self.style.theme_use('clam')
        self.style.configure('TEntry', borderwidth=1, relief="solid")

        self.existing_names = self._get_existing_names()

        self.notebook = ttk.Notebook(root)
        self.notebook.pack(pady=10, padx=10, expand=True, fill='both')

        self.log_frame = ttk.Frame(self.notebook, padding="20")
        self.notebook.add(self.log_frame, text='Log Your Hours')
        self.create_log_widgets()

        self.manager_frame = ttk.Frame(self.notebook, padding="20")
        self.notebook.add(self.manager_frame, text='Manager Dashboard')
        self.create_manager_widgets()

    def _get_existing_names(self):
        """Scans the data subfolder for CSV files and extracts names."""
        names = set()
        
        try:
            file_list = [f for f in os.listdir(DATA_FOLDER) if f.endswith("_hours.csv")]
        except FileNotFoundError:
            return []

        if not file_list:
            return []

        for filename in file_list:
            full_path = os.path.join(DATA_FOLDER, filename)
            try:
                df = pd.read_csv(full_path, encoding='utf-8')
                if not df.empty and 'name' in df.columns:
                    for name in df['name'].unique():
                        names.add(name)
            except Exception:
                continue
        
        return sorted(list(names))
        
    def create_log_widgets(self):
        """Creates the widgets for the 'Log Your Hours' tab with a centered layout."""
        self.log_frame.columnconfigure(0, weight=1)
        self.log_frame.columnconfigure(1, weight=0)
        self.log_frame.columnconfigure(2, weight=1)
        
        log_container = ttk.LabelFrame(self.log_frame, text="Log New Entry", padding=20)
        log_container.grid(row=0, column=1, pady=20, sticky="n")
        log_container.columnconfigure(1, minsize=300)

        ttk.Label(log_container, text="Your Full Name:").grid(row=0, column=0, padx=5, pady=10, sticky="w")
        self.name_combobox = ttk.Combobox(log_container, values=self.existing_names)
        self.name_combobox.grid(row=0, column=1, padx=5, pady=10, sticky="ew")

        ttk.Label(log_container, text="Date (dd-mm-yyyy):").grid(row=1, column=0, padx=5, pady=10, sticky="w")
        self.date_entry = DateEntry(log_container, date_pattern='dd-mm-yyyy', borderwidth=2)
        self.date_entry.grid(row=1, column=1, padx=5, pady=10, sticky="ew")
        
        ttk.Label(log_container, text="Hours Worked:").grid(row=2, column=0, padx=5, pady=10, sticky="w")
        self.hours_entry = ttk.Entry(log_container)
        self.hours_entry.grid(row=2, column=1, padx=5, pady=10, sticky="ew")

        ttk.Label(log_container, text="Work Subject:").grid(row=3, column=0, padx=5, pady=10, sticky="w")
        self.subject_combobox = ttk.Combobox(log_container, values=SUBJECT_OPTIONS, state='readonly')
        self.subject_combobox.grid(row=3, column=1, padx=5, pady=10, sticky="ew")
        if SUBJECT_OPTIONS:
            self.subject_combobox.current(0)
            
        self.style.configure('Accent.TButton', foreground='white', background='#007BFF')
        submit_button = ttk.Button(log_container, text="Log Hours", command=self.log_hours, style='Accent.TButton')
        submit_button.grid(row=4, column=1, padx=5, pady=20, sticky="e")
        
    def log_hours(self):
        name = self.name_combobox.get().strip()
        date_str = self.date_entry.get().strip()
        hours_str = self.hours_entry.get().strip()
        subject = self.subject_combobox.get()
        
        if not all([name, date_str, hours_str, subject]):
            messagebox.showerror("Input Error", "All fields are required.")
            return

        try:
            date_obj = datetime.strptime(date_str, "%d-%m-%Y")
        except ValueError:
            messagebox.showerror("Input Error", "Invalid date format. Please use dd-mm-yyyy.")
            return

        try:
            hours = float(hours_str)
            if hours <= 0:
                messagebox.showerror("Input Error", "Hours must be a positive number.")
                return
        except ValueError:
            messagebox.showerror("Input Error", "Hours must be a valid number.")
            return
            
        filename = get_employee_filename(name)
        file_exists = os.path.exists(filename)
        date_to_save = date_obj.strftime("%Y-%m-%d")

        try:
            with open(filename, 'a', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                if not file_exists:
                    writer.writerow(CSV_HEADER)
                writer.writerow([name, date_to_save, hours, subject])

            messagebox.showinfo("Success", f"Successfully logged {hours} hours for {name}.")
            self.hours_entry.delete(0, 'end')

            if name not in self.existing_names:
                self.existing_names.append(name)
                self.existing_names.sort()
                self.name_combobox['values'] = self.existing_names

        except IOError as e:
            messagebox.showerror("File Error", f"Could not write to file {filename}.\n{e}")

    def create_manager_widgets(self):
        controls_frame = ttk.Frame(self.manager_frame)
        controls_frame.pack(fill='x', pady=5)
        
        refresh_button = ttk.Button(controls_frame, text="Load/Refresh Project Data", command=self.show_dashboard)
        refresh_button.pack(side='left')

        self.total_hours_label = ttk.Label(controls_frame, text="Total Project Hours: N/A", font=("Helvetica", 12, "bold"))
        self.total_hours_label.pack(side='right', padx=10)

        main_pane = ttk.PanedWindow(self.manager_frame, orient=tk.VERTICAL)
        main_pane.pack(fill='both', expand=True, pady=10)

        self.charts_frame = ttk.Frame(main_pane)
        main_pane.add(self.charts_frame, weight=4)

        summary_pane = ttk.PanedWindow(main_pane, orient=tk.HORIZONTAL)
        main_pane.add(summary_pane, weight=1)

        person_frame = ttk.LabelFrame(summary_pane, text="Hours by Team Member")
        summary_pane.add(person_frame, weight=1)
        self.person_tree = ttk.Treeview(person_frame, columns=('name', 'hours'), show='headings')
        self.person_tree.heading('name', text='Name')
        self.person_tree.column('name', anchor='w')
        self.person_tree.heading('hours', text='Total Hours')
        self.person_tree.column('hours', anchor='e', width=100)
        self.person_tree.pack(fill='both', expand=True)

        subject_frame = ttk.LabelFrame(summary_pane, text="Hours by Subject")
        summary_pane.add(subject_frame, weight=1)
        self.subject_tree = ttk.Treeview(subject_frame, columns=('subject', 'hours'), show='headings')
        self.subject_tree.heading('subject', text='Subject')
        self.subject_tree.column('subject', anchor='w')
        self.subject_tree.heading('hours', text='Total Hours')
        self.subject_tree.column('hours', anchor='e', width=100)
        self.subject_tree.pack(fill='both', expand=True)

    def show_dashboard(self):
        all_data = []
        
        try:
            file_list = [f for f in os.listdir(DATA_FOLDER) if f.endswith("_hours.csv")]
        except FileNotFoundError:
            messagebox.showinfo("No Data", f"The data folder '{DATA_FOLDER}' was not found.")
            return

        if not file_list:
            messagebox.showinfo("No Data", "No project data files (.csv) found.")
            return

        for filename in file_list:
            full_path = os.path.join(DATA_FOLDER, filename)
            try:
                df = pd.read_csv(full_path, encoding='utf-8')
                if not df.empty: all_data.append(df)
            except Exception as e:
                messagebox.showwarning("File Read Error", f"Could not read {full_path}.\nError: {e}")
        
        if not all_data:
            messagebox.showinfo("No Data", "No valid data found in CSV files.")
            return
            
        master_df = pd.concat(all_data, ignore_index=True)
        master_df['date'] = pd.to_datetime(master_df['date'])

        total_hours = master_df['hours'].sum()
        hours_by_person = master_df.groupby('name')['hours'].sum().reset_index()
        hours_by_subject = master_df.groupby('subject')['hours'].sum().reset_index()
        
        self.total_hours_label.config(text=f"Total Project Hours: {total_hours:.2f}")

        for i in self.person_tree.get_children(): self.person_tree.delete(i)
        for _, row in hours_by_person.iterrows(): self.person_tree.insert("", "end", values=(row['name'], f"{row['hours']:.2f}"))

        for i in self.subject_tree.get_children(): self.subject_tree.delete(i)
        for _, row in hours_by_subject.iterrows(): self.subject_tree.insert("", "end", values=(row['subject'], f"{row['hours']:.2f}"))
        
        self.draw_charts(master_df, hours_by_person)

    def draw_charts(self, master_df, hours_by_person):
        for widget in self.charts_frame.winfo_children():
            widget.destroy()

        plt.style.use('seaborn-v0_8-whitegrid')
        fig = plt.Figure(figsize=(9, 5), dpi=100, facecolor='#F0F0F0') 
        
        ax1 = fig.add_subplot(121)
        weekly_hours = master_df.set_index('date').resample('W-MON', label='left')['hours'].sum()
        weekly_hours.index = weekly_hours.index.strftime('%Y-%m-%d')
        weekly_hours.plot(kind='bar', ax=ax1, color='skyblue', legend=False)
        ax1.set_title('Total Hours per Week')
        ax1.set_xlabel('Week Start Date')
        ax1.set_ylabel('Hours')
        ax1.tick_params(axis='x', rotation=45, labelsize=9)
        ax1.grid(True, axis='y', linestyle='--', alpha=0.7)

        ax2 = fig.add_subplot(122)
        pie_labels = hours_by_person['name']
        pie_sizes = hours_by_person['hours']
        ax2.pie(pie_sizes, labels=pie_labels, autopct='%1.1f%%', startangle=90, textprops={'fontsize': 9})
        ax2.set_title('Work Distribution by Member')
        ax2.axis('equal') 
        
        fig.tight_layout()

        canvas = FigureCanvasTkAgg(fig, master=self.charts_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

if __name__ == "__main__":
    root = tk.Tk()
    app = HourTrackerApp(root)
    root.mainloop()