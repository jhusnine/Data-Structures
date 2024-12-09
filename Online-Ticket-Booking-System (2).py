import tkinter as tk
from tkinter import messagebox
import sqlite3


class CinemaApp:
    def __init__(self, master):
        self.master = master
        self.master.title("JKL Cinema Booking System")
        self.master.geometry("800x600")
        self.master.configure(bg="black")

        self.user_name = ""  # Store user name
        self.selected_movie = None  # Store selected movie details
        self.selected_branch = ""
        self.selected_seats = []
        self.selected_time = ""
        self.selected_snacks = {}  # Store selected snacks and quantities
        self.seats_status = {}  # Store seat bookings: {(branch, movie, time): [booked_seats]}
        self.setup_database()
        self.create_welcome_page()

    def setup_database(self):
        """Initialize the SQLite database."""
        conn = sqlite3.connect("cinema_booking.db")
        cursor = conn.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS bookings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                branch TEXT,
                movie TEXT,
                schedule TEXT,
                seats TEXT,
                snacks TEXT,
                total_price REAL
            )
            """
        )
        conn.commit()
        conn.close()

    def clear_window(self):
        """Clear all widgets in the window."""
        for widget in self.master.winfo_children():
            widget.destroy()

    def create_welcome_page(self):
        """Create the welcome page."""
        self.clear_window()
        tk.Label(
            self.master,
            text="Welcome to JKL Cinema!",
            font=("Arial", 24, "bold"),
            fg="yellow",
            bg="black",
        ).pack(pady=20)

        tk.Label(
            self.master,
            text="Enter your name:",
            font=("Arial", 18),
            fg="white",
            bg="black",
        ).pack(pady=10)

        name_entry = tk.Entry(self.master, font=("Arial", 16))
        name_entry.pack(pady=10)

        def save_name():
            self.user_name = name_entry.get().strip()
            if self.user_name:
                self.create_branch_selection_page()
            else:
                messagebox.showwarning("Input Required", "Please enter your name!")

        tk.Button(
            self.master,
            text="Continue",
            command=save_name,
            font=("Arial", 14),
            bg="green",
            fg="white",
            width=15,
        ).pack(pady=10)

        tk.Button(
            self.master,
            text="View Tickets",
            command=self.view_tickets,
            font=("Arial", 14),
            bg="blue",
            fg="white",
            width=15,
        ).pack(pady=10)

        tk.Button(
            self.master,
            text="Cancel Tickets",
            command=self.cancel_tickets,  # Ensure this is connected correctly
            font=("Arial", 14),
            bg="red",
            fg="white",
            width=15,
        ).pack(pady=10)

    def cancel_tickets(self):
        """Display and allow cancellation of tickets."""
        conn = sqlite3.connect("cinema_booking.db")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM bookings")
        bookings = cursor.fetchall()
        conn.close()

        # Create a new window for ticket cancellation
        cancel_window = tk.Toplevel(self.master)
        cancel_window.title("Cancel Tickets")
        cancel_window.geometry("800x600")
        cancel_window.configure(bg="black")

        tk.Label(
            cancel_window,
            text="Cancel Tickets",
            font=("Arial", 20, "bold"),
            fg="yellow",
            bg="black",
        ).pack(pady=10)

        # Create a frame for scrolling
        frame = tk.Frame(cancel_window, bg="black")
        frame.pack(fill=tk.BOTH, expand=True)

        canvas = tk.Canvas(frame, bg="black")
        scrollbar = tk.Scrollbar(frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg="black")

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Display bookings with cancel buttons
        for booking in bookings:
            booking_id, name, branch, movie, schedule, seats, snacks, total_price = booking
            booking_frame = tk.Frame(scrollable_frame, bg="black")
            booking_frame.pack(pady=5, padx=10, fill=tk.X)

            tk.Label(
                booking_frame,
                text=f"""
                Booking ID: {booking_id}
                Name: {name}
                Branch: {branch}
                Movie: {movie}
                Schedule: {schedule}
                Seats: {seats}
                Snacks: {snacks}
                Total Price: ₱{total_price}
                """,
                font=("Arial", 12),
                fg="white",
                bg="black",
                justify="left",
                anchor="w",
                wraplength=700,
            ).pack(side=tk.LEFT, padx=10)

            # Use lambda to pass the correct parameters for cancellation
            tk.Button(
                booking_frame,
                text="Cancel",
                command=lambda b_id=booking_id, branch=branch, movie=movie, schedule=schedule, seats=seats: self.confirm_cancel(
                    b_id, branch, movie, schedule, seats
                ),
                font=("Arial", 12),
                bg="red",
                fg="white",
                width=10,
            ).pack(side=tk.RIGHT, padx=10)

        tk.Button(
            cancel_window,
            text="Close",
            command=cancel_window.destroy,
            font=("Arial", 14),
            bg="red",
            fg="white",
            width=10,
        ).pack(pady=10)

    def confirm_cancel(self, booking_id, branch, movie, schedule, seats):
        """Confirm ticket cancellation."""
        if messagebox.askyesno("Confirm Cancellation", "Are you sure you want to cancel this booking?"):
            # Update the database to remove the booking
            conn = sqlite3.connect("cinema_booking.db")
            cursor = conn.cursor()
            cursor.execute("DELETE FROM bookings WHERE id = ?", (booking_id,))
            conn.commit()
            conn.close()

            # Update the seat status
            key = (branch, movie, schedule)
            if key in self.seats_status:
                for seat in seats.split(","):
                    if seat in self.seats_status[key]:
                        self.seats_status[key].remove(seat)

            messagebox.showinfo("Cancellation Successful", "The booking has been canceled.")
            self.cancel_tickets()  # Refresh the cancellation window


    def view_tickets(self):
        """Display all booked tickets."""
        conn = sqlite3.connect("cinema_booking.db")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM bookings")
        bookings = cursor.fetchall()
        conn.close()

        # Create a new window for viewing tickets
        tickets_window = tk.Toplevel(self.master)
        tickets_window.title("View Tickets")
        tickets_window.geometry("800x600")
        tickets_window.configure(bg="black")

        tk.Label(
            tickets_window,
            text="All Bookings",
            font=("Arial", 20, "bold"),
            fg="yellow",
            bg="black",
        ).pack(pady=10)

        # Create a frame for scrolling
        frame = tk.Frame(tickets_window, bg="black")
        frame.pack(fill=tk.BOTH, expand=True)

        canvas = tk.Canvas(frame, bg="black")
        scrollbar = tk.Scrollbar(frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg="black")

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Display bookings
        for booking in bookings:
            booking_id, name, branch, movie, schedule, seats, snacks, total_price = booking
            tk.Label(
                scrollable_frame,
                text=f"""
                Booking ID: {booking_id}
                Name: {name}
                Branch: {branch}
                Movie: {movie}
                Schedule: {schedule}
                Seats: {seats}
                Snacks: {snacks}
                Total Price: ₱{total_price}
                """,
                font=("Arial", 12),
                fg="white",
                bg="black",
                justify="left",
                anchor="w",
                wraplength=700,
            ).pack(pady=5, padx=10, fill=tk.X)

        tk.Button(
            tickets_window,
            text="Close",
            command=tickets_window.destroy,
            font=("Arial", 14),
            bg="red",
            fg="white",
            width=10,
        ).pack(pady=10)

    def create_branch_selection_page(self):
        """Branch selection screen."""
        self.clear_window()
        tk.Label(
            self.master,
            text=f"Welcome, {self.user_name}!\nSelect a branch:",
            font=("Arial", 18, "bold"),
            fg="yellow",
            bg="black",
        ).pack(pady=20)

        branches = [
            "SM City Baguio",
            "SM City Fairview",
            "SM City Tarlac",
            "SM North EDSA",
            "SM Mall of Asia",
            "SM San Jose Del Monte",
        ]
        for branch in branches:
            tk.Button(
                self.master,
                text=branch,
                command=lambda b=branch: self.create_movie_selection_page(b),
                font=("Arial", 14),
                bg="yellow",
                fg="black",
                width=25,
            ).pack(pady=5)

    def create_movie_selection_page(self, branch):
        """Movie selection screen."""
        self.clear_window()
        self.selected_branch = branch
        tk.Label(
            self.master,
            text=f"Branch: {branch}\nSelect a movie to view its plot:",
            font=("Arial", 18, "bold"),
            fg="yellow",
            bg="black",
        ).pack(pady=20)

        movies = [
            (
                "A Silent Voice: The Movie (2016)",
                "A deaf girl, Shoko, is bullied by the popular Shoya. As Shoya continues to bully Shoko, the class turns its back on him. Shoko transfers and Shoya grows up as an outcast. Alone and depressed, the regretful Shoya finds Shoko to make amends.",
                280,
            ),
            (
                "Your Name (2016)",
                "Two teenagers share a profound, magical connection upon discovering they are swapping bodies. Things manage to become even more complicated when the boy and girl decide to meet in person.",
                300,
            ),
            (
                "Fairy Tail: Dragon Cry (2017)",
                "Dragon Cry is a magic artifact, and its power can destroy the world. It was kept in the Kingdom of Fiore but was stolen by the Kingdom of Stella. Natsu and his friends embark on a mission to save the world.",
                360,
            ),
            (
                "Sword Art Online: Progressive - Aria of a Starless Night (2021)",
                "High school student Asuna struggles to survive with a young swordsman after its revealed that she is trapped inside the game of Sword Art Online, where if your HP drops to zero, your brain will be destroyed in real life.",
                360,
            ),
            (
                "Attack on Titan: Chronicle (2020)",
                "A compilation film recapping the first three seasons of the anime Attack on Titan.",
                320,
            ),
            (
                "Weathering with You (2019)",
                "A high-school boy who has run away to Tokyo befriends a girl who appears to be able to manipulate the weather.",
                330,
            ),
        ]

        for title, plot, price in movies:
            movie_frame = tk.Frame(self.master, bg="black")
            movie_frame.pack(pady=5)

            tk.Button(
                movie_frame,
                text=f"{title} - ₱{price}",
                command=lambda t=title, pl=plot, p=price: self.view_movie_plot(t, pl, p),
                font=("Arial", 12),
                bg="yellow",
                fg="black",
                width=40,
            ).pack(side=tk.LEFT, padx=5)

    def view_movie_plot(self, title, plot, price):
        """Display the plot of the selected movie."""
        self.clear_window()
        tk.Label(
            self.master,
            text=f"Title: {title}",
            font=("Arial", 18, "bold"),
            fg="yellow",
            bg="black",
        ).pack(pady=10)

        tk.Label(
            self.master,
            text=f"Plot:\n{plot}",
            font=("Arial", 14),
            fg="white",
            bg="black",
            wraplength=700,
            justify="left",
        ).pack(pady=10)

        tk.Button(
            self.master,
            text="Choose this movie",
            command=lambda: self.create_schedule_page(self.selected_branch, title, plot, price),
            font=("Arial", 14),
            bg="green",
            fg="white",
            width=20,
        ).pack(pady=10)

        tk.Button(
            self.master,
            text="Back to Movie List",
            command=lambda: self.create_movie_selection_page(self.selected_branch),
            font=("Arial", 14),
            bg="red",
            fg="white",
            width=20,
        ).pack(pady=10)

    def create_schedule_page(self, branch, movie, plot, price):
        """Schedule selection screen."""
        self.clear_window()
        tk.Label(
            self.master,
            text=f"Branch: {branch}\nMovie: {movie}\nPrice: ₱{price}",
            font=("Arial", 16),
            fg="yellow",
            bg="black",
        ).pack(pady=10)

        tk.Label(
            self.master,
            text="Select a schedule:",
            font=("Arial", 14),
            fg="white",
            bg="black",
        ).pack(pady=10)

        schedules = ["10:00 AM", "1:00 PM", "4:00 PM", "7:00 PM"]
        for schedule in schedules:
            tk.Button(
                self.master,
                text=schedule,
                command=lambda s=schedule: self.create_seat_selection_page(branch, movie, price, s),
                font=("Arial", 12),
                bg="yellow",
                fg="black",
                width=20,
            ).pack(pady=5)

    def create_seat_selection_page(self, branch, movie, price, schedule):
        """Seat selection screen."""
        self.clear_window()
        tk.Label(
            self.master,
            text=f"Branch: {branch}\nMovie: {movie}\nSchedule: {schedule}\nPrice per Seat: ₱{price}",
            font=("Arial", 14),
            fg="yellow",
            bg="black",
        ).pack(pady=10)

        tk.Label(
            self.master,
            text="Select your seats:",
            font=("Arial", 12),
            fg="white",
            bg="black",
        ).pack(pady=10)

        seat_frame = tk.Frame(self.master, bg="black")
        seat_frame.pack()

        key = (branch, movie, schedule)
        if key not in self.seats_status:
            self.seats_status[key] = []

        self.selected_seats = []

        def toggle_seat(seat):
            if seat in self.selected_seats:
                self.selected_seats.remove(seat)
            else:
                self.selected_seats.append(seat)

        for i in range(25):
            seat = f"Seat-{i+1}"
            state = "disabled" if seat in self.seats_status[key] else "normal"
            tk.Checkbutton(
                seat_frame,
                text=seat,
                variable=tk.BooleanVar(),
                command=lambda s=seat: toggle_seat(s),
                state=state,
            ).grid(row=i // 5, column=i % 5, padx=5, pady=5)

        tk.Button(
            self.master,
            text="Continue to Snacks",
            command=lambda: self.create_snacks_page(branch, movie, price, schedule),
            font=("Arial", 14),
            bg="green",
            fg="white",
        ).pack(pady=20)

    def create_snacks_page(self, branch, movie, price, schedule):
        """Snacks selection screen."""
        if not self.selected_seats:
            messagebox.showwarning("No Seats Selected", "Please select at least one seat!")
            return

        self.clear_window()
        self.selected_snacks = {}

        tk.Label(
            self.master,
            text=f"Branch: {branch}\nMovie: {movie}\nSchedule: {schedule}\nSelected Seats: {len(self.selected_seats)}\nPrice per Seat: ₱{price}",
            font=("Arial", 14),
            fg="yellow",
            bg="black",
        ).pack(pady=10)

        snacks_menu = {
            "Popcorn": 150,
            "Nachos": 100,
            "Hotdog": 80,
            "Soda": 50,
            "Ice Cream": 120,
        }

        def update_snack_quantity(snack, quantity):
            if quantity > 0:
                self.selected_snacks[snack] = quantity
            elif snack in self.selected_snacks:
                del self.selected_snacks[snack]

        for snack, price in snacks_menu.items():
            snack_frame = tk.Frame(self.master, bg="black")
            snack_frame.pack(pady=5)

            tk.Label(
                snack_frame,
                text=f"{snack} - ₱{price}",
                font=("Arial", 12),
                fg="white",
                bg="black",
                width=25,
            ).pack(side=tk.LEFT)

            quantity_spinbox = tk.Spinbox(
                snack_frame,
                from_=0,
                to=10,
                command=lambda s=snack: update_snack_quantity(s, int(quantity_spinbox.get())),
                font=("Arial", 12),
                width=5,
            )
            quantity_spinbox.pack(side=tk.RIGHT)

        tk.Button(
            self.master,
            text="Finalize Booking",
            command=lambda: self.finalize_booking(branch, movie, price, schedule),
            font=("Arial", 14),
            bg="green",
            fg="white",
        ).pack(pady=20)

    def finalize_booking(self, branch, movie, price, schedule):
        """Finalize the booking and display confirmation."""
        total_price = len(self.selected_seats) * price
        total_price += sum(self.selected_snacks.values())

        # Insert booking into the database
        conn = sqlite3.connect("cinema_booking.db")
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO bookings (name, branch, movie, schedule, seats, snacks, total_price) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (
                self.user_name,
                branch,
                movie,
                schedule,
                ",".join(self.selected_seats),
                str(self.selected_snacks),
                total_price,
            ),
        )
        conn.commit()
        conn.close()

        # Update seat status
        key = (branch, movie, schedule)
        self.seats_status[key].extend(self.selected_seats)

        # Confirmation message
        confirmation_message = f"""
        Booking Confirmation:

        Name: {self.user_name}
        Branch: {branch}
        Movie: {movie}
        Schedule: {schedule}
        Seats: {', '.join(self.selected_seats)}
        Snacks: {str(self.selected_snacks)}
        Total Price: ₱{total_price}
        """
        messagebox.showinfo("Booking Confirmed", confirmation_message)

        self.clear_window()
        self.create_welcome_page()


if __name__ == "__main__":
    root = tk.Tk()
    app = CinemaApp(root)
    root.mainloop()