#!/bin/env python3
import os
import glob
import sqlite3
import argparse
import itertools
import multiprocessing
from hashlib import blake2b
from PIL import Image
import face_recognition


EXTENSIONS = ('*.jpg', '*.JPG')
def get_files(folder):
    def glob_map(pattern):
        return glob.iglob(os.path.join(folder, pattern))
    return itertools.chain.from_iterable(glob_map(ext) for ext in EXTENSIONS)

def detect_faces(f, known_face_names, known_face_encodings):
    with sqlite3.connect(database) as connection:
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM image_data WHERE filename = ?", (f,))
        res = cursor.fetchone()
        if res is not None:
            print(f"Skipping {f}...")
            return
    input_image = face_recognition.load_image_file(f)
    input_image_encodings = face_recognition.face_encodings(input_image)
    face_locations = face_recognition.face_locations(input_image)
    face_names = []
    print(f"Processing file '{f}', found {len(face_locations)} possible faces.")
    for encoding, location in zip(input_image_encodings, face_locations):
        matches = face_recognition.compare_faces(known_face_encodings, encoding)
        if any(matches):
            first_match_index = matches.index(True)
            face_names.append(known_face_names[first_match_index])
        else:
            name = "Unknown_" + blake2b(str(encoding).encode('utf-8')).hexdigest()[:15]
            known_face_names.append(name)
            face_names.append(name)
            top, right, bottom, left = location
            width = right - left
            height = bottom - top
            top = max(0, top - int(0.3 * height))
            left = max(0, left - int(0.3 * width))
            bottom = min(input_image.shape[0], bottom + int(0.3 * height))
            right = min(input_image.shape[1], right + int(0.3 * width))
            face_image = input_image[top:bottom, left:right]
            pil_image = Image.fromarray(face_image)
            output_file_path = os.path.join(output_folder, name + ".jpg")
            pil_image.save(output_file_path)
        with sqlite3.connect(database, isolation_level=None) as connection:
            cursor = connection.cursor()
            cursor.execute("INSERT INTO image_data (filename, people, boxes) VALUES (?, ?, ?)",
                       (f, str(face_names), str(face_locations)))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Face Detection Program')
    parser.add_argument('--known_folder', default='./known/', help='Known faces folder path')
    parser.add_argument('--unknown_folder', default='./unknown/', help='Unknown faces folder path')
    parser.add_argument('--output_folder', default='./detected/', help='Output folder path')
    parser.add_argument('--database', default='faces.db', help='Database file name')
    parser.add_argument('--cpus', default=6, type=int, help='Number of threads to use')
    args = parser.parse_args()
    known_folder = args.known_folder
    unknown_folder = args.unknown_folder
    output_folder = args.output_folder
    database = args.database

    known_face_encodings = []
    known_face_names = []

    with sqlite3.connect(database) as connection:
        cursor = connection.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS image_data
            (id INTEGER PRIMARY KEY, filename TEXT, people TEXT, boxes TEXT)''')

    for f in get_files(known_folder):
        ref_image = face_recognition.load_image_file(f)
        ref_image_encoding = face_recognition.face_encodings(ref_image)[0]
        known_face_encodings.append(ref_image_encoding)
        known_face_names.append(os.path.splitext(os.path.basename(f))[0].split("_")[0].strip())

    print(f"Loaded {len(known_face_encodings)} faces.")

    kfe = multiprocessing.Manager().list(known_face_encodings)
    kfn = multiprocessing.Manager().list(known_face_names)
    with multiprocessing.Pool(processes=args.cpus) as pool:
        pool.starmap(detect_faces, [(f, kfn, kfe) for f in get_files(unknown_folder)])

