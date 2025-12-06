import flet as ft
from utils.config import ICONS, COLORS
from data.models import ClassroomModel, ReservationModel, ActivityLogModel
from datetime import datetime
from components.app_header import create_app_header
from components.datetime_picker import DateTimePicker

def show_reservation_form(page, user_id, role, name, classroom_id):
    """Display the reservation form for faculty to book classrooms"""
    
    # Create the header and drawer
    header, drawer = create_app_header(page, user_id, role, name, current_page="reservations")

    # Only faculty can make reservations
    if role != "faculty":
        return
    
    classroom = ClassroomModel.get_classroom_by_id(classroom_id)
    if not classroom:
        return
    
    # Create datetime picker instance
    datetime_picker = DateTimePicker(page)
    
    # Reference for occupied slots display
    occupied_slots_ref = ft.Ref[ft.Column]()
    occupied_container_ref = ft.Ref[ft.Container]()
    
    def load_occupied_slots(selected_date=None):
        """Load and display occupied time slots for selected date"""
        if not selected_date:
            occupied_slots_ref.current.controls = []
            occupied_container_ref.current.visible = False
            page.update()
            return
        
        date_str = selected_date.strftime('%Y-%m-%d')
        occupied = ReservationModel.get_occupied_slots(classroom_id, date_str)
        
        if not occupied:
            occupied_slots_ref.current.controls = [
                ft.Text("✓ No reservations on this date", 
                       size=12, color="green", italic=True)
            ]
        else:
            slot_items = []
            for slot in occupied:
                status_color = "orange" if slot["status"] == "pending" else "green"
                slot_items.append(
                    ft.Row([
                        ft.Icon(ft.Icons.BLOCK, size=14, color=status_color),
                        ft.Text(
                            f"{str(slot['start_time'])[:5]} - {str(slot['end_time'])[:5]}",
                            size=12,
                            weight=ft.FontWeight.BOLD
                        ),
                        ft.Text(
                            f"({slot['status']})",
                            size=11,
                            color=status_color,
                            italic=True
                        )
                    ], spacing=5)
                )
            occupied_slots_ref.current.controls = slot_items
        
        occupied_container_ref.current.visible = True
        page.update()
    
    def on_date_selected(date):
        """When user selects a date, show occupied slots and update button text"""
        # Update date button text
        date_text_ref.current.value = date.strftime('%B %d, %Y')
        date_text_ref.current.color = ft.Colors.BLACK
        load_occupied_slots(date)
    
    purpose = ft.TextField(
        label="Purpose", 
        hint_text="e.g., Faculty Meeting, Training Session, etc.",
        multiline=True, 
        width=370,
        min_lines=3,
        max_lines=5,
        border_radius=5,
        text_size=14,
        border_color="#CCCCCC"
    )
    
    success_text = ft.Text("", size=12)
    availability_text = ft.Text("", size=12)  # New availability text below time picker
    submit_button_ref = ft.Ref[ft.ElevatedButton]()
    
    def validate_availability(date, start_time, end_time):
        """Validate if the selected time slot is available"""
        # Update time button texts
        start_time_text_ref.current.value = start_time
        start_time_text_ref.current.color = ft.Colors.BLACK
        end_time_text_ref.current.value = end_time
        end_time_text_ref.current.color = ft.Colors.BLACK
        page.update()
        
        # Format date for database
        date_str = date.strftime('%Y-%m-%d')
        
        # Check availability
        is_available = ReservationModel.check_availability(
            classroom_id,
            date_str,
            start_time,
            end_time
        )
        
        if not is_available:
            availability_text.value = "⚠ This time slot is already booked! Please select a different time."
            availability_text.color = "red"
            submit_button_ref.current.disabled = True
            page.update()
            return False
        else:
            availability_text.value = "✓ Time slot is available"
            availability_text.color = "green"
            page.update()
            return True
    
    def check_form_ready(*args):
        """Enable submit button when all fields are filled"""
        if datetime_picker.is_complete() and purpose.value:
            # Only enable if availability check passed
            values = datetime_picker.get_values()
            if values:
                is_available = validate_availability(
                    values["date"],
                    values["start_time"],
                    values["end_time"]
                )
                submit_button_ref.current.disabled = not is_available
        else:
            submit_button_ref.current.disabled = True
        page.update()
    
    def purpose_changed(e):
        """Handle purpose field changes"""
        check_form_ready()
    
    purpose.on_change = purpose_changed
    
    def submit_reservation(e):
        # Validate all fields
        if not datetime_picker.is_complete() or not purpose.value:
            success_text.value = "⚠ Please fill all fields"
            success_text.color = "red"
            page.update()
            return
        
        values = datetime_picker.get_values()
        
        # Format date for database (convert datetime to string)
        date_str = values["date"].strftime('%Y-%m-%d')
        
        # Double-check availability before submitting
        is_available = ReservationModel.check_availability(
            classroom_id,
            date_str,
            values["start_time"],
            values["end_time"]
        )
        
        if not is_available:
            success_text.value = "⚠ This time slot was just booked by someone else!"
            success_text.color = "red"
            page.update()
            return
        
        # Create reservation in database
        reservation_id = ReservationModel.create_reservation(
            classroom_id,
            user_id,
            date_str,
            values["start_time"],
            values["end_time"],
            purpose.value
        )
        
        if reservation_id:
            # Log activity
            ActivityLogModel.log_activity(
                user_id, 
                "Created reservation", 
                f"Reserved {classroom['room_name']} on {date_str}"
            )
            
            # Navigate back to dashboard
            from views.dashboard_view import show_dashboard
            show_dashboard(page, user_id, role, name)
        else:
            success_text.value = "⚠ Failed to create reservation. Please try again."
            success_text.color = "red"
            page.update()
    
    def back_to_dashboard(e):
        from views.dashboard_view import show_dashboard
        show_dashboard(page, user_id, role, name)
    
    # Set up datetime picker callbacks
    datetime_picker.set_callbacks(
        on_date_change=on_date_selected,      # Show occupied slots when date selected
        on_validation=validate_availability,  # Validate when all selected
        on_all_selected=check_form_ready      # Enable submit when all filled
    )
    
    # Create custom styled picker buttons with text refs
    date_text_ref = ft.Ref[ft.Text]()
    start_time_text_ref = ft.Ref[ft.Text]()
    end_time_text_ref = ft.Ref[ft.Text]()
    
    date_button = ft.Container(
        ref=datetime_picker.date_button_ref,
        content=ft.Row([
            ft.Icon(ft.Icons.CALENDAR_TODAY, size=18, color=ft.Colors.GREY_700),
            ft.Text("Select Date", size=14, color=ft.Colors.GREY_800, ref=date_text_ref),
        ], spacing=10),
        padding=ft.padding.symmetric(horizontal=15, vertical=14),
        border=ft.border.all(1, "#CCCCCC"),
        border_radius=5,
        bgcolor=ft.Colors.WHITE,
        on_click=datetime_picker.open_date_picker,
        ink=True,
        width=370
    )
    
    start_time_button = ft.Container(
        ref=datetime_picker.start_time_button_ref,
        content=ft.Row([
            ft.Icon(ft.Icons.ACCESS_TIME, size=18, color=ft.Colors.GREY_700),
            ft.Text("Start Time", size=14, color=ft.Colors.GREY_800, ref=start_time_text_ref),
        ], spacing=10),
        padding=ft.padding.symmetric(horizontal=15, vertical=14),
        border=ft.border.all(1, "#CCCCCC"),
        border_radius=5,
        bgcolor=ft.Colors.WHITE,
        on_click=datetime_picker.open_start_time_picker,
        ink=True,
        width=175
    )
    
    end_time_button = ft.Container(
        ref=datetime_picker.end_time_button_ref,
        content=ft.Row([
            ft.Icon(ft.Icons.ACCESS_TIME, size=18, color=ft.Colors.GREY_700),
            ft.Text("End Time", size=14, color=ft.Colors.GREY_800, ref=end_time_text_ref),
        ], spacing=10),
        padding=ft.padding.symmetric(horizontal=15, vertical=14),
        border=ft.border.all(1, "#CCCCCC"),
        border_radius=5,
        bgcolor=ft.Colors.WHITE,
        on_click=datetime_picker.open_end_time_picker,
        ink=True,
        width=175
    )
    
    # Store text refs in datetime_picker so it can update them
    datetime_picker.date_text_ref = date_text_ref
    datetime_picker.start_time_text_ref = start_time_text_ref
    datetime_picker.end_time_text_ref = end_time_text_ref
    
    page.controls.clear()
    page.add(
        ft.Column([
            header,
            ft.Container(
                content=ft.Column([
                    # Back button
                    ft.Container(
                        content=ft.IconButton(
                            icon=ICONS.ARROW_BACK,
                            icon_size=30,
                            on_click=back_to_dashboard,
                            tooltip="Back to Dashboard"
                        ),
                        alignment=ft.alignment.top_left,
                        width=370
                    ),
                    
                    ft.Container(height=10),
                    
                    # Title
                    ft.Text(
                        f"Reserve {classroom['room_name']}", 
                        size=28, 
                        weight=ft.FontWeight.BOLD,
                        text_align=ft.TextAlign.CENTER
                    ),
                    
                    # Subtitle
                    ft.Text(
                        f"{classroom['building']} • Capacity: {classroom['capacity']}", 
                        size=14,
                        color=COLORS.GREY if hasattr(COLORS, "GREY") else "grey",
                        text_align=ft.TextAlign.CENTER
                    ),
                    
                    ft.Container(height=10),
                    
                    # Warning banner
                    ft.Container(
                        content=ft.Row([
                            ft.Icon(ICONS.WARNING, color="#FF9800", size=18),
                            ft.Text(
                                "Reservation requires admin approval",
                                size=13,
                                color="#FF9800",
                                italic=True
                            )
                        ], spacing=8, alignment=ft.MainAxisAlignment.CENTER),
                        padding=12,
                        bgcolor="#FFF3E0",
                        border_radius=5,
                        width=370
                    ),
                    
                    ft.Container(height=25),
                    
                    # Date picker button
                    ft.Text("Date", size=12, weight=ft.FontWeight.BOLD, color=ft.Colors.GREY_700),
                    date_button,
                    
                    # Occupied slots display
                    ft.Container(
                        ref=occupied_container_ref,
                        content=ft.Column([
                            ft.Row([
                                ft.Icon(ft.Icons.INFO_OUTLINE, size=16, color="#F57C00"),
                                ft.Text("Occupied Time Slots:", size=13, weight=ft.FontWeight.BOLD, color="#F57C00")
                            ], spacing=5),
                            ft.Divider(height=5, color="#FFE082"),
                            ft.Column(
                                ref=occupied_slots_ref,
                                controls=[],
                                spacing=5
                            ),
                        ], spacing=8),
                        padding=ft.padding.all(15),
                        bgcolor="#FFF9E6",
                        border_radius=5,
                        border=ft.border.all(1, "#FFE082"),
                        width=370,
                        visible=False
                    ),
                    
                    ft.Container(height=15),
                    
                    # Time picker buttons
                    ft.Text("Time Range", size=12, weight=ft.FontWeight.BOLD, color=ft.Colors.GREY_700),
                    ft.Container(
                        content=ft.Row([
                            start_time_button,
                            end_time_button
                        ], spacing=20, alignment=ft.MainAxisAlignment.CENTER),
                        width=370
                    ),
                    
                    # Availability message below time picker
                    ft.Container(
                        content=availability_text,
                        padding=ft.padding.only(top=8),
                        width=370
                    ),
                    
                    ft.Container(height=15),
                    
                    # Purpose field
                    ft.Text("Purpose", size=12, weight=ft.FontWeight.BOLD, color=ft.Colors.GREY_700),
                    purpose,
                    success_text,
                    ft.Container(height=20),
                    
                    # Submit button
                    ft.Container(
                        content=ft.ElevatedButton(
                            ref=submit_button_ref,
                            content=ft.Row([
                                ft.Icon(ICONS.SEND, size=18),
                                ft.Text("Submit Reservation", size=15)
                            ], spacing=8, alignment=ft.MainAxisAlignment.CENTER),
                            width=370,
                            height=50,
                            style=ft.ButtonStyle(
                                shape=ft.RoundedRectangleBorder(radius=25),
                                bgcolor="#4A7BA7",
                                color="white"
                            ),
                            on_click=submit_reservation,
                            disabled=True  # Initially disabled
                        ),
                    ),
                ], 
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=5),
                padding=40,
                expand=True,
                alignment=ft.alignment.top_center
            )
        ], spacing=0, expand=True)
    )
    page.update()