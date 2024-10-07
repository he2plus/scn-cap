import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
from PIL import Image, ImageTk
import threading
import time
import cv2
from capture import capture_active_window, capture_scrolling_content, capture_region, capture_all_monitors, capture_fullscreen
import utils
import database
import logging
import sys
import pymongo
import gridfs
from pymongo import MongoClient
from io import BytesIO
import datetime
import os

# Setting up logging configuration
logging.basicConfig(
    level=logging.DEBUG,  # Set level to DEBUG to capture all types of logs
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("screen_capture_tool.log"),  # Log to a file
        logging.StreamHandler(sys.stdout) 
    ]
)

logger = logging.getLogger(__name__)

# Set up MongoDB and GridFS
def setup_mongodb():
    client = MongoClient('localhost:27017')
    db = client['my_database']
    fs = gridfs.GridFS(db)
    return fs, db

fs, db = setup_mongodb()

class ScreenCaptureApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Screen Capture Tool")
        self.root.geometry("600x400")  
        
        self.db = database.MetadataManager("captures.db")
        self.storage_option = None  # To store the user's choice of storage
        self.create_ui()
        logger.info("UI created successfully.")

    def create_ui(self):
        # Main frame
        self.main_frame = tk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Working Buddy Section
        self.working_frame = tk.LabelFrame(self.main_frame, text="Working Buddy", padx=10, pady=10)
        self.working_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.start_button = tk.Button(self.working_frame, text="Start Working", command=self.start_capturing)
        self.start_button.pack(pady=5)

        self.break_button = tk.Button(self.working_frame, text="Break Time", command=self.take_break)
        self.break_button.pack(pady=5)

        self.end_button = tk.Button(self.working_frame, text="Call It a Day!", command=self.end_day)
        self.end_button.pack(pady=5)

        # Storage Option Section
        self.storage_frame = tk.LabelFrame(self.main_frame, text="Storage Options", padx=10, pady=10)
        self.storage_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.choose_storage_button = tk.Button(self.storage_frame, text="Choose Storage Option", command=self.choose_storage_option)
        self.choose_storage_button.pack(pady=5)

        # Utilities Section
        self.utilities_frame = tk.LabelFrame(self.main_frame, text="Utilities", padx=10, pady=10)
        self.utilities_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.capture_region_button = tk.Button(self.utilities_frame, text="Capture Region", command=self.capture_region)
        self.capture_region_button.pack(pady=5)

        self.capture_all_monitors_button = tk.Button(self.utilities_frame, text="Capture All Monitors", command=self.capture_all_monitors)
        self.capture_all_monitors_button.pack(pady=5)

    def choose_storage_option(self):
        options = ["Locally (Hidden)", "MongoDB"]
        self.storage_option = simpledialog.askstring("Choose Storage", f"Where would you like to store screenshots?\nOptions: {', '.join(options)}")
        if self.storage_option not in options:
            messagebox.showerror("Error", "Invalid storage option selected.")
            self.storage_option = None
        else:
            logger.info(f"Storage option selected: {self.storage_option}")

    def start_capturing(self):
        if not self.storage_option:
            self.choose_storage_option()
            if not self.storage_option:
                return

        if self.storage_option == "Locally (Hidden)":
            self.capture_path = filedialog.askdirectory(title="Select Save Location")
            if not self.capture_path:
                messagebox.showerror("Error", "Please select a save location.")
                logger.error("No save location selected.")
                return

        self.is_capturing = True
        self.is_break = False
        self.capture_thread = threading.Thread(target=self.capture_loop)
        self.capture_thread.start()
        logger.info("Started capturing screenshots.")

    def capture_loop(self):
        while self.is_capturing:
            if not self.is_break:
                try:
                    screen = capture_fullscreen()
                    if screen is not None:
                        timestamp = time.strftime("%Y%m%d_%H%M%S")
                        if self.storage_option == "Locally (Hidden)":
                            save_path = f"{self.capture_path}/.{timestamp}.png"  # Hidden file
                            utils.save_image_locally(screen, save_path)
                            self.db.add_metadata(save_path, "Fullscreen")
                            logger.info(f"Captured fullscreen and saved at {save_path}")
                        elif self.storage_option == "MongoDB":
                            self.save_screenshot_to_mongodb(screen, timestamp)
                            logger.info(f"Captured fullscreen and saved to MongoDB")
                except Exception as e:
                    logger.error(f"Error capturing fullscreen: {e}")
            
            time.sleep(30)  # Capture interval

    def save_screenshot_to_mongodb(self, image, timestamp):
        """Convert the image to binary and store it in MongoDB."""
        img_io = BytesIO()
        img_io.seek(0)
        img_io.write(cv2.imencode('.png', image)[1].tobytes())
        img_io.seek(0)
        
        metadata = {
            "timestamp": timestamp,
            "description": "Fullscreen"
        }

        fs.put(img_io, filename=f"screenshot_{timestamp}.png", metadata=metadata)
        logger.info(f"Screenshot saved to MongoDB with metadata: {metadata}")

    def take_break(self):
        self.is_break = True
        logger.info("Break time initiated.")

    def resume_work(self):
        self.is_break = False
        logger.info("Resumed work after break.")

    def end_day(self):
        self.is_capturing = False
        if self.capture_thread.is_alive():
            self.capture_thread.join()
        self.db.close()
        messagebox.showinfo("Goodbye!", self.get_positive_message())
        logger.info("Workday ended.")

    def get_positive_message(self):
        messages = [
            "Great job today! Remember, every day is a fresh start!",
            "Keep smiling, and don't forget to take a break!",
            "The best way to predict the future is to create it.",
            "You did great today! Enjoy your evening!"
        ]
        logger.debug("Positive message sent.")
        return messages[0]  

    def capture_region(self):
        try:
            x1 = int(input("Enter the top-left X coordinate: "))
            y1 = int(input("Enter the top-left Y coordinate: "))
            x2 = int(input("Enter the bottom-right X coordinate: "))
            y2 = int(input("Enter the bottom-right Y coordinate: "))

            logger.debug(f"Capturing region: ({x1}, {y1}), ({x2}, {y2})")

            captured_image = capture_region(x1, y1, x2, y2)
            if self.storage_option == "Locally (Hidden)":
                save_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG files", "*.png"), ("All files", "*.*")])
                if save_path:
                    utils.save_image_locally(captured_image, save_path)
                    logger.info(f"Region captured and saved successfully at {save_path}")
            elif self.storage_option == "MongoDB":
                timestamp = time.strftime("%Y%m%d_%H%M%S")
                self.save_screenshot_to_mongodb(captured_image, timestamp)
                logger.info(f"Region captured and saved to MongoDB")
        except Exception as e:
            logger.error(f"Error capturing region: {e}")

    def capture_all_monitors(self):
        try:
            logger.debug("Capturing all monitors.")
            captured_image = capture_all_monitors()
            if self.storage_option == "Locally (Hidden)":
                save_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG files", "*.png"), ("All files", "*.*")])
                if save_path:
                    utils.save_image_locally(captured_image, save_path)
                    logger.info(f"All monitors captured and saved successfully at {save_path}")
            elif self.storage_option == "MongoDB":
                timestamp = time.strftime("%Y%m%d_%H%M%S")
                self.save_screenshot_to_mongodb(captured_image, timestamp)
                logger.info(f"All monitors captured and saved to MongoDB")
        except Exception as e:
            logger.error(f"Error capturing all monitors: {e}")

def main():
    root = tk.Tk()
    app = ScreenCaptureApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
