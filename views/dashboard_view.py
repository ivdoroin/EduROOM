import flet as ft
from utils.config import ICONS, COLORS
from data.models import ClassroomModel, ReservationModel
from views.schedule_view import show_classroom_schedule
from components.classroom_filter import ClassroomAvailabilityFilter
from components.app_header import create_app_header

def show_dashboard(page, user_id, role, name):
    """Display main dashboard with availability filtering"""

    # Create the header and drawer
    header, drawer = create_app_header(page, user_id, role, name, current_page="classrooms")

    # State variables
    all_classrooms = []
    filtered_by_availability = False
    current_search_query = ""

    def open_reservation_form(classroom_id):
        from views.reservation_view import show_reservation_form
        show_reservation_form(page, user_id, role, name, classroom_id)

    # Get classrooms from database
    try:
        all_classrooms = ClassroomModel.get_all_classrooms() or []
    except Exception:
        all_classrooms = []

    # Search and filter state
    search_query = ft.Ref[ft.TextField]()
    classroom_list_ref = ft.Ref[ft.Column]()
    result_count_ref = ft.Ref[ft.Text]()

    def create_classroom_card(room):
        """Helper function to create a classroom card"""
        status_color = COLORS.GREEN if room.get("status") == "Available" else "orange"
        image_src = room.get("image_url") or "../assets/images/classroom-default.png"

        def view_schedule_click(e):
            show_classroom_schedule(page, room["id"], room.get("room_name", "Unnamed Room"))

        reserve_enabled = (role == "faculty") and (room.get("status") == "Available")

        reserve_btn = ft.ElevatedButton(
            "Reserve",
            icon=ICONS.BOOK_ONLINE,
            on_click=lambda e, rid=room["id"]: open_reservation_form(rid),
            disabled=not reserve_enabled,
            height=35,
            expand=True
        )

        if role in ("admin", "student"):
            reserve_btn = ft.ElevatedButton(
                "Reserve",
                icon=ICONS.BOOK_ONLINE,
                disabled=True,
                height=35,
                expand=True
            )

        schedule_btn = ft.OutlinedButton(
            "View Schedule",
            icon=ft.Icons.CALENDAR_TODAY,
            on_click=view_schedule_click,
            height=35,
            expand=True
        )

        return ft.Card(
            width=320,
            elevation=3,
            content=ft.Container(
                padding=0,
                content=ft.Column(
                    [
                        ft.Container(
                            content=ft.Image(
                                src=image_src,
                                fit=ft.ImageFit.COVER,
                                width=None,
                                height=200,
                            ),
                            border_radius=ft.border_radius.only(
                                top_left=8, top_right=8
                            ),
                            clip_behavior=ft.ClipBehavior.ANTI_ALIAS
                        ),
                        ft.Container(
                            padding=ft.padding.symmetric(horizontal=12, vertical=8),
                            content=ft.Column(
                                [
                                    ft.Text(
                                        room.get("room_name", "Unnamed Room"),
                                        weight=ft.FontWeight.BOLD,
                                        size=14
                                    ),
                                    ft.Text(
                                        f"{room.get('building','')} • Capacity: {room.get('capacity','-')}",
                                        size=11,
                                        color=ft.Colors.GREY_600
                                    ),
                                    ft.Text(
                                        room.get("status", "Unknown"),
                                        size=12,
                                        weight=ft.FontWeight.BOLD,
                                        color=status_color
                                    ),
                                ],
                                spacing=3
                            )
                        ),
                        ft.Container(
                            padding=ft.padding.all(12),
                            content=ft.Row(
                                [schedule_btn, reserve_btn],
                                spacing=10,
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                            )
                        )
                    ],
                    tight=True,
                    spacing=0
                )
            )
        )

    def matches_search(text, query):
        """Check if query appears in text"""
        if not query:
            return True
        return query.lower() in text.lower()
    
    def apply_filters(classrooms_to_filter):
        """Apply search query to classroom list"""
        query = current_search_query.strip()
        filtered_cards = []
        
        for room in classrooms_to_filter:
            room_name = room.get("room_name", "")
            building = room.get("building", "")
            capacity = str(room.get("capacity", ""))
            status = room.get("status", "")
            
            searchable_text = f"{room_name} {building} {capacity} {status}"
            
            if matches_search(searchable_text, query):
                filtered_cards.append(create_classroom_card(room))
        
        return filtered_cards
    
    def update_classroom_display(classrooms_to_show):
        """Update the classroom grid with filtered results"""
        filtered_cards = apply_filters(classrooms_to_show)
        
        # Update result count
        result_count_ref.current.value = f"Showing {len(filtered_cards)} classroom(s)"
        
        if not filtered_cards:
            classroom_list_ref.current.controls = [
                ft.Container(
                    content=ft.Column([
                        ft.Icon(ft.icons.SEARCH_OFF, size=64, color=ft.Colors.GREY_400),
                        ft.Text(
                            "No classrooms found",
                            size=18,
                            weight=ft.FontWeight.BOLD,
                            color=ft.Colors.GREY_600
                        ),
                        ft.Text(
                            "Try adjusting your search or filter criteria",
                            size=14,
                            color=ft.Colors.GREY_500,
                            italic=True
                        )
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=10),
                    padding=40,
                    alignment=ft.alignment.center
                )
            ]
        else:
            classroom_list_ref.current.controls = create_grid_rows(filtered_cards)
        
        page.update()
    
    def filter_by_availability(reservation_date, start_time, end_time):
        """Filter classrooms by availability on specific date/time"""
        nonlocal filtered_by_availability
        filtered_by_availability = True
        
        try:
            # Get available classrooms from database
            available_classrooms = ReservationModel.get_available_classrooms(
                reservation_date.date(),
                start_time,
                end_time
            )
            
            update_classroom_display(available_classrooms)
            
        except Exception as e:
            print(f"Error filtering classrooms: {e}")
            show_snackbar("Error loading available classrooms")
    
    def clear_availability_filter():
        """Clear availability filter and show all classrooms"""
        nonlocal filtered_by_availability
        filtered_by_availability = False
        update_classroom_display(all_classrooms)
    
    def search_classrooms(e):
        """Handle search query changes"""
        nonlocal current_search_query
        current_search_query = search_query.current.value.strip()
        
        # Apply search to current classroom list (filtered or all)
        if filtered_by_availability:
            # Re-apply the availability filter with new search
            # This requires storing the filter parameters
            pass
        else:
            update_classroom_display(all_classrooms)
    
    def show_snackbar(message):
        page.snack_bar = ft.SnackBar(content=ft.Text(message))
        page.snack_bar.open = True
        page.update()

    def create_grid_rows(cards):
        """Organize cards into rows of 3"""
        rows = []
        for i in range(0, len(cards), 3):
            row_cards = cards[i:i+3]
            rows.append(
                ft.Row(
                    controls=row_cards,
                    spacing=20,
                    alignment=ft.MainAxisAlignment.CENTER,
                    wrap=False
                )
            )
        return rows

    # Create availability filter
    availability_filter = ClassroomAvailabilityFilter(
        on_filter_applied=filter_by_availability,
        on_filter_cleared=clear_availability_filter
    )

    # Initial classroom display
    classroom_cards = [create_classroom_card(room) for room in all_classrooms]
    grid_rows = create_grid_rows(classroom_cards)

    # Build page layout
    page.controls.clear()
    page.add(
        ft.Column([
            header,  # Use the header from create_app_header
            ft.Container(
                content=ft.Text("Available Classrooms", size=32, font_family="Montserrat Bold", weight=ft.FontWeight.BOLD),
                padding=ft.padding.only(left=30, top=20), 
                alignment=ft.alignment.center
            ),
            ft.Container(height=10),
            # Search and filter controls
            ft.Container(
                content=ft.Row([
                    ft.TextField(
                        ref=search_query,
                        hint_text="Search by name, building, capacity...",
                        prefix_icon=ft.Icons.SEARCH,
                        on_change=search_classrooms,
                        width=500,
                        border_radius=10,
                    ),
                    availability_filter
                ], spacing=20, alignment=ft.MainAxisAlignment.CENTER),
                padding=ft.padding.symmetric(horizontal=30)
            ),
            # Result count
            ft.Container(
                content=ft.Text(
                    ref=result_count_ref,
                    value=f"Showing {len(all_classrooms)} classroom(s)",
                    size=13,
                    color=ft.Colors.GREY_600
                ),
                padding=ft.padding.symmetric(horizontal=30, vertical=5)
            ),
            # Scrollable classroom grid
            ft.Container(
                content=ft.Column(
                    ref=classroom_list_ref,
                    controls=grid_rows,
                    spacing=20,
                    scroll=ft.ScrollMode.AUTO
                ),
                padding=ft.padding.symmetric(horizontal=30),
                expand=True
            )
        ], spacing=0, expand=True)
    )
    page.update()