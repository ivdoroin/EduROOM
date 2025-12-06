import flet as ft
from datetime import datetime, timedelta
import calendar

def CustomCalendar(on_date_selected, initial_date=None, min_date=None):
    """Custom calendar picker component"""
    
    selected_date = initial_date or datetime.now()
    current_month = selected_date.month
    current_year = selected_date.year
    min_date = min_date or datetime.now()
    
    # References for dynamic updates
    month_year_text = ft.Ref[ft.Text]()
    calendar_grid = ft.Ref[ft.Column]()
    
    def get_month_year_string():
        return f"{calendar.month_name[current_month]} {current_year}"
    
    def build_calendar_grid():
        cal = calendar.monthcalendar(current_year, current_month)
        rows = []
        
        for week in cal:
            week_buttons = []
            for day in week:
                if day == 0:
                    week_buttons.append(ft.Container(width=40, height=40))
                else:
                    date_obj = datetime(current_year, current_month, day)
                    is_selected = (date_obj.date() == selected_date.date())
                    is_past = date_obj.date() < min_date.date()
                    is_today = date_obj.date() == datetime.now().date()
                    
                    if is_selected:
                        bg_color = ft.Colors.BLUE
                        text_color = ft.Colors.WHITE
                    elif is_today:
                        bg_color = ft.Colors.BLUE_100
                        text_color = ft.Colors.BLUE
                    else:
                        bg_color = None
                        text_color = ft.Colors.GREY_400 if is_past else ft.Colors.BLACK
                    
                    week_buttons.append(
                        ft.Container(
                            content=ft.Text(str(day), size=14, color=text_color),
                            width=40,
                            height=40,
                            alignment=ft.alignment.center,
                            border_radius=20,
                            bgcolor=bg_color,
                            on_click=lambda e, d=day: date_clicked(d) if not is_past else None,
                            ink=not is_past
                        )
                    )
            
            rows.append(ft.Row(week_buttons, spacing=5))
        
        return ft.Column(rows, spacing=5)
    
    def date_clicked(day):
        nonlocal selected_date
        selected_date = datetime(current_year, current_month, day)
        calendar_grid.current.controls = [build_calendar_grid()]
        calendar_grid.current.update()
        
        if on_date_selected:
            on_date_selected(selected_date)
    
    def prev_month(e):
        nonlocal current_month, current_year
        if current_month == 1:
            current_month = 12
            current_year -= 1
        else:
            current_month -= 1
        
        refresh_calendar()
    
    def next_month(e):
        nonlocal current_month, current_year
        if current_month == 12:
            current_month = 1
            current_year += 1
        else:
            current_month += 1
        
        refresh_calendar()
    
    def refresh_calendar():
        month_year_text.current.value = get_month_year_string()
        calendar_grid.current.controls = [build_calendar_grid()]
        month_year_text.current.update()
        calendar_grid.current.update()
    
    # Build the calendar UI
    return ft.Container(
        content=ft.Column([
            # Header with navigation
            ft.Row([
                ft.IconButton(
                    icon=ft.Icons.CHEVRON_LEFT,
                    on_click=prev_month
                ),
                ft.Text(
                    ref=month_year_text,
                    value=get_month_year_string(),
                    size=16,
                    weight=ft.FontWeight.BOLD
                ),
                ft.IconButton(
                    icon=ft.Icons.CHEVRON_RIGHT,
                    on_click=next_month
                )
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            
            # Weekday headers
            ft.Row([
                ft.Container(
                    content=ft.Text(day, size=12, weight=ft.FontWeight.BOLD),
                    width=40,
                    alignment=ft.alignment.center
                )
                for day in ['Mo', 'Tu', 'We', 'Th', 'Fr', 'Sa', 'Su']
            ]),
            
            # Calendar grid
            ft.Column(
                ref=calendar_grid,
                controls=[build_calendar_grid()],
                spacing=0
            )
        ], spacing=10),
        padding=20,
        border=ft.border.all(1, ft.Colors.OUTLINE),
        border_radius=10,
        width=340
    )