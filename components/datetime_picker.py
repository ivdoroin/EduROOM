import flet as ft
import datetime

class DateTimePicker:
    """Reusable date and time picker component"""
    
    def __init__(self, page):
        self.page = page
        self.selected_date = None
        self.selected_start_time = None
        self.selected_end_time = None
        
        # Refs for UI components
        self.date_button_ref = ft.Ref[ft.Container]()
        self.start_time_button_ref = ft.Ref[ft.Container]()
        self.end_time_button_ref = ft.Ref[ft.Container]()
        
        # Callback functions
        self.on_date_change_callback = None
        self.on_start_time_change_callback = None
        self.on_end_time_change_callback = None
        self.on_all_selected_callback = None
        self.on_validation_callback = None  # NEW: For availability checking
    
    def set_callbacks(self, on_date_change=None, on_start_time_change=None, 
                     on_end_time_change=None, on_all_selected=None, on_validation=None):
        """Set callback functions for when values change"""
        self.on_date_change_callback = on_date_change
        self.on_start_time_change_callback = on_start_time_change
        self.on_end_time_change_callback = on_end_time_change
        self.on_all_selected_callback = on_all_selected
        self.on_validation_callback = on_validation  # NEW
    
    def handle_date_change(self, e):
        """Handle date picker selection"""
        self.selected_date = e.control.value
        self.date_button_ref.current.content.value = self.selected_date.strftime('%m/%d/%Y')
        
        if self.on_date_change_callback:
            self.on_date_change_callback(self.selected_date)
        
        self._check_all_selected()
        self.page.update()
    
    def handle_start_time_change(self, e):
        """Handle start time picker selection"""
        self.selected_start_time = e.control.value
        self.start_time_button_ref.current.content.value = self.selected_start_time
        
        if self.on_start_time_change_callback:
            self.on_start_time_change_callback(self.selected_start_time)
        
        self._check_all_selected()
        self.page.update()
    
    def handle_end_time_change(self, e):
        """Handle end time picker selection"""
        self.selected_end_time = e.control.value
        self.end_time_button_ref.current.content.value = self.selected_end_time
        
        if self.on_end_time_change_callback:
            self.on_end_time_change_callback(self.selected_end_time)
        
        self._check_all_selected()
        self.page.update()
    
    def _check_all_selected(self):
        """Check if all fields are selected and trigger callback"""
        if (self.selected_date and self.selected_start_time and 
            self.selected_end_time):
            
            # NEW: Run validation callback if provided
            if self.on_validation_callback:
                is_valid = self.on_validation_callback(
                    self.selected_date, 
                    self.selected_start_time, 
                    self.selected_end_time
                )
                # If validation fails, don't proceed
                if not is_valid:
                    return
            
            # If valid (or no validation), trigger the all_selected callback
            if self.on_all_selected_callback:
                self.on_all_selected_callback(
                    self.selected_date, 
                    self.selected_start_time, 
                    self.selected_end_time
                )
    
    def open_date_picker(self, e):
        """Open the date picker dialog"""
        self.page.open(
            ft.DatePicker(
                first_date=datetime.datetime.now(),
                last_date=datetime.datetime.now() + datetime.timedelta(days=365),
                on_change=self.handle_date_change
            )
        )
    
    def open_start_time_picker(self, e):
        """Open the start time picker dialog"""
        self.page.open(
            ft.TimePicker(
                on_change=self.handle_start_time_change
            )
        )
    
    def open_end_time_picker(self, e):
        """Open the end time picker dialog"""
        self.page.open(
            ft.TimePicker(
                on_change=self.handle_end_time_change
            )
        )
    
    def reset(self):
        """Reset all selections"""
        self.selected_date = None
        self.selected_start_time = None
        self.selected_end_time = None
        
        if self.date_button_ref.current:
            self.date_button_ref.current.content.value = "Select Date"
        if self.start_time_button_ref.current:
            self.start_time_button_ref.current.content.value = "Start Time"
        if self.end_time_button_ref.current:
            self.end_time_button_ref.current.content.value = "End Time"
        
        self.page.update()
    
    def set_values(self, date=None, start_time=None, end_time=None):
        """Set initial values for the pickers"""
        if date:
            self.selected_date = date
            if self.date_button_ref.current:
                self.date_button_ref.current.content.value = date.strftime('%m/%d/%Y')
        
        if start_time:
            self.selected_start_time = start_time
            if self.start_time_button_ref.current:
                self.start_time_button_ref.current.content.value = str(start_time)
        
        if end_time:
            self.selected_end_time = end_time
            if self.end_time_button_ref.current:
                self.end_time_button_ref.current.content.value = str(end_time)
        
        self.page.update()
    
    def get_values(self):
        """Get current selected values"""
        return {
            "date": self.selected_date,
            "start_time": self.selected_start_time,
            "end_time": self.selected_end_time
        }
    
    def is_complete(self):
        """Check if all fields have been selected"""
        return (self.selected_date is not None and 
                self.selected_start_time is not None and 
                self.selected_end_time is not None)
    
    def build_row(self, spacing=15, date_width=180, time_width=150):
        """Build and return a row containing all three picker buttons"""
        date_button = ft.Container(
            ref=self.date_button_ref,
            content=ft.Text("Select Date", size=14),
            padding=ft.padding.symmetric(horizontal=15, vertical=12),
            border=ft.border.all(1, ft.Colors.GREY_400),
            border_radius=8,
            bgcolor=ft.Colors.WHITE,
            on_click=self.open_date_picker,
            ink=True,
            width=date_width
        )
        
        start_time_button = ft.Container(
            ref=self.start_time_button_ref,
            content=ft.Text("Start Time", size=14),
            padding=ft.padding.symmetric(horizontal=15, vertical=12),
            border=ft.border.all(1, ft.Colors.GREY_400),
            border_radius=8,
            bgcolor=ft.Colors.WHITE,
            on_click=self.open_start_time_picker,
            ink=True,
            width=time_width
        )
        
        end_time_button = ft.Container(
            ref=self.end_time_button_ref,
            content=ft.Text("End Time", size=14),
            padding=ft.padding.symmetric(horizontal=15, vertical=12),
            border=ft.border.all(1, ft.Colors.GREY_400),
            border_radius=8,
            bgcolor=ft.Colors.WHITE,
            on_click=self.open_end_time_picker,
            ink=True,
            width=time_width
        )
        
        return ft.Row(
            [date_button, start_time_button, end_time_button],
            spacing=spacing,
            alignment=ft.MainAxisAlignment.START
        )
    
    def build_column(self, spacing=10, date_width=300, time_width=140):
        """Build and return a column containing all three picker buttons with labels"""
        date_button = ft.Container(
            ref=self.date_button_ref,
            content=ft.Text("Select Date", size=14),
            padding=ft.padding.symmetric(horizontal=15, vertical=12),
            border=ft.border.all(1, ft.Colors.GREY_400),
            border_radius=8,
            bgcolor=ft.Colors.WHITE,
            on_click=self.open_date_picker,
            ink=True,
            width=date_width
        )
        
        start_time_button = ft.Container(
            ref=self.start_time_button_ref,
            content=ft.Text("Start Time", size=14),
            padding=ft.padding.symmetric(horizontal=15, vertical=12),
            border=ft.border.all(1, ft.Colors.GREY_400),
            border_radius=8,
            bgcolor=ft.Colors.WHITE,
            on_click=self.open_start_time_picker,
            ink=True,
            width=time_width
        )
        
        end_time_button = ft.Container(
            ref=self.end_time_button_ref,
            content=ft.Text("End Time", size=14),
            padding=ft.padding.symmetric(horizontal=15, vertical=12),
            border=ft.border.all(1, ft.Colors.GREY_400),
            border_radius=8,
            bgcolor=ft.Colors.WHITE,
            on_click=self.open_end_time_picker,
            ink=True,
            width=time_width
        )
        
        return ft.Column([
            ft.Text("Date", size=12, weight=ft.FontWeight.BOLD),
            date_button,
            ft.Container(height=spacing),
            ft.Text("Time Range", size=12, weight=ft.FontWeight.BOLD),
            ft.Row([start_time_button, end_time_button], spacing=15),
        ], spacing=5)