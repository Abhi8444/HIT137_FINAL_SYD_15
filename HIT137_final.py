import tkinter as tk
from tkinter import filedialog, Scale, HORIZONTAL
import cv2

class CROPApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Image Editor")

        self.original_image = None
        self.cropped_image = None
        self.preview_image = None

        # Fixed dimensions for canvases
        self.canvas_width = 500
        self.canvas_height = 400

        # Load Image Button
        self.load_button = tk.Button(root, text="Load Image", command=self.load_image)
        self.load_button.pack(pady=5)

        # Frame to hold canvases side by side
        self.canvas_frame = tk.Frame(root)
        self.canvas_frame.pack()

        # Canvas for Original Image
        self.original_canvas = tk.Canvas(self.canvas_frame, cursor="cross", width=self.canvas_width, height=self.canvas_height, bd=2, relief=tk.SOLID)
        self.original_canvas.pack(side=tk.LEFT, padx=5, pady=5)

        # Canvas for Cropped Preview
        self.preview_canvas = tk.Canvas(self.canvas_frame, width=self.canvas_width, height=self.canvas_height, bd=2, relief=tk.SOLID)
        self.preview_canvas.pack(side=tk.RIGHT, padx=5, pady=5)

        # Resize Slider
        self.scale = Scale(root, from_=100, to=10, orient=HORIZONTAL, label='Quality', command=self.update_preview)
        self.scale.pack(pady=5)
        self.scale.set(100)  # Default at 100% quality

        # Save Image Button
        self.save_button = tk.Button(root, text="Save Image", command=self.save_image)
        self.save_button.pack(pady=5)

        # Variables for Cropping
        self.rect = None
        self.start_x = None
        self.start_y = None

        # Variables to keep references
        self.original_photo = None
        self.preview_photo = None

        # Bind Mouse Events for Cropping
        self.original_canvas.bind("<ButtonPress-1>", self.on_button_press)
        self.original_canvas.bind("<B1-Motion>", self.on_move_press)
        self.original_canvas.bind("<ButtonRelease-1>", self.on_button_release)

    def load_image(self):
        # Select and load image from local device
        file_path = filedialog.askopenfilename()
        if file_path:
            image = cv2.imread(file_path)
            # Resize image to fit within the canvas size
            self.original_image = self.resize_image_to_canvas(image, self.canvas_width, self.canvas_height)
            # Display thumbnail on the Load button (optional)
            thumbnail = self.create_thumbnail(self.original_image)
            self.display_thumbnail(thumbnail)
            # Show image on original canvas
            self.show_image(self.original_image)

    def create_thumbnail(self, image):
        # Create a temporary thumbnail of the loaded image
        thumbnail_size = (50, 50)
        thumbnail = cv2.resize(image, thumbnail_size)
        return thumbnail

    def display_thumbnail(self, image):
        # Display the thumbnail on the Load Image button
        ppm_image = self.cv2_to_ppm(image)
        if ppm_image is not None:
            self.thumbnail_photo = tk.PhotoImage(data=ppm_image)
            self.load_button.config(image=self.thumbnail_photo, compound=tk.LEFT)
            self.load_button.image = self.thumbnail_photo

    
    def show_image(self, image):
        # Display the image on the original canvas
        self.original_canvas.delete("all")
        ppm_image = self.cv2_to_ppm(image)
        if ppm_image is not None:
            self.original_photo = tk.PhotoImage(data=ppm_image)
            # Center the image on the canvas
            x_offset = (self.canvas_width - image.shape[1]) // 2
            y_offset = (self.canvas_height - image.shape[0]) // 2
            self.original_canvas.create_image(x_offset, y_offset, anchor="nw", image=self.original_photo)
            self.display_image = image.copy()
            self.image_x_offset = x_offset
            self.image_y_offset = y_offset

    def cv2_to_ppm(self, image):
        # Convert OpenCV image to PPM format for Tkinter
        is_success, buffer = cv2.imencode(".ppm", image)
        if is_success:
            return buffer.tobytes()
        else:
            return None

    def on_button_press(self, event):
        # Start drawing rectangle for cropping
        if self.original_image is None:
            return
        self.start_x = event.x
        self.start_y = event.y
        if self.rect:
            self.original_canvas.delete(self.rect)

    def on_move_press(self, event):
        # Update rectangle
        if self.original_image is None:
            return
        cur_x, cur_y = event.x, event.y
        if self.rect:
            self.original_canvas.delete(self.rect)
        # Draw rectangle
        self.rect = self.original_canvas.create_rectangle(self.start_x, self.start_y, cur_x, cur_y, outline='white')

    

    def show_preview_image(self, image):
        # Display the cropped image on the preview canvas
        self.preview_canvas.delete("all")
        ppm_image = self.cv2_to_ppm(image)
        if ppm_image is not None:
            self.preview_photo = tk.PhotoImage(data=ppm_image)
            # Center the image on the canvas
            x_offset = (self.canvas_width - image.shape[1]) // 2
            y_offset = (self.canvas_height - image.shape[0]) // 2
            self.preview_canvas.create_image(x_offset, y_offset, anchor="nw", image=self.preview_photo)

    def update_preview(self, value):
        # Update the preview image based on slider value
        if self.preview_image is None:
            return
        scale_percent = int(value)
        degraded_image = self.preview_image.copy()
        
        # Apply progressive degradation (blur effect)
        degradation_level = (100 - scale_percent) // 10
        for _ in range(degradation_level):
            degraded_image = cv2.blur(degraded_image, (5, 5))
        
        # Update the preview image
        self.preview_image = degraded_image.copy()
        
        # Update the image in the preview canvas
        ppm_image = self.cv2_to_ppm(degraded_image)
        if ppm_image is not None:
            self.preview_photo = tk.PhotoImage(data=ppm_image)
            # Center the image on the canvas
            x_offset = (self.canvas_width - degraded_image.shape[1]) // 2
            y_offset = (self.canvas_height - degraded_image.shape[0]) // 2
            self.preview_canvas.create_image(x_offset, y_offset, anchor="nw", image=self.preview_photo)

    def save_image(self):
        # Save the modified (blurred) image
        if self.preview_image is None:
            print("No image to save.")
            return
        file_path = filedialog.asksaveasfilename(defaultextension=".png")
        if file_path:
            cv2.imwrite(file_path, self.preview_image)  # Save the blurred image
            print(f"Image saved at: {file_path}")

if __name__ == "__main__":
    root = tk.Tk()
    app = CROPApp(root)
    root.mainloop()
