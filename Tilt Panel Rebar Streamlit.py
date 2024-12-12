# %%
# import sys
import os
import re
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.patches import Rectangle
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from statistics import mean
# from PyPDF2 import PdfMerger
# import tkinter as tk
# from tkinter import filedialog
# from tkinter import ttk
# from tkinter import messagebox
import streamlit as st
from streamlit_file_browser import st_file_browser

# %%
# # Find the tup folder
# def browse_folder():
#     folder_path = filedialog.askdirectory()
#     if folder_path:
#         folder_var.set(folder_path)



# def ok_button():
#     root.destroy()

# root = tk.Tk()
# root.title("Folder Directory Browser")

# # create a checkbox variable
# rbrcheck_var = tk.IntVar()
# viewcheck_var = tk.IntVar()
# pdfcheck_var = tk.IntVar()

# # create a checkbox
# checkbox = tk.Checkbutton(root, text="Show Rebar Area", variable=rbrcheck_var)
# checkbox.pack()

# # create a checkbox
# checkbox = tk.Checkbutton(root, text="Show Rebar Viewer", variable=viewcheck_var)
# checkbox.pack()

# # create a checkbox
# checkbox = tk.Checkbutton(root, text="Print rebar to PDF", variable=pdfcheck_var)
# checkbox.pack()

# # create a label to display the selected folder path
# folder_var = tk.StringVar()
# folder_label = tk.Label(root, textvariable=folder_var, width=50)
# folder_label.pack()

# # add a button to browse folders
# browse_button = tk.Button(root, text="Browse", command=browse_folder)
# browse_button.pack()

# # add an "OK" button to close the dialog
# ok_button = tk.Button(root, text="OK", command=ok_button)
# ok_button.pack()

# root.mainloop()

# # get the selected folder path after the window is closed
# selected_folder_path = folder_var.get()

# %% Streamlit file broswer to get the folder path were the .tup files are stored
event = st_file_browser("example_artifacts", key='A')
st.write(event)

# %%
def reading_tup():
    # Define a list of items to look for in each line
    items = ['PanelType', 'ParapetHeight', 'BottomPanelHeight', 'PanelHeight', 'PanelLength', 'PanelThickness', 'PanelMaterial', 'Openings', 'DataVBarsCount', 'DataVBarsVBars','DataHBarsCount', 'DataHBarsHBars']

    # Initialize an empty dictionary for each item
    item_dict = {key: np.nan for key in items}

    # Define a blank Dataframe with the column names
    df = pd.DataFrame(columns = items)

    # Read in command-line arguments
    #arg1 = sys.argv[1]
    # Define the folder containing the text files
    folder = 'C:\\Users\\porte\\OneDrive\\Jupyter Notebooks\\Wall Panels'
    # folder = selected_folder_path

    #Define the pdf names to be used
    sched = folder + '\\Schedule.pdf'
    panels = folder + '\\Rebar.pdf'
    sched_panels = folder + '\\Panel Schedule_Rebar.pdf'

    # Iterate through the text files in the folder
    for file in os.listdir(folder):
        if file.endswith('.tup'):

            # Set Panel type to the name of the .tup file
            item_dict['PanelType']=file.replace('.tup', '')

            # Read in the file
            with open(folder + "\\" + file, 'r') as f:
                lines = f.readlines()
            # Loop through each line in the file
            for line in lines:
                # Loop through each item in the items list
                for item in items:
                    # Check if the item is in the line
                    if line.startswith(f"{item}"):
                        try:
                            # Extract the value from the line
                            value = str(line.split("=")[1].strip()).replace(" ft", "").replace(" in", "")
                            if value.startswith('C'):
                                value = value.split("-")[0].strip().replace("C ", "")
                            # Append the value to the dictionary with a semicolon separator
                            if str(item_dict[item]) == 'nan':
                                item_dict[item] = value
                            else:
                                item_dict[item] = str(item_dict[item]) + ';' + value
                            break
                        except:
                            # If the item is not in the line, append None to the dictionary
                            item_dict[item] = None

            df1 = pd.DataFrame.from_dict([item_dict])
            df = pd.concat([df, df1], ignore_index=True)
            for key in item_dict:
                item_dict[key] = np.nan

    # Change Material to psi and thickness add inches
    df['PanelMaterial'] = df['PanelMaterial'] + '000 psi'
    df['PanelThickness'] = df['PanelThickness'] + ' inches'
    df['Tfc'] = 'T=' + df['PanelThickness'] + '/f\'c=' + df['PanelMaterial']
    
    return [items, df, sched, panels, sched_panels]

