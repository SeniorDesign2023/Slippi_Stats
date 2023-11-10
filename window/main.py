### MAIN WINDOW ###

# Using tkinter version 8.6
# Visit https://docs.python.org/3/library/tkinter.html for documentation

from tkinter import *
from tkinter import ttk
from tkinter import filedialog

def main():
    root = Tk()
    root.geometry('1280x760')
    root.title("Slippi Stats")
    Label(root, text = "Slippi Stats", font = ('Helvetica 20 bold')).pack(pady = 20)
    
    # Create a File Explorer label
    global label_file_explorer
    label_file_explorer = Label(root, 
                                text = "File Explorer using Tkinter",
                                width = 100, height = 4, 
                                fg = "blue")
    button_explore = Button(root, 
                            text = "Browse Files",
                            command = browseFiles)
    label_file_explorer.pack(pady=10)
    button_explore.pack(pady=10)
    quitButton = ttk.Button(text="Quit", command=root.destroy)
    quitButton.pack(pady = 100)
    root.mainloop()


def browseFiles():
    filename = filedialog.askopenfilename(initialdir = "/",
                                          title = "Select a File",
                                          filetypes = (("Slippi Files",
                                                        "*.slp*"),
                                                       ("all files",
                                                        "*.*")))
    label_file_explorer.configure(text="File Opened: "+filename)
main()