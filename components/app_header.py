import flet as ft

def create_app_header(page, user_id, role, name, current_page="classrooms"):
    """Create the application header with navigation and user drawer"""
    
    # ==================== DRAWER ====================
    def logout_click(e):
        from views.login_view import show_login
        page.close(drawer)
        page.session.clear()
        show_login(page)
    
    def toggle_theme(e):
        page.theme_mode = ft.ThemeMode.DARK if page.theme_mode == ft.ThemeMode.LIGHT else ft.ThemeMode.LIGHT
        page.update()
    
    def open_profile(e):
        from views.profile_view import show_profile
        page.close(drawer)
        show_profile(page, user_id, role, name)
    
    drawer = ft.NavigationDrawer(
        position=ft.NavigationDrawerPosition.END,
        controls=[
            ft.Container(
                content=ft.Row([
                    ft.Icon(ft.Icons.PERSON, size=40),
                    ft.Column([
                        ft.Text(name, size=16, weight=ft.FontWeight.BOLD),
                        ft.Text(role.upper(), size=12, color=ft.Colors.GREY_600)
                    ], spacing=2)
                ], spacing=15),
                padding=20,
            ),
            ft.Divider(thickness=2),
            ft.ListTile(
                leading=ft.Icon(ft.Icons.PERSON),
                title=ft.Text("Profile"),
                on_click=open_profile
            ),
            ft.ListTile(
                leading=ft.Icon(ft.Icons.PALETTE),
                title=ft.Text("Toggle Theme"),
                on_click=toggle_theme
            ),
            ft.ListTile(
                leading=ft.Icon(ft.Icons.LOGOUT),
                title=ft.Text("Logout"),
                on_click=logout_click
            ),
            ft.Container(height=20),
        ],
    )
    
    # ==================== HEADER ====================
    logo = ft.Image(
        src="../assets/images/EduROOM-logo.png", 
        width=160,
        fit=ft.ImageFit.CONTAIN
    )

    def go_classrooms(e):
        from views.dashboard_view import show_dashboard
        show_dashboard(page, user_id, role, name)

    def go_reservations(e):
        if role == "faculty":
            from views.my_reservations_view import show_my_reservations
            show_my_reservations(page, user_id, role, name)
        elif role == "admin":
            from views.admin_view import show_admin_panel
            show_admin_panel(page, user_id, role, name)

    def go_analytics(e):
        if role == "admin":
            from views.analytics_view import show_analytics_dashboard
            show_analytics_dashboard(page, user_id, role, name)

    reservations_enabled = role in ("faculty", "admin")
    analytics_enabled = role == "admin"

    active_style = ft.ButtonStyle(
        color=ft.Colors.BLUE,
        bgcolor=ft.Colors.BLUE_100,
    )

    navbar_block = ft.Row(
        [
            ft.TextButton(
                "Classrooms", 
                on_click=go_classrooms,
                style=active_style if current_page == "classrooms" else None
            ),
            ft.TextButton(
                "Reservations", 
                on_click=go_reservations, 
                disabled=not reservations_enabled,
                style=active_style if current_page == "reservations" else None
            ),
            ft.TextButton(
                "Analytics", 
                on_click=go_analytics, 
                disabled=not analytics_enabled,
                style=active_style if current_page == "analytics" else None
            )
        ],
        expand=True,
        alignment=ft.MainAxisAlignment.SPACE_AROUND,
    )

    settings_btn = ft.IconButton(
        icon=ft.Icons.SETTINGS, 
        tooltip="Settings", 
        on_click=lambda e: page.open(drawer)
    )

    header_row = ft.Row(
        [logo, navbar_block, settings_btn],
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        vertical_alignment=ft.CrossAxisAlignment.CENTER
    )

    header_container = ft.Container(
        content=header_row,
        padding=ft.padding.symmetric(horizontal=20, vertical=15),
        bgcolor=ft.Colors.GREY_200,
        border=ft.border.only(bottom=ft.BorderSide(2, ft.Colors.OUTLINE_VARIANT))
    )
    
    # ==================== WELCOME BANNER ====================
    role_color = "#ffd141"
    
    welcome_banner = ft.Container(
        content=ft.Row(
            [
                ft.Text(f"Welcome, {name}!", size=15),
                ft.Container(
                    content=ft.Text(role.upper(), size=11),
                    bgcolor=role_color,
                    padding=ft.padding.symmetric(horizontal=10, vertical=4),
                    border_radius=5
                )
            ],
            spacing=30,
            alignment=ft.MainAxisAlignment.START,
        ),
        padding=ft.padding.symmetric(vertical=10, horizontal=30),
        bgcolor=ft.Colors.GREY_400,
    )
    
    # ==================== COMBINE ====================
    header_column = ft.Column(
        [header_container, welcome_banner],
        spacing=0
    )
    
    return header_column, drawer