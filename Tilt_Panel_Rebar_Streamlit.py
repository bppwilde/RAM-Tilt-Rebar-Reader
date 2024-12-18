#%%Import libraries
import altair as alt
import numpy as np
import pandas as pd
import streamlit as st
import os
import matplotlib.pyplot as plt

#%% File uploader, that accepts only tup files. Other files can be uploaded but only the tup files will be accepted.
accepted_ftype = ['tup']
st.title("Folder Upload System")

uploaded_files = st.file_uploader("Choose files from a folder", accept_multiple_files=True, type=accepted_ftype)

if uploaded_files:
    st.write("Uploaded files:")
    for file in uploaded_files:
        st.write(f"- {file.name}")
    
    # Create a temporary directory to store uploaded files
    temp_dir = "temp_wall_files"
    os.makedirs(temp_dir, exist_ok=True)
    
    for file in uploaded_files:
        first_line = file.readline().decode('utf-8').strip()
        st.write(f"First line of {file.name}: {first_line}")
        first_line = file.readline().decode('utf-8').strip()
        st.write(f"First line of {file.name}: {first_line}")

        file_path = os.path.join(temp_dir, file.name)
        with open(file_path, "wb") as f:
            f.write(file.getbuffer())
    
    st.success(f"Files uploaded successfully to {temp_dir} folder.")

    st.write(f"Number of files: {len(uploaded_files)}")
#%% Test Plot
st.title("Matplotlib Plot in Streamlit")

fig, ax = plt.subplots()
ax.plot([1, 2, 3, 4, 5])
ax.set_xlabel("X-axis")
ax.set_ylabel("Y-axis")
ax.set_title("Simple Line Plot")

st.pyplot(fig)
