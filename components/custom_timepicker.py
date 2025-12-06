import flet as ft
from datetime import time

def CustomTimePicker(label, on_time_selected, initial_time=None):
    """Custom time picker component"""
    
    selected_time = initial_time or time(8, 0)
    
    hour_dropdown = ft.Ref[ft.Dropdown]()
    minute_dropdown = ft.Ref[ft.Dropdown]()
    
    def time_changed(e):
        nonlocal selected_time
        hour = int(hour_dropdown.current.value)
        minute = int(minute_dropdown.current.value)
        selected_time = time(hour, minute)
        
        if on_time_selected:
            on_time_selected(selected_time)
    
    return ft.Container(
        content=ft.Column([
            ft.Text(label, size=14, weight=ft.FontWeight.W_500),
            ft.Row([
                ft.Dropdown(
                    ref=hour_dropdown,
                    label="Hour",
                    width=100,
                    options=[ft.dropdown.Option(f"{h:02d}") for h in range(7, 22)],
                    value=f"{selected_time.hour:02d}",
                    on_change=time_changed
                ),
                ft.Text(":", size=24, weight=ft.FontWeight.BOLD),
                ft.Dropdown(
                    ref=minute_dropdown,
                    label="Minute",
                    width=100,
                    options=[ft.dropdown.Option(f"{m:02d}") for m in range(0, 60, 15)],
                    value=f"{selected_time.minute:02d}",
                    on_change=time_changed
                )
            ], spacing=10, alignment=ft.MainAxisAlignment.CENTER)
        ], spacing=10),
        padding=15,
        border=ft.border.all(1, ft.Colors.OUTLINE),
        border_radius=10
    )


def TimeRangePicker(on_times_selected, initial_start=None, initial_end=None):
    """Combined start and end time picker with validation"""
    
    start_time = initial_start or time(8, 0)
    end_time = initial_end or time(9, 0)
    
    validation_text = ft.Ref[ft.Text]()
    
    def start_time_changed(new_time):
        nonlocal start_time
        start_time = new_time
        validate_times()
        if on_times_selected:
            on_times_selected(start_time, end_time)
    
    def end_time_changed(new_time):
        nonlocal end_time
        end_time = new_time
        validate_times()
        if on_times_selected:
            on_times_selected(start_time, end_time)
    
    def validate_times():
        if end_time <= start_time:
            validation_text.current.value = "End time must be after start time"
            validation_text.current.visible = True
        else:
            validation_text.current.visible = False
        validation_text.current.update()
    
    def is_valid():
        return end_time > start_time
    
    def get_times():
        return (start_time, end_time)
    
    # Store functions as attributes
    picker = ft.Column([
        ft.Row([
            CustomTimePicker(
                "Start Time",
                start_time_changed,
                start_time
            ),
            ft.Container(width=20),
            CustomTimePicker(
                "End Time",
                end_time_changed,
                end_time
            )
        ], alignment=ft.MainAxisAlignment.CENTER),
        ft.Text(
            ref=validation_text,
            value="",
            size=12,
            color=ft.Colors.RED,
            visible=False
        )
    ], spacing=10)
    
    # Attach helper methods
    picker.is_valid = is_valid
    picker.get_times = get_times
    
    return picker