from AppKit import NSWorkspace
import time
import json
from datetime import datetime
import os
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tkinter as tk
from tkinter import messagebox
from tkcalendar import DateEntry

# Global variables
active_window_start_time = None
daily_totals = {}
json_filename = 'window_times.json'

def save_window_times_to_json(filename):
    with open(filename, 'w') as file:
        json.dump(daily_totals, file, indent=4)

def format_time(seconds):
    hours, remainder = divmod(seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    
    if hours > 0:
        return f"{hours} hours"
    elif minutes > 0:
        return f"{minutes} minutes"
    else:
        return f"{seconds} seconds"

def get_active_window_title():
    active_app_name = NSWorkspace.sharedWorkspace().activeApplication()['NSApplicationName']
    return active_app_name

def load_existing_data(filename):
    global daily_totals
    if os.path.exists(filename):
        with open(filename, 'r') as file:
            try:
                daily_totals = json.load(file)
            except json.JSONDecodeError:
                daily_totals = {}

def plot_data(date):
    if not daily_totals:
        messagebox.showinfo("No Data", "No data to display.")
        return

    date_str = date.isoformat()

    if date_str not in daily_totals:
        messagebox.showinfo("No Data", f"No data available for {date_str}.")
        return

    data = daily_totals[date_str]
    
    if not data:
        messagebox.showinfo("No Data", f"No data available for {date_str}.")
        return
    
    sorted_data = sorted(data.items(), key=lambda x: x[1], reverse=True)

    apps = [item[0] for item in sorted_data]
    times_seconds = [item[1] for item in sorted_data]
    times_mins = [time / 60 for time in times_seconds]

    fig, ax = plt.subplots()
    ax.barh(apps, times_mins, color='skyblue')
    ax.set_xlabel('Time Spent (mins)')
    ax.set_ylabel('Application')
    ax.set_title(f'Time Spent on Applications for {date_str}')

    for widget in canvas.get_tk_widget().winfo_children():
        widget.destroy()

    canvas.figure = fig
    canvas.draw()

def on_date_change(event):
    selected_date = calendar.get_date()
    plot_data(selected_date)

if __name__ == '__main__':
    try:
        previous_window = None

        load_existing_data(json_filename)

        # Create the main window
        root = tk.Tk()
        root.title("Time Watch")

        # Create a frame for the plot
        plot_frame = tk.Frame(root)
        plot_frame.pack(fill=tk.BOTH, expand=True)

        # Create a canvas for the matplotlib plot
        fig, ax = plt.subplots()
        canvas = FigureCanvasTkAgg(fig, master=plot_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # Create a date picker
        calendar_frame = tk.Frame(root)
        calendar_frame.pack(fill=tk.X, expand=False)
        tk.Label(calendar_frame, text="Select Date:").pack(side=tk.LEFT, padx=10)
        calendar = DateEntry(calendar_frame, width=12, background='darkblue',
                            foreground='white', borderwidth=2, year=datetime.now().year)
        calendar.pack(side=tk.LEFT, padx=10)
        calendar.bind("<<DateEntrySelected>>", on_date_change)

        # Create a button to refresh the plot
        refresh_button = tk.Button(root, text="Refresh", command=lambda: plot_data(calendar.get_date()))
        refresh_button.pack()

        while True:
            active_window_title = get_active_window_title()

            current_time = datetime.now()
            today = current_time.date().isoformat()

            if active_window_title != previous_window:
                if previous_window:
                    time_spent = (current_time - active_window_start_time).total_seconds()
                    if today not in daily_totals:
                        daily_totals[today] = {}

                    if previous_window in daily_totals[today]:
                        daily_totals[today][previous_window] += time_spent
                    else:
                        daily_totals[today][previous_window] = time_spent

                previous_window = active_window_title
                active_window_start_time = current_time

                print(f"Active Window: {active_window_title}")

                save_window_times_to_json(json_filename)
            else:
                if previous_window and active_window_start_time:
                    time_spent = (current_time - active_window_start_time).total_seconds()
                    if today not in daily_totals:
                        daily_totals[today] = {}
                    if previous_window in daily_totals[today]:
                        daily_totals[today][previous_window] += time_spent
                    else:
                        daily_totals[today][previous_window] = time_spent

                active_window_start_time = current_time

            root.update_idletasks()
            root.update()
            time.sleep(1)
    except KeyboardInterrupt:
        print('\nStopped!')
        save_window_times_to_json(json_filename)
    finally:
        save_window_times_to_json(json_filename)
