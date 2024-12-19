#%%Import libraries
import altair as alt
import numpy as np
import pandas as pd
import streamlit as st
import os
import io
import matplotlib.pyplot as plt
#%% Test Plot
def test_plot(x, s_title):
    st.title(f"Matplotlib Plot #{x}")
    st.header(f"Line = {s_title}")
    fig, ax = plt.subplots()
    ax.plot([1, 2, 3, 4, 5])
    ax.set_xlabel("X-axis")
    ax.set_ylabel("Y-axis")
    ax.set_title("Simple Line Plot")

    st.pyplot(fig)

#%% File uploader, that accepts only tup files. Other files can be uploaded but only the tup files will be accepted.
accepted_ftype = ['tup']
st.title("Folder Upload System")

uploaded_files = st.file_uploader("Choose files from a folder", accept_multiple_files=True, type=accepted_ftype)

# Define a list of items to look for in each line
items = ['PanelType', 'ParapetHeight', 'BottomPanelHeight', 'PanelHeight', 'PanelLength', 'PanelThickness', 'PanelMaterial', 'Openings', 'DataVBarsCount', 'DataVBarsVBars','DataHBarsCount', 'DataHBarsHBars']

# Initialize an empty dictionary for each item
item_dict = {key: np.nan for key in items}

# Define a blank Dataframe with the column names
df = pd.DataFrame(columns = items)

if uploaded_files:
    # Create a temporary directory to store uploaded files
    temp_dir = "temp_wall_files"
    os.makedirs(temp_dir, exist_ok=True)
    i = 0
    for file in uploaded_files:
        if file.name.endswith('.tup'):
            # Set Panel type to the name of the .tup file
            item_dict['PanelType']=file.name.replace('.tup', '')

            # Read all lines in the file
            lines = file.read().decode('utf-8', errors='replace')
            # lines = file.read().decode('utf-8')
            st.header(f"First line = {lines[0]}")
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
    
    
    st.success(f"Files uploaded successfully to {temp_dir} folder.")

    st.write(f"Number of files: {len(uploaded_files)}")
    
    #Display the dataframe from reading the tup files for testing purposes
    st.dataframe(df)

