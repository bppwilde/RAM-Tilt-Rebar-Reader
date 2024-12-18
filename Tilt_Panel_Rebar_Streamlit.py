import altair as alt
import numpy as np
import pandas as pd
import streamlit as st
import tkinter as tk
from tkinter import filedialog
from tkinter import ttk
from tkinter import messagebox
# %% Tkinter form to find folder path
def browse_folder():
    folder_path = filedialog.askdirectory()
    if folder_path:
        folder_var.set(folder_path)

def ok_button():
    root.destroy()

root = tk.Tk()
root.title("Folder Directory Browser")

# create a checkbox variable
rbrcheck_var = tk.IntVar()
viewcheck_var = tk.IntVar()
pdfcheck_var = tk.IntVar()

# create a checkbox
checkbox = tk.Checkbutton(root, text="Show Rebar Area", variable=rbrcheck_var)
checkbox.pack()

# create a checkbox
checkbox = tk.Checkbutton(root, text="Show Rebar Viewer", variable=viewcheck_var)
checkbox.pack()

# create a checkbox
checkbox = tk.Checkbutton(root, text="Print rebar to PDF", variable=pdfcheck_var)
checkbox.pack()

# create a label to display the selected folder path
folder_var = tk.StringVar()
folder_label = tk.Label(root, textvariable=folder_var, width=50)
folder_label.pack()

# add a button to browse folders
browse_button = tk.Button(root, text="Browse", command=browse_folder)
browse_button.pack()

# add an "OK" button to close the dialog
ok_button = tk.Button(root, text="OK", command=ok_button)
ok_button.pack()

root.mainloop()

# get the selected folder path after the window is closed
selected_folder_path = folder_var.get()

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
