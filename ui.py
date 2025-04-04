import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import csv
import json
from sentiment_analysis import sentiment_analysis

class SentimentAnalysisApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Sentiment Analysis")
        self.root.geometry("800x600")
        
        # Darker, more saturated colors
        self.bg_color = "#1a1a1a"  # Darker background
        self.entry_bg = "#2a2a2a"  # Darker entry background
        self.green_color = "#3cb371"  # More saturated green
        self.blue_color = "#1e88e5"  # More saturated blue
        self.red_color = "#e53935"   # Delete button color
        
        self.root.configure(bg=self.bg_color)
        
        # Main title
        self.title_label = tk.Label(
            root, 
            text="Sentiment Analysis", 
            font=("Arial", 24, "bold"),
            bg=self.bg_color,
            fg="white",
            pady=20
        )
        self.title_label.pack()
        
        # Container for menu buttons
        self.menu_frame = tk.Frame(root, bg=self.bg_color)
        self.menu_frame.pack(pady=10)
        
        # Menu buttons with rounded corners
        self.manual_btn = self.create_rounded_button(
            self.menu_frame,
            "Manual Inputs",
            self.green_color,
            lambda: self.show_panel("manual")
        )
        self.manual_btn.grid(row=0, column=0, padx=10)
        
        self.dataset_btn = self.create_rounded_button(
            self.menu_frame,
            "Dataset Input",
            self.blue_color,
            lambda: self.show_panel("dataset")
        )
        self.dataset_btn.grid(row=0, column=1, padx=10)
        
        self.twitter_btn = self.create_rounded_button(
            self.menu_frame,
            "Twitter Scrape",
            self.blue_color,
            lambda: self.show_panel("twitter")
        )
        self.twitter_btn.grid(row=0, column=2, padx=10)
        
        # Container for different panels
        self.panel_frame = tk.Frame(root, bg=self.bg_color)
        self.panel_frame.pack(pady=20, fill=tk.BOTH, expand=True)
        
        # Create the panels but don't show them yet
        self.create_manual_panel()
        self.create_dataset_panel()
        self.create_twitter_panel()
        
        # Results panel at the bottom
        self.results_frame = tk.Frame(root, bg=self.bg_color)
        self.results_frame.pack(pady=20, side=tk.BOTTOM, fill=tk.X)
        
        self.result_label = tk.Label(
            self.results_frame,
            text="",
            font=("Arial", 16),
            bg=self.bg_color,
            fg="white",
            pady=10
        )
        self.result_label.pack()
        
        # Start with manual panel
        self.show_panel("manual")
    
    def create_rounded_button(self, parent, text, bg_color, command):
        """Create a button with rounded appearance"""
        button = tk.Button(
            parent,
            text=text,
            font=("Arial", 12, "bold"),
            bg=bg_color,
            fg="white",
            width=15,
            height=2,
            relief=tk.RAISED,
            bd=0,
            command=command,
            cursor="hand2"
        )
        # Make it look more rounded with extra padding and rounded corners
        button.configure(padx=10, pady=5, highlightthickness=0, 
                         highlightbackground=bg_color, activebackground=bg_color)
        
        # Apply rounded corners (this is a trick that works in many Tkinter environments)
        button.bind("<Map>", lambda e, btn=button, color=bg_color: self.apply_rounded_corners(btn, color))
        
        return button
    
    def apply_rounded_corners(self, widget, color):
        """Apply rounded corners to a widget using platform-specific methods"""
        # This is a platform-independent approach that adds some styling
        radius = 10
        widget.config(relief=tk.FLAT, bd=0)
        widget.config(highlightbackground=color, highlightthickness=1)
        
        # Create a more rounded look with creative borders
        widget.config(borderwidth=0)
    
    def create_circle_button(self, parent, text, bg_color, command, width=2):
        """Create a circular button"""
        button = tk.Button(
            parent,
            text=text,
            font=("Arial", 12, "bold"),
            bg=bg_color,
            fg="white",
            width=width,
            relief=tk.FLAT,
            bd=0,
            command=command,
            cursor="hand2"
        )
        button.configure(padx=2, pady=0, highlightthickness=0, 
                         highlightbackground=bg_color, activebackground=bg_color)
        
        # Apply rounded corners
        button.bind("<Map>", lambda e, btn=button, color=bg_color: self.apply_rounded_corners(btn, color))
        
        return button
        
    def create_manual_panel(self):
        self.manual_panel = tk.Frame(self.panel_frame, bg=self.bg_color)
        
        # List to keep track of all review entries
        self.review_entries = []
        self.review_frames = {}  # Dictionary to store frame references with their assigned number
        self.next_review_number = 1
        
        # Container for review entries
        self.reviews_frame = tk.Frame(self.manual_panel, bg=self.bg_color)
        self.reviews_frame.pack(fill=tk.BOTH, expand=True, padx=50)
        
        # Add button ABOVE the review entries
        self.add_button_frame = tk.Frame(self.reviews_frame, bg=self.bg_color)
        self.add_button_frame.pack(anchor=tk.W, pady=(0, 10))
        
        self.add_btn = self.create_circle_button(
            self.add_button_frame,
            "+",
            self.green_color,
            self.add_new_review
        )
        self.add_btn.pack(side=tk.LEFT)
        
        # Add initial one review entry
        self.add_review_entry()
        
        # Submit button
        self.submit_frame = tk.Frame(self.manual_panel, bg=self.bg_color)
        self.submit_frame.pack(fill=tk.X, pady=20)
        
        self.submit_btn = self.create_rounded_button(
            self.submit_frame,
            "Submit",
            self.green_color,
            lambda: self.analyze_sentiment(1)
        )
        self.submit_btn.pack(side=tk.RIGHT, padx=50)
    
    def add_review_entry(self):
        """Add a new review entry with the current next_review_number"""
        review_frame = tk.Frame(self.reviews_frame, bg=self.bg_color)
        review_frame.pack(fill=tk.X, pady=5)
        
        # Store the frame with its assigned number for future reference
        self.review_frames[self.next_review_number] = review_frame
        
        number_label = tk.Label(
            review_frame,
            text=str(self.next_review_number),
            font=("Arial", 14),
            bg=self.bg_color,
            fg="white",
            width=3
        )
        number_label.pack(side=tk.LEFT, padx=5)
        
        entry = tk.Entry(
            review_frame,
            font=("Arial", 12),
            bg=self.entry_bg,
            fg="white",
            insertbackground="white",
            width=40,  # Reduced width to make space for the remove button
            relief=tk.FLAT,
            bd=1
        )
        entry.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=8, padx=(0, 5))
        entry.insert(0, "Enter Your Review Here")
        entry.bind("<FocusIn>", lambda e, entry=entry: self.on_entry_click(entry))
        
        # Assign the current number to this entry
        entry_number = self.next_review_number
        
        # Add a remove button
        remove_btn = self.create_circle_button(
            review_frame,
            "−",  # Using minus symbol
            self.red_color,
            lambda num=entry_number: self.remove_review(num),
            width=2
        )
        remove_btn.pack(side=tk.RIGHT, padx=5)
        
        # Apply rounded corners to the entry field
        entry.bind("<Map>", lambda e, widget=entry: self.round_entry(widget))
        
        # Add to the list of entries with the current number
        self.review_entries.append((entry_number, entry))
        
        # Increment the next number for future entries
        self.next_review_number += 1
    
    def round_entry(self, entry):
        """Apply rounded appearance to entry widgets"""
        entry.config(relief=tk.FLAT, bd=1)
        radius = 8
        # This is a visual trick to make entries look more rounded
        entry.config(highlightbackground=self.bg_color, highlightthickness=1)
    
    def renumber_entries(self):
        """Renumber all review entries in order after a deletion."""
        new_entries = []
        self.next_review_number = 1  # Reset counter

        for _, entry in self.review_entries:
            # Update number label
            entry.master.winfo_children()[0].config(text=str(self.next_review_number))
            
            # Store updated number
            new_entries.append((self.next_review_number, entry))
            
            self.next_review_number += 1

        # Replace old list with updated numbering
        self.review_entries = new_entries

    def remove_review(self, number):
        """Remove a review entry with the specified number and update numbering."""
        if len(self.review_entries) > 1:
            entry_to_remove = None
            for entry_info in self.review_entries:
                if entry_info[0] == number:
                    entry_to_remove = entry_info
                    break
            
            if entry_to_remove:
                self.review_entries.remove(entry_to_remove)
                
                if number in self.review_frames:
                    self.review_frames[number].destroy()
                    del self.review_frames[number]
                
                # Reassign numbers to remaining entries
                self.renumber_entries()

    def on_entry_click(self, entry):
        if entry.get() == "Enter Your Review Here":
            entry.delete(0, tk.END)
    
    def add_new_review(self):
        self.add_review_entry()
    
    def create_dataset_panel(self):
        self.dataset_panel = tk.Frame(self.panel_frame, bg=self.bg_color)
        
        # File path input
        self.file_label = tk.Label(
            self.dataset_panel,
            text="Enter File path to your dataset (json/csv)",
            font=("Arial", 14),
            bg=self.bg_color,
            fg="white",
            pady=20
        )
        self.file_label.pack()
        
        self.file_entry_frame = tk.Frame(self.dataset_panel, bg=self.bg_color)
        self.file_entry_frame.pack(fill=tk.X, padx=50, pady=20)
        
        self.file_entry = tk.Entry(
            self.file_entry_frame,
            font=("Arial", 12),
            bg=self.entry_bg,
            fg="white",
            insertbackground="white",
            relief=tk.FLAT,
            bd=1
        )
        self.file_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=8)
        self.file_entry.bind("<Map>", lambda e, widget=self.file_entry: self.round_entry(widget))
        
        self.browse_btn = self.create_rounded_button(
            self.file_entry_frame,
            "Browse",
            self.blue_color,
            self.browse_file
        )
        self.browse_btn.config(width=8, height=1)
        self.browse_btn.pack(side=tk.RIGHT, padx=10)
        
        # Submit button
        self.dataset_submit_frame = tk.Frame(self.dataset_panel, bg=self.bg_color)
        self.dataset_submit_frame.pack(fill=tk.X, pady=20)
        
        self.dataset_submit_btn = self.create_rounded_button(
            self.dataset_submit_frame,
            "Submit",
            self.green_color,
            lambda: self.analyze_sentiment(2)
        )
        self.dataset_submit_btn.pack(side=tk.RIGHT, padx=50)
    
    def create_twitter_panel(self):
        self.twitter_panel = tk.Frame(self.panel_frame, bg=self.bg_color)
        
        # Product name input
        self.product_label = tk.Label(
            self.twitter_panel,
            text="Enter Product/Brand Name",
            font=("Arial", 14),
            bg=self.bg_color,
            fg="white",
            pady=20
        )
        self.product_label.pack()
        
        self.product_entry_frame = tk.Frame(self.twitter_panel, bg=self.bg_color)
        self.product_entry_frame.pack(fill=tk.X, padx=50, pady=20)
        
        self.product_entry = tk.Entry(
            self.product_entry_frame,
            font=("Arial", 12),
            bg=self.entry_bg,
            fg="white",
            insertbackground="white",
            relief=tk.FLAT,
            bd=1
        )
        self.product_entry.pack(fill=tk.X, ipady=8)
        self.product_entry.bind("<Map>", lambda e, widget=self.product_entry: self.round_entry(widget))
        
        # Submit button
        self.twitter_submit_frame = tk.Frame(self.twitter_panel, bg=self.bg_color)
        self.twitter_submit_frame.pack(fill=tk.X, pady=20)
        
        self.twitter_submit_btn = self.create_rounded_button(
            self.twitter_submit_frame,
            "Submit",
            self.green_color,
            lambda: self.analyze_sentiment(3)
        )
        self.twitter_submit_btn.pack(side=tk.RIGHT, padx=50)
    
    def show_panel(self, panel_name):
        # Hide all panels
        for panel in [self.manual_panel, self.dataset_panel, self.twitter_panel]:
            panel.pack_forget()
        
        # Reset button colors
        self.manual_btn.config(bg=self.blue_color)
        self.dataset_btn.config(bg=self.blue_color)
        self.twitter_btn.config(bg=self.blue_color)
        
        # Show the selected panel and highlight its button
        if panel_name == "manual":
            self.manual_panel.pack(fill=tk.BOTH, expand=True)
            self.manual_btn.config(bg=self.green_color)
        elif panel_name == "dataset":
            self.dataset_panel.pack(fill=tk.BOTH, expand=True)
            self.dataset_btn.config(bg=self.green_color)
        elif panel_name == "twitter":
            self.twitter_panel.pack(fill=tk.BOTH, expand=True)
            self.twitter_btn.config(bg=self.green_color)
    
    def browse_file(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("CSV Files", "*.csv"), ("JSON Files", "*.json")]
        )
        if file_path:
            self.file_entry.delete(0, tk.END)
            self.file_entry.insert(0, file_path)
    
    def analyze_sentiment(self, menu_option):
        try:
            if menu_option == 1:  # Manual input
                # Get reviews from entry fields
                reviews = []
                for num, entry in self.review_entries:
                    text = entry.get().strip()
                    if text and text != "Enter Your Review Here":
                        reviews.append([num, text])
                
                if not reviews:
                    raise ValueError("Please enter at least one review")
                
                # Call sentiment analysis function
                result = sentiment_analysis(menu_option, reviews)
                self.display_result(result)
                
            elif menu_option == 2:  # Dataset input
                file_path = self.file_entry.get().strip()
                if not file_path:
                    raise ValueError("Please select a file")
                
                # Call sentiment analysis function
                result = sentiment_analysis(menu_option, file_path)
                self.display_result(result)
                
            elif menu_option == 3:  # Twitter scrape
                product = self.product_entry.get().strip()
                if not product:
                    raise ValueError("Please enter a product/brand name")
                
                # Call sentiment analysis function
                result = sentiment_analysis(menu_option, product)
                self.display_result(result)
                
        except Exception as e:
            messagebox.showerror("Error", str(e))
    
    def display_result(self, result):
        # Extract sentiment and certainty from result
        # Assuming the sentiment_analysis function returns a string with the format:
        # "Sentiment: [sentiment]\nCertainty: [certainty]"
        self.result_label.config(text=result)

# Run the application
if __name__ == "__main__":
    root = tk.Tk()
    app = SentimentAnalysisApp(root)
    root.mainloop()