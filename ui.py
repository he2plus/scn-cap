import utils
from capture import capture_fullscreen, capture_active_window, capture_region, capture_active_monitor, capture_all_monitors

def main():
    """Provides a command-line interface for capturing and managing images."""
    while True:
        print("-" * 40)
        print("Image Capture Tool")
        print("-" * 40)
        print("1. Capture Fullscreen")
        print("2. Capture Active Window")
        print("3. Capture Region")
        print("4. Capture Active Monitor")
        print("5. Capture All Monitors")
        print("6. Exit")
        choice = input("Enter your choice (1-6): ")

        if choice == '1':
            save_path = input("Enter the save path (e.g., screenshot.jpg): ")
            image = capture_fullscreen(save_path)
            if image is not None:
                utils.save_image_locally(image, save_path)
                print("Screenshot captured successfully!")
        elif choice == '2':
            save_path = input("Enter the save path: ")
            image = capture_active_window()
            if image is not None:
                utils.save_image_locally(image, save_path)
                print("Active window captured successfully!")
        elif choice == '3':
            try:
                x1 = int(input("Enter the starting x coordinate: "))
                y1 = int(input("Enter the starting y coordinate: "))
                x2 = int(input("Enter the ending x coordinate: "))
                y2 = int(input("Enter the ending y coordinate: "))
                save_path = input("Enter the save path: ")
                image = capture_region(x1, y1, x2, y2)
                if image is not None:
                    utils.save_image_locally(image, save_path)
                    print("Region captured successfully!")
            except ValueError:
                print("Invalid input. Coordinates must be integers.")
        elif choice == '4':
            save_path = input("Enter the save path: ")
            image = capture_active_monitor()
            if image is not None:
                utils.save_image_locally(image, save_path)
                print("Active monitor captured successfully!")
        elif choice == '5':
            save_path = input("Enter the save path: ")
            image = capture_all_monitors()
            if image is not None:
                utils.save_image_locally(image, save_path)
                print("All monitors captured successfully!")
        elif choice == '6':
            print("Exiting program...")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
