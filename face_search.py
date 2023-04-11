import os
import sqlite3
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk

num_columns = 5
display_results = 20
offset = 0

# Find files with name (from the previous answer)
def find_files_with_name(database, name):
    with sqlite3.connect(database) as connection:
        cursor = connection.cursor()
        cursor.execute("SELECT filename FROM image_data WHERE people LIKE ? LIMIT ? OFFSET ?",
                       (f"%{name}%", display_results, offset))
        result = cursor.fetchall()
    return [row[0] for row in result]

# Function to open the image with the default image viewer
def open_image(filepath):
    image_window = tk.Toplevel()
    image_window.title(filepath)
    image = Image.open(filepath)
    photo = ImageTk.PhotoImage(image)
    image_label = ttk.Label(image_window, image=photo)
    image_label.image = photo
    image_label.pack()

# Function to search for images with the entered name
def search_images():
    name = name_entry.get().strip()
    print(f"Searching first {display_results} results for {name} offset by {offset}...")
    filepaths = find_files_with_name(database, name)
    display_thumbnails(filepaths)

# Function to clear the search results
def reset_search():
    global offset
    offset = 0
    for child in thumbnail_frame.winfo_children():
        child.destroy()

def next_page():
    global offset
    offset += display_results
    search_images()
    
def prev_page():
    global offset
    offset = max(0, offset - display_results)
    search_images()

# Function to display the thumbnails
def display_thumbnails(filepaths):
    for child in thumbnail_frame.winfo_children():
        child.destroy()
    thumbnail_size = (100, 100)
    for i, filepath in enumerate(filepaths):
        print(filepath)
        image = Image.open(filepath)
        image.thumbnail(thumbnail_size)
        photo = ImageTk.PhotoImage(image)
        label = ttk.Label(thumbnail_frame, image=photo)
        label.image = photo

        row = i // num_columns
        col = i % num_columns
        
        label.grid(row=row, column=col, padx=5, pady=5)
        label.bind("<Button-1>", lambda e, path=filepath: open_image(path))

# GUI setup
database = 'faces.db'

root = tk.Tk()
root.title("Face Search")

main_frame = ttk.Frame(root, padding=10)
main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

# Entry and buttons
name_entry = ttk.Entry(main_frame)
name_entry.grid(row=0, column=0, padx=(0, 5), pady=(0, 5))

search_button = ttk.Button(main_frame, text="Search", command=search_images)
search_button.grid(row=0, column=1, padx=(5, 5), pady=(0, 5))

reset_button = ttk.Button(main_frame, text="Reset", command=reset_search)
reset_button.grid(row=0, column=2, padx=(5, 0), pady=(0, 5))

prev_button = ttk.Button(main_frame, text="Previous", command=prev_page)
prev_button.grid(row=0, column=3, padx=(5, 0), pady=(0, 5))

next_button = ttk.Button(main_frame, text="Next", command=next_page)
next_button.grid(row=0, column=4, padx=(5, 0), pady=(0, 5))

# Frame to display the thumbnails
canvas = tk.Canvas(root)
canvas.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
#scrollbar = ttk.Scrollbar(root, orient="vertical", command=canvas.yview)
#scrollbar.grid(row=1, column=2, sticky=(tk.N, tk.S))

#canvas.configure(yscrollcommand=scrollbar.set)
#canvas.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

thumbnail_frame = ttk.Frame(canvas)
canvas.create_window((0, 0), window=thumbnail_frame, anchor="nw")
#thumbnail_frame.grid(row=1, column=0, pady=(0, 10))

root.mainloop()
