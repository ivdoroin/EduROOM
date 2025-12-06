import flet as ft
from datetime import datetime, time
from components.custom_calendar import CustomCalendar
from components.custom_timepicker import TimeRangePicker
from data.models import ReservationModel

def ClassroomAvailabilityFilter(on_filter_applied, on_filter_cleared):
    """Filter to find available classrooms by date and time"""
    
    selected_date = None
    start_time = None
    end_time = None
    is_expanded = False
    
    # References
    filter_button = ft.Ref[ft.ElevatedButton]()
    filter_panel = ft.Ref[ft.Container]()
    active_filter_display = ft.Ref[ft.Container]()
    date_display = ft.Ref[ft.Text]()
    calendar_container = ft.Ref[ft.Container]()
    time_picker_container = ft.Ref[ft.Container]()
    
    def toggle_filter(e):
        nonlocal is_expanded
        is_expanded = not is_expanded
        filter_panel.current.visible = is_expanded
        filter_panel.current.update()
    
    def date_selected(date):
        nonlocal selected_date
        selected_date = date
        date_display.current.value = f"Selected: {date.strftime('%B %d, %Y')}"
        date_display.current.color = ft.Colors.BLUE
        date_display.current.update()
    
    def times_selected(start, end):
        nonlocal start_time, end_time
        start_time = start
        end_time = end
    
    def apply_filter(e):
        nonlocal is_expanded
        
        if not selected_date:
            show_error("Please select a date")
            return
        
        # Get time picker reference and validate
        time_picker = time_picker_container.current.content
        if not time_picker.is_valid():
            show_error("End time must be after start time")
            return
        
        # Get times from time picker
        start_time, end_time = time_picker.get_times()
        
        # Close the filter panel
        is_expanded = False
        filter_panel.current.visible = False
        filter_panel.current.update()
        
        # Show active filter badge
        active_filter_display.current.visible = True
        filter_text = active_filter_display.current.content.controls[1]
        filter_text.value = (
            f"{selected_date.strftime('%b %d')} • "
            f"{start_time.strftime('%H:%M')} - {end_time.strftime('%H:%M')}"
        )
        active_filter_display.current.update()
        
        # Trigger the filter callback
        if on_filter_applied:
            on_filter_applied(selected_date, start_time, end_time)
    
    def clear_filter(e):
        nonlocal selected_date, start_time, end_time, is_expanded
        selected_date = None
        start_time = None
        end_time = None
        date_display.current.value = "No date selected"
        date_display.current.color = ft.Colors.GREY_700
        active_filter_display.current.visible = False
        is_expanded = False
        filter_panel.current.visible = False
        
        date_display.current.update()
        active_filter_display.current.update()
        filter_panel.current.update()
        
        # Trigger the clear callback
        if on_filter_cleared:
            on_filter_cleared()
    
    def show_error(message):
        print(f"Error: {message}")
    
    # Build the component
    return ft.Column([
        ft.Row([
            ft.ElevatedButton(
                ref=filter_button,
                text="Filter by Availability",
                icon=ft.Icons.FILTER_ALT,
                on_click=toggle_filter,
                style=ft.ButtonStyle(
                    bgcolor=ft.Colors.BLUE,
                    color=ft.Colors.WHITE
                )
            ),
            ft.Container(
                ref=active_filter_display,
                content=ft.Row([
                    ft.Icon(ft.Icons.FILTER_ALT, color=ft.Colors.WHITE, size=16),
                    ft.Text("", size=13, color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD),
                    ft.IconButton(
                        icon=ft.Icons.CLOSE,
                        icon_color=ft.Colors.WHITE,
                        icon_size=16,
                        on_click=clear_filter,
                        tooltip="Clear filter"
                    )
                ], spacing=10, alignment=ft.MainAxisAlignment.CENTER),
                padding=ft.padding.symmetric(horizontal=15, vertical=8),
                bgcolor=ft.Colors.BLUE,
                border_radius=20,
                visible=False
            )
        ], spacing=15),
        
        ft.Container(
            ref=filter_panel,
            content=ft.Column([
                ft.Row([
                    ft.Text("Select Date & Time", size=16, weight=ft.FontWeight.BOLD),
                    ft.IconButton(
                        icon=ft.Icons.CLOSE,
                        on_click=toggle_filter,
                        tooltip="Close"
                    )
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                
                ft.Divider(),
                
                # Calendar
                ft.Container(
                    ref=calendar_container,
                    content=CustomCalendar(
                        on_date_selected=date_selected,
                        min_date=datetime.now()
                    )
                ),
                ft.Text(
                    ref=date_display,
                    value="No date selected",
                    size=13,
                    color=ft.Colors.GREY_700
                ),
                
                ft.Container(height=10),
                
                # Time picker
                ft.Container(
                    ref=time_picker_container,
                    content=TimeRangePicker(
                        on_times_selected=times_selected,
                        initial_start=time(8, 0),
                        initial_end=time(9, 0)
                    )
                ),
                
                ft.Container(height=20),
                
                # Action buttons
                ft.Row([
                    ft.ElevatedButton(
                        "Apply Filter",
                        icon=ft.Icons.CHECK,
                        on_click=apply_filter,
                        style=ft.ButtonStyle(
                            bgcolor=ft.Colors.GREEN,
                            color=ft.Colors.WHITE
                        )
                    ),
                    ft.OutlinedButton(
                        "Clear Filter",
                        icon=ft.Icons.CLEAR,
                        on_click=clear_filter
                    )
                ], spacing=10, alignment=ft.MainAxisAlignment.CENTER)
            ], spacing=15, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            padding=20,
            border=ft.border.all(2, ft.Colors.BLUE_200),
            border_radius=10,
            bgcolor=ft.Colors.BLUE_50,
            visible=False
        )
    ], spacing=15)