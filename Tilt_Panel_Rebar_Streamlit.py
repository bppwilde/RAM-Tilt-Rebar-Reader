#%%Import libraries
import altair as alt
import numpy as np
import pandas as pd
import streamlit as st
import os
import io
import tempfile
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
#from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from statistics import mean

#%% Overall Panel geometry generation
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

#%% Rebar areas
def r_areas(rbr):
    rbrcheck_var = 0
    if rbrcheck_var == 1:
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


#%% How to plot the vertical rebar
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


#%% How to plot horizontal rebar
def plot_horizontals(h_data, h_fig,  f_size=12):
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

#%% File uploader, that accepts only tup files. Other files can be uploaded but only the tup files will be accepted.
accepted_ftype = ['tup']
folder_title = st.title("Upload RAM files:")

placeholder = st.empty()

with placeholder:
    uploaded_files = st.file_uploader("Choose files from a folder", accept_multiple_files=True, type=accepted_ftype)

# Define a list of items to look for in each line
items = ['PanelType', 'ParapetHeight', 'BottomPanelHeight', 'PanelHeight', 'PanelLength', 'PanelThickness', 'PanelMaterial', 'Openings', 'DataVBarsCount', 'DataVBarsVBars','DataHBarsCount', 'DataHBarsHBars']

# Create an alias for st.session_state
ss = st.session_state

# Initialize session state variables if they don't exist
if 'item_dict' not in ss:
    ss.item_dict = {}
if 'df' not in ss:
    ss.df = pd.DataFrame()

folder_title = st.title("Upload RAM files:")

placeholder = st.empty()

with placeholder:
    uploaded_files = st.file_uploader("Choose files from a folder", accept_multiple_files=True, type=accepted_ftype)

# Define a list of items to look for in each line
items = ['PanelType', 'ParapetHeight', 'BottomPanelHeight', 'PanelHeight', 'PanelLength', 'PanelThickness', 'PanelMaterial', 'Openings', 'DataVBarsCount', 'DataVBarsVBars','DataHBarsCount', 'DataHBarsHBars']

if uploaded_files:
    # Create a unique temporary directory for the session
    temp_dir = tempfile.mkdtemp(prefix="temp_wall_files_")

    # Process each uploaded file
    for file in uploaded_files:
        # Save the uploaded file to the temporary directory
        file_path = os.path.join(temp_dir, file.name)
        with open(file_path, "wb") as f:
            f.write(file.getbuffer())

        # Your existing code to process the file
        if file.name.endswith('.tup'):
            # Set Panel type to the name of the .tup file
            ss.item_dict['PanelType'] = file.name.replace('.tup', '')

            # Read all lines in the file
            for encoded_line in file:
                line = encoded_line.decode("utf-8", errors="replace").strip()
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
                            if str(ss.item_dict[item]) == 'nan':
                                ss.item_dict[item] = value
                            else:
                                ss.item_dict[item] = str(ss.item_dict[item]) + ';' + value
                            break
                        except:
                            # If the item is not in the line, append None to the dictionary
                            ss.item_dict[item] = None

            df1 = pd.DataFrame.from_dict([ss.item_dict])
            ss.df = pd.concat([ss.df, df1], ignore_index=True)
            for key in ss.item_dict:
                ss.item_dict[key] = np.nan

    # Change Material to psi and thickness add inches
    ss.df['PanelMaterial'] = ss.df['PanelMaterial'] + '000 psi'
    ss.df['PanelThickness'] = ss.df['PanelThickness'] + ' inches'
    ss.df['Tfc'] = 'T=' + ss.df['PanelThickness'] + '/f\'c=' + ss.df['PanelMaterial']

    st.success(f"Files uploaded successfully.")

    status_text = st.empty()
    status_text.text(f"Waiting to process files: {0} of {len(ss.df)}")
    progress_bar = st.progress(0)

    # Display the dataframe from reading the tup files for testing purposes
    selected_columns = ['PanelType', 'PanelThickness', 'PanelMaterial']
    st.header('Panel Schedule')
    # Calculate the height based on the number of rows in the dataframe
    df_height = (len(ss.df) + 1) * 35 + 3  # Adjust the multiplier as needed for your specific case

    # Display the dataframe with the calculated height
    st.dataframe(ss.df[selected_columns], height=df_height)

    for index, row in ss.df.iterrows():

        # Plot the graph on the appropriate subplot by splitting the subfigure into Vertical and Horizontal rebar graphs
        fig, (verts, horzs) = plt.subplots(1, 2, figsize=(16, 14))

        # Use the modules to generate the graphs for verticals and horizontals
        plot_verticals(row, verts, f_size=11)
        plot_horizontals(row, horzs, f_size=11)
        # Set titles
        xp = 0
        wp = float(row['PanelLength'])
        yp = -float(row['BottomPanelHeight'])
        hp = -yp + float(row['ParapetHeight']) + float(row['PanelHeight'])
        panel_out = Rectangle((xp,yp), wp, hp, edgecolor = 'black', fill=False, lw=5)
        # Place the legend between the title and the plot
        legend_params = {
            'loc': 9,
            'bbox_to_anchor': (0.5, 1.1),
            'ncol': 4,
            'fancybox': True,
            'shadow': False,
            'fontsize':10
        }
        verts.legend(**legend_params)
        horzs.legend(**legend_params)

        tx = panel_out.get_x() + panel_out.get_width()
        ty = panel_out.get_y() + panel_out.get_height()
        fig.suptitle(f"{row['PanelType']}, {row['Tfc']}", fontsize=24)
        verts.set_title(f"Vertical Rebar (L={tx:.3f} ft, T/wall={ty:.3f} ft)", fontsize=14)
        horzs.set_title("Horizontal Rebar", fontsize=14)
        # plt.tight_layout()
        st.pyplot(fig)

        # Update the progress bar and status message
        progress = (index + 1) / len(ss.df)
        progress_bar.progress(progress)
        status_text.text(f"Processing file {index+1} of {len(ss.df)}")

     # Clear the status message when done
    status_text.empty()
    progress_bar.empty()
    folder_title.empty()
