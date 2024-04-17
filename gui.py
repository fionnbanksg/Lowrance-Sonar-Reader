#bestFit: https://www.desmos.com/calculator/iyuftxwub9
import tkinter as tk
from tkinter import filedialog
from tkinter import ttk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from reader import read_sl, read_bin
import numpy as np
import os
import math

dataframe = None
primary_np = None

def open_sl_file():
    global primary_np
    global dataframe
    file_path = filedialog.askopenfile(filetypes=[("SL files", "*.sl3"), ("SL files", "*.sl2")])
    if file_path:
        print("Selected Filepath", file_path)
        sl_bin_data = read_bin(file_path.name)
        df = read_sl(file_path.name)
        dataframe = df 
        df_primary = df.query("survey_label == 'primary' & max_range < 60") 
        primary_list = [np.frombuffer(sl_bin_data[(f+168):(f+(p-168))], dtype="uint8") for f, p in zip(df_primary["first_byte"], df_primary["frame_size"])]
        primary_np = np.stack(primary_list)
        update_image(primary_np)
        export_menu.entryconfig("Export Sonar Data", state="normal")
        export_menu.entryconfig("Export Other Data", state="normal")
        export_menu.entryconfig("Export Sonar Data (Non Normalised)", state="normal")
        export_menu.entryconfig("Export Sonar (20log(value))", state="normal")
        export_menu.entryconfig("Export Voltage Levels (mV)", state="normal")

def update_image(primary_np):
    ax.clear()  # Clear the previous plot
    if primary_np is None:
        ax.text(0.5, 0.5, 'Click File > Open SL File to open an SL2 or SL3 file.', horizontalalignment='center', verticalalignment='center', transform=ax.transAxes, fontsize=12, color='gray')
        ax.axis('off')
    else:
        image = 20*np.log(primary_np.transpose())
        adjusted_image =  image * intensity_var.get()
        ax.imshow(adjusted_image, cmap=color_profile_var.get(), aspect='auto', vmin=0, vmax=255)


        ax.axis('off')
    ax.set_position([0, 0, 1, 1])  # Set the position of the subplot to fill the entire figure
    canvas.draw()

def export_sonar_data(primary_np):
    filetypes = [
        ("CSV Files", "*.csv"),
        ("Text Files", "*.txt")
    ]
    file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=filetypes)
    
    if file_path:
        file_extension = os.path.splitext(file_path)[1]
        
        if file_extension == '.txt':
            np.savetxt(file_path, primary_np.transpose()/255, delimiter='\t', fmt='%f')
        elif file_extension == '.csv':
            np.savetxt(file_path, primary_np.transpose()/255, delimiter=',', fmt='%f')
        else:
            print("Unsupported file type.")

def export_sonar_data_non_normalised(primary_np):
    filetypes = [
        ("CSV Files", "*.csv"),
        ("Text Files", "*.txt")
    ]
    file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=filetypes)
    
    if file_path:
        file_extension = os.path.splitext(file_path)[1]
        
        if file_extension == '.txt':
            np.savetxt(file_path, primary_np.transpose(), delimiter='\t', fmt='%d')
        elif file_extension == '.csv':
            np.savetxt(file_path, primary_np.transpose(), delimiter=',', fmt='%d')
        else:
            print("Unsupported file type.")


def export_voltage_levels_preliminary(primary_np):
    filetypes = [
        ("CSV Files", "*.csv"),
        ("Text Files", "*.txt")
    ]
    file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=filetypes)
    values = np.power(math.e, (primary_np.transpose()-135.61)/15.11)
    if file_path:
        file_extension = os.path.splitext(file_path)[1]
        
        if file_extension == '.txt':
            np.savetxt(file_path, values, delimiter='\t', fmt='%f')
        elif file_extension == '.csv':
            np.savetxt(file_path, values, delimiter=',', fmt='%f')
        else:
            print("Unsupported file type.")



def export_sonar_data_log(primary_np):
    filetypes = [
        ("CSV Files", "*.csv"),
        ("Text Files", "*.txt")
    ]
    file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=filetypes)
    
    if file_path:
        file_extension = os.path.splitext(file_path)[1]
        
        if file_extension == '.txt':
            np.savetxt(file_path, 20*np.log(primary_np.transpose()/180), delimiter='\t', fmt='%f')
        elif file_extension == '.csv':
            np.savetxt(file_path, 20*np.log(primary_np.transpose()/180), delimiter=',', fmt='%f')
        else:
            print("Unsupported file type.")


def export_other_data(dataframe):
    filetypes = [
        ("CSV Files", "*.csv"),
        ("Text Files", "*.txt")
    ]
    file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=filetypes)
    
    if file_path:
        file_extension = os.path.splitext(file_path)[1]
        
        if file_extension == '.txt':
            dataframe.to_csv(file_path, sep='\t', index=False)
        elif file_extension == '.csv':
            dataframe.to_csv(file_path, sep=',', index=False)
        else:
            print("Unsupported file type.")

def on_color_profile_change(event):
    update_image(primary_np)


def on_intensity_change(event):
    update_image(primary_np)

def on_window_resize(event):
    update_image(primary_np)

root = tk.Tk()
root.title("Lowrance SL File Reader")
root.attributes("-fullscreen", False)
menu_bar = tk.Menu(root)
root.config(menu=menu_bar)

file_menu = tk.Menu(menu_bar, tearoff=False)
export_menu = tk.Menu(menu_bar, tearoff=False)

menu_bar.add_cascade(label="File", menu=file_menu)
menu_bar.add_cascade(label="Export", menu=export_menu)

file_menu.add_command(label="Open SL File", command=open_sl_file)
export_menu.add_command(label="Export Sonar Data", command=lambda:export_sonar_data(primary_np), state="disabled")
export_menu.add_command(label="Export Sonar Data (Non Normalised)", command=lambda:export_sonar_data_non_normalised(primary_np), state="disabled")
export_menu.add_command(label="Export Sonar (20log(value))", command=lambda:export_sonar_data_log(primary_np), state="disabled")
export_menu.add_command(label="Export Other Data", command=lambda:export_other_data(dataframe), state="disabled")
export_menu.add_command(label="Export Voltage Levels (mV)", command=lambda:export_voltage_levels_preliminary(primary_np), state="disabled")


figure = Figure(figsize=(7, 4), dpi=120) 

ax = figure.add_subplot(111)
canvas = FigureCanvasTkAgg(figure, master=root)
canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)
color_profile_var = tk.StringVar(value="cividis")  
intensity_var = tk.DoubleVar(value=0.0) 
color_profile_label = tk.Label(root, text="Color Profile:")
color_profile_label.pack()
color_profile_scale = ttk.Combobox(root, textvariable=color_profile_var, values=["viridis", "cividis", "plasma", "magma", "inferno", "twilight", "spring", "summer", "autumn", "winter"])  # Add more color profiles if needed
color_profile_scale.bind("<<ComboboxSelected>>", on_color_profile_change)
color_profile_scale.pack()

intensity_label = tk.Label(root, text="Intensity:")
intensity_label.pack()
intensity_scale = ttk.Scale(root, from_=0, to=2, variable=intensity_var, orient="horizontal")
intensity_scale.bind("<ButtonRelease-1>", on_intensity_change )
intensity_scale.bind("<Motion>", on_intensity_change)
intensity_scale.pack()

root.bind("<Configure>", on_window_resize) 
update_image(primary_np)  

root.mainloop()
