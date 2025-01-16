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
        self.main_frame.columnconfigure(1, weight=1)
        
        # Variables
        self.username_var = tk.StringVar()
        self.social_network_var = tk.StringVar()
        self.date_var = tk.StringVar()
        self.time_var = tk.StringVar()
        self.current_image_path = None
        
        # Set initial values
        self.date_var.set(datetime.now().strftime('%Y-%m-%d'))
        self.time_var.set(datetime.now().strftime('%H:%M'))
        
        self.create_widgets()
        self.load_entries()

    def init_database(self):
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
        # Username
        ttk.Label(self.main_frame, text="Username:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        username_entry = ttk.Entry(self.main_frame, textvariable=self.username_var)
        username_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=5, pady=5)
        
        # Social Network
        ttk.Label(self.main_frame, text="Social Network:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        social_networks = ['Twitter', 'Instagram', 'Facebook', 'LinkedIn', 'Other']
        social_network_combo = ttk.Combobox(self.main_frame, textvariable=self.social_network_var, values=social_networks)
        social_network_combo.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=5, pady=5)
        
        # Date and Time
        ttk.Label(self.main_frame, text="Date:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        date_entry = ttk.Entry(self.main_frame, textvariable=self.date_var)
        date_entry.grid(row=2, column=1, sticky=(tk.W, tk.E), padx=5, pady=5)
        
        ttk.Label(self.main_frame, text="Time:").grid(row=3, column=0, sticky=tk.W, padx=5, pady=5)
        time_entry = ttk.Entry(self.main_frame, textvariable=self.time_var)
        time_entry.grid(row=3, column=1, sticky=(tk.W, tk.E), padx=5, pady=5)
        
        # Image
        ttk.Label(self.main_frame, text="Image:").grid(row=4, column=0, sticky=tk.W, padx=5, pady=5)
        ttk.Button(self.main_frame, text="Browse", command=self.browse_image).grid(row=4, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Image preview - moved to better location
        self.image_label = ttk.Label(self.main_frame, cursor="hand2", relief="solid", borderwidth=1)
        self.image_label.grid(row=0, column=2, rowspan=5, padx=(20,10), pady=5, sticky='n')
        self.image_label.bind('<Button-1>', self.open_image)
        
        # Notes
        ttk.Label(self.main_frame, text="Notes:").grid(row=5, column=0, sticky=tk.NW, padx=5, pady=5)
        self.notes_text = tk.Text(self.main_frame, height=10, width=40)
        self.notes_text.grid(row=5, column=1, sticky=(tk.W, tk.E), padx=5, pady=5)
        
        # Entries list with scrollbar
        tree_frame = ttk.Frame(self.main_frame)
        tree_frame.grid(row=6, column=0, columnspan=4, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)
        tree_frame.columnconfigure(0, weight=1)
        
        # Create and configure the treeview
        self.tree = ttk.Treeview(tree_frame, 
                                columns=('Username', 'Social Network', 'Date', 'Time'),
                                show='headings',
                                height=10,
                                selectmode='browse')  # Only allow single selection
        
        # Configure scrollbar
        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Configure the columns
        for col in ('Username', 'Social Network', 'Date', 'Time'):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100, minwidth=100)
        
        # Bind selection event - Using the bind method just once
        self.tree.bind('<<TreeviewSelect>>', self.handle_selection)
        
        # Buttons below tree view
        button_frame = ttk.Frame(self.main_frame)
        button_frame.grid(row=7, column=0, columnspan=4, pady=10)
        
        ttk.Button(button_frame, text="Save Entry", command=self.save_entry).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Clear Form", command=self.clear_form).pack(side=tk.LEFT, padx=5)

    def handle_selection(self, event=None):
        """Single handler for tree selection events"""
        try:
            selected = self.tree.selection()
            if not selected:  # If nothing is selected
                return
                
            item = self.tree.item(selected[0])
            values = item['values']
            
            if not values or len(values) < 4:
                return
                
            # Get the full entry from the database
            self.cursor.execute('''
                SELECT username, social_network, date, time, image_path, notes
                FROM entries
                WHERE username=? AND social_network=? AND date=? AND time=?
            ''', values)
            
            entry = self.cursor.fetchone()
            if not entry:
                return
                
            # Update form fields
            self.username_var.set(entry[0])
            self.social_network_var.set(entry[1])
            self.date_var.set(entry[2])
            self.time_var.set(entry[3])
            
            # Update image first (index 4)
            self.current_image_path = entry[4]
            self.image_label.configure(image='')
            self.image_label.image = None
            
            if self.current_image_path and os.path.exists(self.current_image_path):
                self.display_image(self.current_image_path)
            
            # Update notes last (index 5)
            self.notes_text.delete("1.0", tk.END)
            if entry[5]:
                self.notes_text.insert("1.0", entry[5])
                
        except Exception as e:
            print(f"Selection handling error: {e}")
            # Don't show error to user, just silently handle it
            pass

    def display_image(self, image_path):
        """Display the selected image"""
        try:
            image = Image.open(image_path)
            aspect_ratio = image.width / image.height
            new_height = 150
            new_width = int(new_height * aspect_ratio)
            
            image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(image)
            self.image_label.configure(image=photo)
            self.image_label.image = photo
        except Exception as e:
            print(f"Error displaying image: {e}")

    def browse_image(self):
        """Browse for an image file"""
        file_path = filedialog.askopenfilename(
            filetypes=[("Image files", "*.png *.jpg *.jpeg *.gif *.bmp *.ico")]
        )
        if file_path:
            if not os.path.exists('images'):
                os.makedirs('images')
            
            filename = os.path.basename(file_path)
            new_path = os.path.join('images', filename)
            shutil.copy2(file_path, new_path)
            
            self.current_image_path = new_path
            self.display_image(new_path)

    def open_image(self, event):
        """Open the full image when clicked"""
        if self.current_image_path and os.path.exists(self.current_image_path):
            image = Image.open(self.current_image_path)
            image.show()

    def save_entry(self):
        """Save a new journal entry"""
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
            messagebox.showerror("Error", f"Failed to save entry: {str(e)}")

    def load_entries(self):
        """Load all entries into the treeview"""
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        try:
            self.cursor.execute('''
                SELECT username, social_network, date, time FROM entries
                ORDER BY date DESC, time DESC
            ''')
            
            for entry in self.cursor.fetchall():
                self.tree.insert('', 'end', values=entry)
                
        except sqlite3.Error as e:
            print(f"Error loading entries: {e}")

    def clear_form(self):
        """Clear all form fields"""
        self.username_var.set("")
        self.social_network_var.set("")
        self.date_var.set(datetime.now().strftime('%Y-%m-%d'))
        self.time_var.set(datetime.now().strftime('%H:%M'))
        self.current_image_path = None
        self.notes_text.delete("1.0", tk.END)
        self.image_label.configure(image='')
        self.image_label.image = None

    def __del__(self):
        """Clean up database connection"""
        if hasattr(self, 'conn'):
            self.conn.close()

if __name__ == "__main__":
    root = tk.Tk()
    app = JournalApp(root)
    root.mainloop()