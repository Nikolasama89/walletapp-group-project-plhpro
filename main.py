import sqlite3
import tkinter
print("Tkinter version:", tkinter.TkVersion)
# Create the main application window
root = tkinter.Tk()
root.title("Tkinter Demo")
root.geometry("300x200")  # window size

# Function to change label text
def on_button_click():
    label.config(text="Hello, Tkinter!")

# Add a label
label = tkinter.Label(root, text="Click the button below")
label.pack(pady=20)

# Add a button
button = tkinter.Button(root, text="Click Me", command=on_button_click)
button.pack(pady=10)

# Start the application event loop
root.mainloop()