# %%
# def on_row_select(event):
#     selected_row = treeview.focus()
#     selected_column = treeview.identify_column(event.x)
#     if selected_row:
#         if selected_column == "#1" or selected_column == "#2":
#             t_num = treeview.item(selected_row)['values'][2]
#             current_value = treeview.set(selected_row, column=selected_column)
#             new_value = "X" if current_value != "X" else ""
#             treeview.set(selected_row, column=selected_column, value=new_value)
#             test = df.loc[df['PanelType']== t_num].index.values.astype(int)[0]
#             data = df.iloc[test]
#             match selected_column:
#                 case '#1':
#                     generate_graph(data, ax1, canvas1)
#                 case '#2':
#                     generate_graph(data, ax2, canvas2)
#             # Clear values in the rest of the column
#             for item in treeview.get_children():
#                 if item != selected_row:
#                     treeview.set(item, column=selected_column, value="")
            
            
# %%
def panel_geom(pnl_data, p_fig):
    # Prep the panel outline XY points to use rectangle patch and add to figure
    xp = 0
    wp = float(pnl_data['PanelLength'])
    yp = -float(pnl_data['BottomPanelHeight'])
    hp = -yp + float(pnl_data['ParapetHeight']) + float(pnl_data['PanelHeight'])
    panel_out = Rectangle((xp,yp), wp, hp, edgecolor = 'black', fill=False, lw=5)
    p_fig.add_patch(panel_out)

    # Plot the openings on both graphs based on what is provided in the Openings section of the dataframe
    i_open = int(pnl_data['Openings'].split(';')[0])
    for i in range(0, i_open*5, 5):
        if i_open == 0:
            continue
        # for i opening, get reference corner, x/y, width, height. Then use the reference to adjust the x/y values and plot with color and dashed

        refer = int(pnl_data['Openings'].split(';')[1+i])
        x = float(pnl_data['Openings'].split(';')[2+i])
        y = float(pnl_data['Openings'].split(';')[3+i])
        w = float(pnl_data['Openings'].split(';')[4+i])
        h = float(pnl_data['Openings'].split(';')[5+i])

        match refer:
            case 1:  # Lower Right Corner
                x = wp - x
                w = -w
            case 2:  # Upper left corner
                h = -h
                y = float(pnl_data['PanelHeight']) - y
            case 3:  # Upper right corner
                x = wp - x
                w = -w
                h = -h
                y = float(pnl_data['PanelHeight']) - y
            case _:  # Lower left corner
                x = x
                y = y

        p_fig.add_patch(Rectangle((x,y), w, h, edgecolor = 'blue', fill=False, lw=2, ls='--'))
        
        
def plot_verticals(v_data, v_fig, l_size=10, f_size=12):
    panel_geom(v_data, v_fig)

    # Plot Vertical and Horizontal Rebar
    x_values = set()
    y_values = set()
    y_values.add(0)
    # Get the XY values of the rectangles in order to find the strip locations
    for patch in v_fig.patches:
        if isinstance(patch, plt.Rectangle):
            x_values.add(round(patch.get_x(), 2))
            x_values.add(round(patch.get_x() + patch.get_width(), 2))
            y_values.add(round(patch.get_y(), 2))
            y_values.add(round(patch.get_y() + patch.get_height(), 2))
    x_values = list(x_values)
    y_values = list(y_values)
    x_values.sort()
    y_values.sort()
    if y_values[0]==0:
        h_offset = 0
    else:
        h_offset = 1
        
    # Section for Vertical rebar
    n = int(v_data['DataVBarsCount'])
    if n != 0:
        # Split the string into a list
        parts = str(v_data['DataVBarsVBars']).split(';')
        groups = [parts[i:i+n] for i in range(0, len(parts), n)]
        output_list = [[] for _ in range(n)]

        #strip, bar qty, bar size, level, spacing, end1, end2
        for i, item in enumerate(parts):
            output_list[i % n].append(float(item))

        for i in range(0, n):
            rebar = output_list[i]
            x = (x_values[int(rebar[0])+1] - x_values[int(rebar[0])])/2 + x_values[int(rebar[0])]
            r_size = int(rebar[2])+2
            r_area = r_areas(rebar)
            line = v_fig.plot([x,x],[rebar[5],rebar[6]], ls='-', label=f'({int(rebar[1])}) #{r_size} @ {round(rebar[4]*12)} in {r_area}')
            xdata, ydata = line[0].get_data()
            v_fig.annotate('',xy=(x_values[int(rebar[0])+1], mean(ydata)), xytext=(x_values[int(rebar[0])], mean(ydata)), arrowprops=dict(color=line[0].get_color(),arrowstyle='|-|'))
            v_fig.annotate(line[0].get_label().replace('@','\n@'), xy=(xdata[0], mean(ydata)), rotation=90, fontsize = f_size, ha='center', va='center', bbox=dict(facecolor='white', edgecolor=line[0].get_color()))

        v_fig.legend(loc=9, ncols=5, fontsize=l_size)
        
        
