import flet as ft
from utils.config import ICONS, COLORS
from data.models import UserModel, ActivityLogModel
from views.dashboard_view import show_dashboard

def show_login(page):
    """Display the login page with database authentication"""
    
    email_field = ft.TextField(
        label="CSPC Email",
        hint_text="yourname@my.cspc.edu.ph",
        width=460,
        height=60,
        border_radius=10,
        text_size=14
    )
    
    id_number_field = ft.TextField(
        label="ID Number",
        hint_text="Enter your ID number",
        width=460,
        height=60,
        border_radius=10,
        text_size=14
    )
    
    password_field = ft.TextField(
        label="Password",
        hint_text="Enter your password",
        password=True,
        can_reveal_password=True,
        width=460,
        height=60,
        border_radius=10,
        text_size=14
    )
    
    error_text = ft.Text("", color="red", size=12)

    def login_click(e):
        email = email_field.value.strip()
        id_number = id_number_field.value.strip()
        password = password_field.value
        
        # Validate all fields are filled
        if not email or not id_number or not password:
            error_text.value = "Please fill in all fields"
            page.update()
            return
        
        # Authenticate using database - check both email AND id_number
        user = UserModel.authenticate_with_email(email, id_number, password)
        
        if user:
            # Log the login activity
            ActivityLogModel.log_activity(user['id'], "User logged in")
            
            # Store user info in page session
            page.session.set("user_id", user['id'])
            page.session.set("user_role", user['role'])
            page.session.set("user_name", user['full_name'])
            
            # Login successful
            show_dashboard(page, user['id'], user['role'], user['full_name'])
        else:
            error_text.value = "Invalid credentials. Please check your email, ID number, and password."
            page.update()

    logo = ft.Container(
        content=ft.Column([
            ft.Icon(ICONS.SCHOOL, size=80, color="#004B87"),
            ft.Text(
                "EduROOM",
                size=48,
                weight=ft.FontWeight.BOLD,
                spans=[
                    ft.TextSpan("Edu", style=ft.TextStyle(color="#7BC043")),
                    ft.TextSpan("ROOM", style=ft.TextStyle(color="#00A0DF"))
                ]
            )
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=5),
    )
    
    page.controls.clear()
    page.add(
        ft.Container(
            content=ft.Column([
                logo,
                ft.Text(
                    "Classroom Reservation System",
                    size=20,
                    weight=ft.FontWeight.W_500,
                    text_align=ft.TextAlign.CENTER
                ),
                ft.Container(height=30),
                email_field,
                id_number_field,
                password_field,
                error_text,
                ft.Container(height=10),
                ft.ElevatedButton(
                    "Login",
                    width=460,
                    height=50,
                    style=ft.ButtonStyle(
                        shape=ft.RoundedRectangleBorder(radius=10),
                        bgcolor="#5A5A5A",
                        color="white"
                    ),
                    on_click=login_click
                ),
            ], 
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=5),
            padding=40,
            expand=True,
            alignment=ft.alignment.center
        )
    )
    page.update()