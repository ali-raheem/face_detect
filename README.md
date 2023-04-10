# face_detect
Run face recognition locally on photos using the `face_recognition` module.

## Features
* multithreading
* Detect multiple faces per image
* Crop unknown faces for easy labelling
* Skip previously processed images.
* Output to SQLite db.

## Usage
Put known faces cropped down in `known` folder. Filename should be the desired label (i.e. the person's name) anything after `_` ignored so multiple samples for each name possible.
Put images to process in `unknown` folder, I downsample to 1024x1024 for speed. I've had good results down to 256x256 depending on framing.


