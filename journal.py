import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import sqlite3
from datetime import datetime
import shutil
import os
from PIL import Image, ImageTk

class JournalApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Social Media Journal")
        self.root.geometry("800x600")
        
        # Initialize database
        self.init_database()
        
        # Create main frame
        self.main_frame = ttk.Frame(self.root, padding="10")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Variables
        self.username_var = tk.StringVar()
        self.social_network_var = tk.StringVar()
        self.date_var = tk.StringVar()
        self.time_var = tk.StringVar()
        self.image_path = tk.StringVar()
        self.current_image_path = None
        
        # Create widgets
        self.create_widgets()
        
        # Load entries
        self.load_entries()

    def init_database(self):
        """Initialize SQLite database and create table if it doesn't exist"""
        self.conn = sqlite3.connect('journal.db')
        self.cursor = self.conn.cursor()
        
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS entries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                social_network TEXT NOT NULL,
                date TEXT NOT NULL,
                time TEXT NOT NULL,
                image_path TEXT,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        self.conn.commit()

    def create_widgets(self):
        """Create all GUI widgets"""
        # Username
        ttk.Label(self.main_frame, text="Username:").grid(row=0, column=0, sticky=tk.W)
        ttk.Entry(self.main_frame, textvariable=self.username_var).grid(row=0, column=1, sticky=(tk.W, tk.E))
        
        # Social Network
        ttk.Label(self.main_frame, text="Social Network:").grid(row=1, column=0, sticky=tk.W)
        social_networks = ['Twitter', 'Instagram', 'Facebook', 'LinkedIn', 'Other']
        ttk.Combobox(self.main_frame, textvariable=self.social_network_var, values=social_networks).grid(row=1, column=1, sticky=(tk.W, tk.E))
        
        # Date and Time
        ttk.Label(self.main_frame, text="Date:").grid(row=2, column=0, sticky=tk.W)
        date_entry = ttk.Entry(self.main_frame, textvariable=self.date_var)
        date_entry.grid(row=2, column=1, sticky=(tk.W, tk.E))
        self.date_var.set(datetime.now().strftime('%Y-%m-%d'))
        self.time_var.set(datetime.now().strftime('%H:%M'))
        
        ttk.Label(self.main_frame, text="Time:").grid(row=3, column=0, sticky=tk.W)
        time_entry = ttk.Entry(self.main_frame, textvariable=self.time_var)
        time_entry.grid(row=3, column=1, sticky=(tk.W, tk.E))
        self.time_var.set(datetime.now().strftime('%H:%M'))
        
        # Image
        ttk.Label(self.main_frame, text="Image:").grid(row=4, column=0, sticky=tk.W)
        ttk.Button(self.main_frame, text="Browse", command=self.browse_image).grid(row=4, column=1, sticky=tk.W)
        
        # Preview image
        self.image_label = ttk.Label(self.main_frame, cursor="hand2")
        self.image_label.grid(row=2, column=2, rowspan=3)
        self.image_label.bind('<Button-1>', self.open_image)
        
        # Notes
        ttk.Label(self.main_frame, text="Notes:").grid(row=5, column=0, sticky=tk.W)
        self.notes_text = tk.Text(self.main_frame, height=10, width=40)
        self.notes_text.grid(row=5, column=1, sticky=(tk.W, tk.E))
        
        # Buttons Frame - Moved to left side
        button_frame = ttk.Frame(self.main_frame)
        button_frame.grid(row=0, column=2, rowspan=2, sticky=tk.W, padx=10)
        
        ttk.Button(button_frame, text="Save Entry", command=self.save_entry).pack(side=tk.TOP, pady=5)
        ttk.Button(button_frame, text="Clear Form", command=self.clear_form).pack(side=tk.TOP, pady=5)
        
        # Entries list
        self.tree = ttk.Treeview(self.main_frame, columns=('Username', 'Social Network', 'Date', 'Time'), show='headings')
        self.tree.grid(row=6, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure columns
        self.tree.heading('Username', text='Username')
        self.tree.heading('Social Network', text='Social Network')
        self.tree.heading('Date', text='Date')
        self.tree.heading('Time', text='Time')
        
        # Bind double-click event
        self.tree.bind('<Double-1>', self.load_entry)

    def browse_image(self):
        """Open file dialog to select an image"""
        file_path = filedialog.askopenfilename(
            filetypes=[("Image files", "*.png *.jpg *.jpeg *.gif *.bmp *.ico")]
        )
        if file_path:
            # Create images directory if it doesn't exist
            if not os.path.exists('images'):
                os.makedirs('images')
            
            # Copy image to images directory
            filename = os.path.basename(file_path)
            new_path = os.path.join('images', filename)
            shutil.copy2(file_path, new_path)
            
            self.current_image_path = new_path
            self.display_image(new_path)

    def display_image(self, image_path):
        """Display the selected image"""
        if image_path and os.path.exists(image_path):
            image = Image.open(image_path)
            image.thumbnail((100, 100))  # Resize image for preview
            photo = ImageTk.PhotoImage(image)
            self.image_label.configure(image=photo)
            self.image_label.image = photo
            
    def open_image(self, event):
        """Open the full image when clicked"""
        if self.current_image_path and os.path.exists(self.current_image_path):
            image = Image.open(self.current_image_path)
            image.show()  # This will open the image in the default image viewer

    def save_entry(self):
        """Save journal entry to database"""
        username = self.username_var.get()
        social_network = self.social_network_var.get()
        date = self.date_var.get()
        time = self.time_var.get()
        notes = self.notes_text.get("1.0", tk.END).strip()
        
        if not all([username, social_network, date, time]):
            messagebox.showerror("Error", "Please fill in all required fields")
            return
        
        try:
            self.cursor.execute('''
                INSERT INTO entries (username, social_network, date, time, image_path, notes)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (username, social_network, date, time, self.current_image_path, notes))
            self.conn.commit()
            
            messagebox.showinfo("Success", "Entry saved successfully!")
            self.clear_form()
            self.load_entries()
        except sqlite3.Error as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")

    def load_entries(self):
        """Load all entries into the treeview"""
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Load entries from database
        self.cursor.execute('''
            SELECT username, social_network, date, time FROM entries
            ORDER BY date DESC, time DESC
        ''')
        
        for entry in self.cursor.fetchall():
            self.tree.insert('', 'end', values=entry)

    def load_entry(self, event):
        """Load selected entry into the form"""
        selected_item = self.tree.selection()[0]
        values = self.tree.item(selected_item)['values']
        
        # Get full entry details from database
        self.cursor.execute('''
            SELECT * FROM entries
            WHERE username=? AND social_network=? AND date=? AND time=?
        ''', values)
        
        entry = self.cursor.fetchone()
        if entry:
            self.username_var.set(entry[1])
            self.social_network_var.set(entry[2])
            self.date_var.set(entry[3])
            self.current_image_path = entry[4]
            self.notes_text.delete("1.0", tk.END)
            self.notes_text.insert("1.0", entry[5] if entry[5] else "")
            
            if self.current_image_path:
                self.display_image(self.current_image_path)

    def clear_form(self):
        """Clear all form fields"""
        self.username_var.set("")
        self.social_network_var.set("")
        self.date_var.set(datetime.now().strftime('%Y-%m-%d'))
        self.current_image_path = None
        self.notes_text.delete("1.0", tk.END)
        self.image_label.configure(image='')

    def __del__(self):
        """Clean up database connection"""
        if hasattr(self, 'conn'):
            self.conn.close()

if __name__ == "__main__":
    root = tk.Tk()
    app = JournalApp(root)
    root.mainloop()