def plot_horizontals(h_data, h_fig, l_size=10, f_size=12):
    panel_geom(h_data, h_fig)
    
    # Plot Vertical and Horizontal Rebar
    x_values = set()
    y_values = set()
    y_values.add(0)
    # Get the XY values of the rectangles in order to find the strip locations
    for patch in h_fig.patches:
        if isinstance(patch, plt.Rectangle):
            x_values.add(round(patch.get_x(), 2))
            x_values.add(round(patch.get_x() + patch.get_width(), 2))
            y_values.add(round(patch.get_y(), 2))
            y_values.add(round(patch.get_y() + patch.get_height(), 2))
    x_values = list(x_values)
    y_values = list(y_values)
    x_values.sort()
    y_values.sort()
    if y_values[0]==0:
        h_offset = 0
    else:
        h_offset = 1
        
    # Section for Horizontal rebar
    n = int(h_data['DataHBarsCount'])
    if n != 0:
        # Split the string into a list
        parts = str(h_data['DataHBarsHBars']).split(';')
        groups = [parts[i:i+n] for i in range(0, len(parts), n)]
        output_list = [[] for _ in range(n)]

        #Qty, rebar size, Layer, Spacing, Closed, Axis(starting vertical strip), Distance1 (useless), Distance2(length), horizontal strip
        for i, item in enumerate(parts):
            output_list[i % n].append(float(item))

        for i in range(0, len(output_list)):
            rebar = output_list[i]
            x1 = x_values[int(rebar[5])]
            x2 = x1+rebar[7]
            y1 = y_values[int(rebar[8])+h_offset]
            y2 = y_values[int(rebar[8])+h_offset+1]
            y = mean([y1, y2])
            r_size = int(rebar[1])+2
            match (x2-x1):
                case _ if (x2-x1) <= 4:
                    h_label = f'#3 Ties @7 in'
                case _:
                    h_label = f'({int(rebar[0])}) #{r_size} @ {round(rebar[3]*12)} in {r_areas(rebar)}'

            line = h_fig.plot([x1,x2],[y,y], ls='-', label=h_label)
            if f'#{4} @ {18} in' not in h_label:
                xdata, ydata = line[0].get_data()
                h_fig.annotate('',xy=(mean([x1,x2]), y1), xytext=(mean([x1,x2]), y2), arrowprops=dict(color=line[0].get_color(),arrowstyle='|-|'))
                h_fig.annotate(line[0].get_label().replace('@','\n@'), xy=(mean([x1,x2]), y), fontsize = f_size, ha='center', va='center', bbox=dict(facecolor='white', edgecolor=line[0].get_color()))

        h_fig.legend(loc=9, ncols=5, fontsize=l_size)

        
def r_areas(rbr):
    if rbrcheck_var.get() == 1:
        rebar_areas = {
            2: 0.05,
            3: 0.11,
            4: 0.2,
            5: 0.31,
            6: 0.44,
            7: 0.6,
            8: 0.79,
            9: 1.00,
            10: 1.27
        }  
        r_sze = int(rbr[2])+2
        reb_area = f'\n({round(int(rbr[1])*rebar_areas[r_sze],2)} in2)'
    else:
        reb_area = ''
    return reb_area

# %%
# Function to extract numerical portion from a string
def extract_numerical_part(s):
    # Remove characters after the third character
    truncated_str = s[:3]
    # Use regular expression to find the numerical part
    match = re.search(r'T(\d+)', truncated_str)
    if match:
        return int(match.group(1))
    else:
        return 0
        
# Function to sort the Treeview by column 2 in natural sorting order
def sort_treeview(treeview):
    items = list(treeview.get_children())  # Convert tuple to list
    items.sort(key=lambda item: extract_numerical_part(treeview.item(item)['values'][2]))
    for index, item in enumerate(items):
        treeview.move(item, '', index)


# %%

# %%
# if viewcheck_var.get() == 1:
#     # Specify the columns to include and their order
#     columns_to_use = [df.columns[i] for i in [0, 5, 6, 1, 2, 3, 4]]
#     check_columns = ['Panel1', 'Panel2']
    
#     # Create the main window
#     root = tk.Tk()
#     root.title("DataFrame Viewer")

#     # Create a Treeview widget to display the DataFrame
#     treeview = ttk.Treeview(root)
#     treeview['columns'] = tuple(check_columns + columns_to_use)  # Use the specified columns
#     for col in (check_columns + columns_to_use):
#         treeview.heading(col, text=col)

