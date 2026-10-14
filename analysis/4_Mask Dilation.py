import cv2
import numpy as np
import tifffile as tifffile
import os

# Function to fill contours in a binary mask
def fill_contours(mask):
    # Get outer contours and draw filled ones as white on a black background
    contours = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contours = contours[0] if len(contours) == 2 else contours[1]
    result = np.zeros_like(mask)
    
    for contour in contours:
        cv2.drawContours(result, [contour], 0, 255, -1)
    
    result = np.array(result/result.max(), dtype=np.uint8)
    return result

# Function to calculate the area of a mask based on its outline
def calculate_mask_area(mask):
    # Calculate the area as the sum of all non-zero pixels in the mask
    area = np.sum(mask)
    return area

# Function to create masks dividing the area into thirds
def create_thirds_masks(nuclear_mask, cytoplasmic_mask):
    # Fill nuclear and cytoplasmic masks
    filled_nuclear_mask = fill_contours(nuclear_mask)
    filled_cytoplasmic_mask = fill_contours(cytoplasmic_mask)

    # Calculate the area of the filled nuclear mask
    nuclear_area = calculate_mask_area(filled_nuclear_mask)
    cytoplasmic_area = calculate_mask_area(filled_cytoplasmic_mask)
    print("The nuclear area is", nuclear_area)
    print("The cytoplasmic area is", cytoplasmic_area)
    
    calculated_cytoplasmic_area = cytoplasmic_area - nuclear_area
    
    print("The calculated cytoplasmic area is", calculated_cytoplasmic_area)

    # Calculate the target area for the 1/3 region
    first_third_target_area = calculated_cytoplasmic_area / 3
    second_thrid_target_area = first_third_target_area * 2

    # Initialize masks for the first and second thirds
    first_third_mask = np.zeros_like(nuclear_mask)
    second_third_mask = np.zeros_like(nuclear_mask)
    last_third_mask = np.zeros_like(nuclear_mask)
    
    # Create a kernel for dilation (adjust the kernel size as needed)
    kernel = np.ones((3, 3), np.uint8)
    
    # Dilation for first third
    dilated_nuclear_mask = filled_nuclear_mask.copy()
    while (calculate_mask_area(dilated_nuclear_mask) - nuclear_area) < first_third_target_area:
        # Dilation
        dilated_nuclear_mask = cv2.dilate(dilated_nuclear_mask, kernel, iterations=1)
        # Ensure the dilation is within the cytoplasmic bounds
        dilated_nuclear_mask = dilated_nuclear_mask * filled_cytoplasmic_mask
    # Remove the nucleus from the dilation mask
    first_third_mask = dilated_nuclear_mask - filled_nuclear_mask
    print("Final dilated mask area for 1/3 is", calculate_mask_area(first_third_mask))
    
    # Dilation for second third
    dilated_nuclear_mask = filled_nuclear_mask.copy()
    while (calculate_mask_area(dilated_nuclear_mask) - nuclear_area) < second_thrid_target_area:
        # Dilation
        dilated_nuclear_mask = cv2.dilate(dilated_nuclear_mask, kernel, iterations=1)
        # Ensure the dilation is within the cytoplasmic bounds
        dilated_nuclear_mask = dilated_nuclear_mask * filled_cytoplasmic_mask
    # Remove the nucleus and first dilation mask from the dilation mask
    second_third_mask = dilated_nuclear_mask - first_third_mask - filled_nuclear_mask
    print("Final dilated mask area for 2/3 is", calculate_mask_area(second_third_mask))
    # Get final mask by removing all components previously made from the cytoplasmic mask
    last_third_mask = filled_cytoplasmic_mask-first_third_mask-second_third_mask-filled_nuclear_mask
    
    return first_third_mask, second_third_mask, last_third_mask

# Function to process masks in a directory
def process_masks_in_directory(directory):
    # Iterate over files in the directory
    for filename in os.listdir(directory):
        if filename.endswith("_nuclear_mask.tif"):
            # Construct the corresponding cytoplasmic mask filename
            cytoplasmic_filename = filename.replace("_nuclear_mask.tif", "_cytoplasmic_mask.tif")

            # Check if the cytoplasmic mask file exists
            if os.path.isfile(os.path.join(directory, cytoplasmic_filename)):
                # Load nuclear and cytoplasmic masks as NumPy arrays
                nuclear_mask = tifffile.imread(os.path.join(directory, filename))
                cytoplasmic_mask = tifffile.imread(os.path.join(directory, cytoplasmic_filename))

                print(f"Processing: {filename} and {cytoplasmic_filename}")

                # Ensure masks are binary (0 and 1)
                nuclear_mask = (nuclear_mask > 0).astype(np.uint8)
                cytoplasmic_mask = (cytoplasmic_mask > 0).astype(np.uint8)

                # Create the third masks
                first_third_mask, second_third_mask, last_third_mask = create_thirds_masks(nuclear_mask, cytoplasmic_mask)

                # Save the thirds masks with appropriate names
                first_third_filename = filename.replace("_nuclear_mask.tif", "_first_third.tif")
                second_third_filename = filename.replace("_nuclear_mask.tif", "_second_third.tif")
                last_third_filename = filename.replace("_nuclear_mask.tif", "_last_third.tif")

                tifffile.imsave(os.path.join(directory, first_third_filename), first_third_mask.astype(np.uint8) * 255)
                tifffile.imsave(os.path.join(directory, second_third_filename), second_third_mask.astype(np.uint8) * 255)
                tifffile.imsave(os.path.join(directory, last_third_filename), last_third_mask.astype(np.uint8) * 255)

                print(f"Processed: {filename} and {cytoplasmic_filename}")
                print(f"Saved: {first_third_filename} and {second_third_filename} and {last_third_filename}")


if __name__ == "__main__":
    # Provide the directory where the masks are located
    directory = r"Z:\koch\SARS-CoV-2 Project\Imaging\Terminator Imaging\Rapid\Emi_NoStart\20260112\65msExp_20T_0I\Dish01"

    # Process the masks in the directory and save the third masks in the same directory
    process_masks_in_directory(directory)
