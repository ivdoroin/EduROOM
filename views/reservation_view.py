import flet as ft
from utils.config import ICONS, COLORS
from data.models import ClassroomModel, ReservationModel, ActivityLogModel
from datetime import datetime

def show_reservation_form(page, user_id, role, name, classroom_id):
    """Display the reservation form for faculty to book classrooms"""
    
    # Only faculty can make reservations
    if role != "faculty":
        return
    
    classroom = ClassroomModel.get_classroom_by_id(classroom_id)
    if not classroom:
        return
    
    date_field = ft.TextField(
        label="Date", 
        hint_text="YYYY-MM-DD",
        width=370,
        height=55,
        border_radius=5,
        text_size=14,
        border_color="#CCCCCC"
    )
    
    start_time = ft.TextField(
        label="Start Time", 
        hint_text="HH:MM",
        width=175,
        height=55,
        border_radius=5,
        text_size=14,
        border_color="#CCCCCC"
    )
    
    end_time = ft.TextField(
        label="End Time", 
        hint_text="HH:MM",
        width=175,
        height=55,
        border_radius=5,
        text_size=14,
        border_color="#CCCCCC"
    )
    
    purpose = ft.TextField(
        label="Purpose", 
        hint_text="",
        multiline=True, 
        width=370,
        min_lines=3,
        max_lines=5,
        border_radius=5,
        text_size=14,
        border_color="#CCCCCC"
    )
    
    success_text = ft.Text("", size=12)
    
    def validate_date(date_str):
        """Validate date format"""
        try:
            datetime.strptime(date_str, '%Y-%m-%d')
            return True
        except ValueError:
            return False
    
    def validate_time(time_str):
        """Validate time format"""
        try:
            datetime.strptime(time_str, '%H:%M')
            return True
        except ValueError:
            return False
    
    def submit_reservation(e):
        # Validate all fields
        if not date_field.value or not start_time.value or not end_time.value or not purpose.value:
            success_text.value = "⚠ Please fill all fields"
            success_text.color = "red"
            page.update()
            return
        
        # Validate date format
        if not validate_date(date_field.value):
            success_text.value = "⚠ Invalid date format. Use YYYY-MM-DD"
            success_text.color = "red"
            page.update()
            return
        
        # Validate time format
        if not validate_time(start_time.value) or not validate_time(end_time.value):
            success_text.value = "⚠ Invalid time format. Use HH:MM (24-hour)"
            success_text.color = "red"
            page.update()
            return
        
        # Check if classroom is available
        is_available = ReservationModel.check_availability(
            classroom_id,
            date_field.value,
            start_time.value,
            end_time.value
        )
        
        if not is_available:
            success_text.value = "⚠ Classroom is already booked for this time slot"
            success_text.color = "red"
            page.update()
            return
        
        # Create reservation in database
        reservation_id = ReservationModel.create_reservation(
            classroom_id,
            user_id,
            date_field.value,
            start_time.value,
            end_time.value,
            purpose.value
        )
        
        if reservation_id:
            # Log activity
            ActivityLogModel.log_activity(
                user_id, 
                "Created reservation", 
                f"Reserved {classroom['room_name']} on {date_field.value}"
            )
            
            success_text.value = "✓ Reservation submitted! Waiting for admin approval."
            success_text.color = COLORS.GREEN if hasattr(COLORS, "GREEN") else "green"
            
            # Clear form
            date_field.value = ""
            start_time.value = ""
            end_time.value = ""
            purpose.value = ""
            page.update()
        else:
            success_text.value = "⚠ Failed to create reservation. Please try again."
            success_text.color = "red"
            page.update()
    
    def back_to_dashboard(e):
        from views.dashboard_view import show_dashboard
        show_dashboard(page, user_id, role, name)
    
    page.controls.clear()
    page.add(
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
                
                date_field,
                ft.Container(height=15),
                
                # Time fields centered
                ft.Container(
                    content=ft.Row([
                        start_time,
                        end_time
                    ], spacing=20, alignment=ft.MainAxisAlignment.CENTER),
                    width=370
                ),
                
                ft.Container(height=15),
                purpose,
                success_text,
                ft.Container(height=20),
                
                # Submit button
                ft.Container(
                    content=ft.ElevatedButton(
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
                        on_click=submit_reservation
                    ),
                ),
            ], 
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=0),
            padding=40,
            expand=True,
            alignment=ft.alignment.top_center
        )
    )
    page.update()