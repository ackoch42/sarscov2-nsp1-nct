import napari
import numpy as np
from tifffile import imread, imsave
import os
import csv
from PIL import Image, ImageDraw

# Specify the directory containing tif files
tif_directory = r"Z:\koch\SARS-CoV-2 Project\Imaging\Terminator Imaging\Rapid\Emi_NoStart\20260112\65msExp_20T_0I\Dish01"

# Get a list of tif files in the directory
tif_files = [f for f in os.listdir(tif_directory) if f.endswith('.tif')]

def create_and_display_viewer(tif_file):
    # Load image: expected shape (t, z, c, x, y)
    img_path = os.path.join(tif_directory, tif_file)
    img = imread(img_path)

    if img.ndim != 5:
        raise ValueError(f"{tif_file} expected shape (t,z,c,x,y); got {img.shape}")

    t, z, c, x, y = img.shape

    # Directory for saving masks
    save_dir = os.path.dirname(os.path.abspath(img_path))

    viewer = napari.Viewer()

    # ---- Overview layer: max over t,z,c -> (x,y)
    overview = np.max(img, axis=(0, 1, 2))  # (x,y)
    viewer.add_image(overview, name='Image (overview)')

    # ---- Per-channel layers: max over t,z only -> (c,x,y), then add each (x,y)
    per_channel_max_tz = np.max(img, axis=(0, 1))  # (c, x, y)
    n_channels = per_channel_max_tz.shape[0]

    for c_idx in range(n_channels):
        ch_img = per_channel_max_tz[c_idx]  # (x,y)

        # Simple auto-contrast (you can adjust in UI as well)
        if np.any(ch_img):
            lo = float(np.percentile(ch_img, 1))
            hi = float(np.percentile(ch_img, 99.9))
            if hi <= lo:
                hi = lo + 1.0
            contrast_limits = [lo, hi]
        else:
            contrast_limits = [0.0, 1.0]

        viewer.add_image(
            ch_img,
            name=f'Channel {c_idx}',
            contrast_limits=contrast_limits,
            visible=False  # start hidden; toggle on if useful for nuclei
        )
    # Create a layer for the nuclear mask
    nuclear_mask_layer = viewer.add_shapes(name='Nuclear Mask')

    # Create a layer for the cytoplasmic mask
    cytoplasmic_mask_layer = viewer.add_shapes(name='Cytoplasmic Mask')

    # Function to create and save a mask
    def create_and_save_mask(layer, mask_filename):
        # Get the drawn shapes
        shapes = layer.data  # Access the data attribute of the layer

        # Save the shapes as a CSV file
        csv_filepath = os.path.join(save_dir, mask_filename + '.csv')
        with open(csv_filepath, 'w', newline='') as csvfile:
            csv_writer = csv.writer(csvfile)
            for shape in shapes:
                csv_writer.writerow(shape)  # Save each shape as a separate row
        print(f"Saved mask as {csv_filepath}")

        # Process the CSV file and generate result image
        polygon_data = read_csv_file(csv_filepath)
        result_image = draw_lines_between_points(polygon_data)

        # Save the result as a TIFF image in the same directory as the TIFF file
        result_image_filepath = os.path.join(save_dir, mask_filename + '.tif')
        result_im = Image.fromarray(result_image)
        result_im.save(result_image_filepath)

        print(f"Processed and saved result image as {result_image_filepath}")

    # Add keybindings to trigger the create_and_save_mask function
    viewer.bind_key(f'n', lambda e: create_and_save_mask(nuclear_mask_layer, tif_file[:-4] + '_nuclear_mask'))
    viewer.bind_key(f'c', lambda e: create_and_save_mask(cytoplasmic_mask_layer, tif_file[:-4] + '_cytoplasmic_mask'))

    # Display the viewer
    napari.run()

# Function to read CSV file
def read_csv_file(csv_file):
    with open(csv_file, 'r') as csvfile:
        csv_reader = csv.reader(csvfile)
        # Read the CSV data and convert it to a list of tuples
        polygon_data = []
        for row in csv_reader:
            # Extract numbers from the format "[x y]"
            for coord in row:
                values = [float(val.strip('[]')) for val in coord.split() if val.strip('[]')]
                polygon_data.extend(values)
    return polygon_data

# Function to draw lines between points
def draw_lines_between_points(polygon_data):
    # Create a blank 512x512 numpy array
    image = Image.new('L', (512, 512), 0)
    draw = ImageDraw.Draw(image)

    # Convert polygon_data to a list of tuples for easier iteration
    polygon_tuples = [(polygon_data[i], polygon_data[i + 1]) for i in range(0, len(polygon_data), 2)]

    # Draw lines between all points in the polygon
    for i in range(len(polygon_tuples) - 1):
        # Swap x and y values when drawing
        point1 = (int(min(max(polygon_tuples[i][1], 0), 511)), int(min(max(polygon_tuples[i][0], 0), 511)))
        point2 = (int(min(max(polygon_tuples[i + 1][1], 0), 511)), int(min(max(polygon_tuples[i + 1][0], 0), 511)))
        draw.line([point1, point2], fill=255, width=1)

    # Draw a line between the last and first points to close the polygon
    # Swap x and y values when drawing
    point1 = (int(min(max(polygon_tuples[-1][1], 0), 511)), int(min(max(polygon_tuples[-1][0], 0), 511)))
    point2 = (int(min(max(polygon_tuples[0][1], 0), 511)), int(min(max(polygon_tuples[0][0], 0), 511)))
    draw.line([point1, point2], fill=255, width=1)

    return np.array(image)

# Print the total number of TIFF files to process
print(f"Total TIFF files to process: {len(tif_files)}")

# Iterate over tif files and create a viewer for each
for idx, tif_file in enumerate(tif_files, start=1):
    print(f"Processing file {idx} of {len(tif_files)}: {tif_file}")
    create_and_display_viewer(tif_file)
