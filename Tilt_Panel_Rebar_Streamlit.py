#%%Import libraries
import altair as alt
import numpy as np
import pandas as pd
import streamlit as st
import os


#%% File uploader, that accepts only tup files. Other files can be uploaded but only the tup files will be accepted.
accepted_ftype = ['tup']
st.title("Folder Upload System")

uploaded_files = st.file_uploader("Choose files from a folder", accept_multiple_files=True, type=accepted_ftype)

if uploaded_files:
    st.write("Uploaded files:")
    for file in uploaded_files:
        st.write(f"- {file.name}")
    
    # Create a temporary directory to store uploaded files
    temp_dir = "temp wall files."
    os.makedirs(temp_dir, exist_ok=True)
    
    for file in uploaded_files:
        file_path = os.path.join(temp_dir, file.name)
        with open(file_path, "wb") as f:
            f.write(file.getbuffer())
    
    st.success(f"Files uploaded successfully to {temp_dir}")

    st.write(f"Number of files: {len(uploaded_files)}")
#%%

"""
# Welcome to Streamlit!

Edit `/streamlit_app.py` to customize this app to your heart's desire :heart:.
If you have any questions, checkout our [documentation](https://docs.streamlit.io) and [community
forums](https://discuss.streamlit.io).

In the meantime, below is an example of what you can do with just a few lines of code:
"""

num_points = st.slider("Number of points in spiral", 1, 10000, 1100)
num_turns = st.slider("Number of turns in spiral", 1, 300, 31)

indices = np.linspace(0, 1, num_points)
theta = 2 * np.pi * num_turns * indices
radius = indices

x = radius * np.cos(theta)
y = radius * np.sin(theta)

df = pd.DataFrame({
    "x": x,
    "y": y,
    "idx": indices,
    "rand": np.random.randn(num_points),
})

st.altair_chart(alt.Chart(df, height=700, width=700)
    .mark_point(filled=True)
    .encode(
        x=alt.X("x", axis=None),
        y=alt.Y("y", axis=None),
        color=alt.Color("idx", legend=None, scale=alt.Scale()),
        size=alt.Size("rand", legend=None, scale=alt.Scale(range=[1, 150])),
    ))