#     treeview.column("#0", width=0, stretch=tk.NO)  # Hide the default first column
#     treeview.column("#1", width=75, stretch=tk.NO)
#     treeview.column("#2", width=75, stretch=tk.NO)
# #     # Insert DataFrame rows into the Treeview, using the specified columns and order
#     for _, row in df.iterrows():
#         # Create a list to hold the checkbox values for each checkbox column
#         values = ["", ""] + [row[col] for col in columns_to_use]
#         tagged = 'oddrow' if (_%2)==0 else 'evenrow'
#         # Insert the row values, including the checkbox values, into the Treeview
#         treeview.insert("", tk.END, values=values, tags = tagged)


#     treeview.tag_configure('oddrow', background='snow')
#     treeview.tag_configure('evenrow', background='SkyBlue1')
#     treeview.pack(fill=tk.BOTH, expand=True)

#     # Bind the row selection event to the on_row_select function
#     treeview.bind("<ButtonRelease-1>", on_row_select)

#     # # Create a Figure and Axes to display the graph
#     # fig, ax = plt.subplots(figsize=(2, 6))
#     # canvas = FigureCanvasTkAgg(fig, master=root)
#     # canvas.get_tk_widget().pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)
    
#     # Create the Figure and Axes for the first graph
#     fig1, ax1 = plt.subplots(figsize=(6, 4))
#     canvas1 = FigureCanvasTkAgg(fig1, master=root)
#     canvas1.get_tk_widget().pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

#     # Create the Figure and Axes for the second graph
#     fig2, ax2 = plt.subplots(figsize=(6, 4))
#     canvas2 = FigureCanvasTkAgg(fig2, master=root)
#     canvas2.get_tk_widget().pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    
#     # Add checkbox for rebar area for toggle purposes
#     check_button1 = tk.Checkbutton(root, text="Rebar Area", variable=rbrcheck_var, command=update_area)
#     check_button1.pack(anchor=tk.W)
#     # Update the initial checkbox state based on the existing variable
#     if rbrcheck_var.get() == 1:
#         check_button1.select()
#     else:
#         check_button1.deselect()
#     # Close button function
#     def close_window():
#         pdfcheck_var.set(1)
#         root.destroy()

#     # Create the close button
#     close_button = tk.Button(root, text="Print PDF",bg = 'azure', fg = 'red4', command=close_window)
#     close_button.pack()

#     root.mainloop()

# %%
# Define a custom sort key function to extract the numeric part of the 'T' strings
def sort_key(s):
    match = re.search(r'\d+', s)
    if match:
        return int(match.group())
    else:
        return 0
        
def chunk_df():

    # Sort the dataframe by the 'T' column using the custom sort key function
    dfl = df.iloc[df['PanelType'].map(sort_key).argsort()].reset_index(drop=True)

    # Split the dataframe into chunks of 6 rows each
    dfs = [df[i:i+graphs] for i in range(0, len(df), graphs)]
    return [dfl, dfs]

def _draw_as_table(df, pagesize):
    alternating_colors = [['white'] * len(df.columns), ['lightgray'] * len(df.columns)] * len(df)
    alternating_colors = alternating_colors[:len(df)]
    fig, ax = plt.subplots(figsize=pagesize)
    ax.axis('tight')
    ax.axis('off')
    the_table = ax.table(cellText=df.values,
                        rowLabels=df.index,
                        colLabels=df.columns,
                        rowColours=['lightblue']*len(df),
                        colColours=['lightblue']*len(df.columns),
                        cellColours=alternating_colors,
                        loc='center')
    the_table.auto_set_column_width(col=list(range(len(df.columns)))) # Provide integer list of columns to adjust
    return fig
  

def dataframe_to_pdf(df, filename, numpages=(1, 1), pagesize=(11, 8.5)):
  with PdfPages(filename) as pdf:
    nh, nv = numpages
    rows_per_page = len(df) // nh
    cols_per_page = len(df.columns) // nv
    for i in range(0, nh):
        for j in range(0, nv):
            page = df.iloc[(i*rows_per_page):min((i+1)*rows_per_page, len(df)),
                           (j*cols_per_page):min((j+1)*cols_per_page, len(df.columns))]
            fig = _draw_as_table(page, pagesize)
            if nh > 1 or nv > 1:
                # Add a part/page number at bottom-center of page
                fig.text(0.5, 0.5/pagesize[0],
                         "Part-{}x{}: Page-{}".format(i+1, j+1, i*nv + j + 1),
                         ha='center', fontsize=8)
            pdf.savefig(fig, bbox_inches='tight')
            plt.close()

# %%
items, df, sched, panels, sched_panels = reading_tup()
# Define number of graphs per page
graphs = 6
df, dfs = chunk_df()