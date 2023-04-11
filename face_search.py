import os
import ast
import sqlite3
import argparse
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk, ImageDraw

num_columns = 5
display_results = 15
offset = 0

def find_files_with_name(database, name):                                                                                           
    with sqlite3.connect(database) as connection:                                                                                   
        cursor = connection.cursor()                                                                                                
        cursor.execute("SELECT filename, people, boxes FROM image_data WHERE people LIKE ? LIMIT ? OFFSET ?",                       
            (f"%{name}%", display_results, offset))                                                                      
    result = cursor.fetchall()                                                                                                  
    parsed_result = []                                                                                                              
    for row in result:                                                                                                              
        filename, people_str, boxes_str = row                                                                                       
        people = ast.literal_eval(people_str) if people_str else None                                                               
        boxes = ast.literal_eval(boxes_str) if boxes_str else None
#        print("boxes", boxes)
        parsed_result.append((filename, people, boxes))                                                                             
    return parsed_result

def open_image(filepath, names=None, bboxes=None):
    image_window = tk.Toplevel()
    image_window.title(filepath)
    image = Image.open(filepath)
    print(f"Opening image {filepath} of {names} at {bboxes}.")
    if all((enable_bbox, names, bboxes)):
        draw = ImageDraw.Draw(image)
        for i, bbox in enumerate(bboxes):
            top, left, bottom, right = bbox
            draw.rectangle(((left, top), (right, bottom)), outline="blue", width=3)
            draw.text((left, bottom + 5), names[i], fill="blue")  
    photo = ImageTk.PhotoImage(image)
    image_label = ttk.Label(image_window, image=photo)
    image_label.image = photo
    image_label.pack()

def search_images():
    name = name_entry.get().strip()
    print(f"Searching first {display_results} results for {name} offset by {offset}...")
    thumbnails = find_files_with_name(database, name)
    display_thumbnails(thumbnails)

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

def display_thumbnails(thumbnails):
    for child in thumbnail_frame.winfo_children():
        child.destroy()
    thumbnail_size = (100, 100)
    for i, thumbnail in enumerate(thumbnails):
        filepath, names, bboxes = thumbnail
        print("image",filepath, names, bboxes)
        image = Image.open(filepath)
        image.thumbnail(thumbnail_size)
        photo = ImageTk.PhotoImage(image)
        label = ttk.Label(thumbnail_frame, image=photo)
        label.image = photo

        row = i // num_columns
        col = i % num_columns
        
        label.grid(row=row, column=col, padx=5, pady=5)
        label.bind("<Button-1>", lambda e, path=filepath, names=names, bboxes=bboxes: open_image(path, names=names, bboxes=bboxes))


parser = argparse.ArgumentParser(description="Face Database GUI")
parser.add_argument('--database', default='faces.db', help='Database file name')
args = parser.parse_args()
database = args.database

root = tk.Tk()
root.title("Face Search")

main_frame = ttk.Frame(root, padding=10)
main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

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

enable_bbox = tk.BooleanVar(value=False)
bbox_button = ttk.Checkbutton(main_frame, text="Bbox", variable=enable_bbox)
bbox_button.grid(row=0, column=5, padx=(5, 0), pady=(0, 5))

canvas = tk.Canvas(root)
canvas.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

thumbnail_frame = ttk.Frame(canvas)
canvas.create_window((0, 0), window=thumbnail_frame, anchor="nw")

root.mainloop()
