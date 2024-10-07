import cv2

def save_image_locally(image_data, save_path):
    """Saves the captured image locally to the specified path."""
    try:
        if image_data is not None:
            cv2.imwrite(save_path, image_data)
            print(f"Image successfully saved to {save_path}")
        else:
            print("No image data provided to save.")
    except Exception as e:
        print(f"Error saving image: {e}")
