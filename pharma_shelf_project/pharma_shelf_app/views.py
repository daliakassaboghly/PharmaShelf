from django.shortcuts import render, redirect
from django.contrib import messages
from . import models
import bcrypt


from django.conf import settings
from django.template.loader import render_to_string
from django.urls import reverse
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from python_http_client.exceptions import HTTPError


from math import ceil


def login(request):
    if "user_id" in request.session:
        return redirect("/dashboard")

    if request.method == "POST":
        users = models.get_user_by_email(request.POST["email"])
        if len(users) == 0:
            messages.error(request, "Invalid email or password.")
            return redirect("/login")

        user = users[0]

        if not bcrypt.checkpw(request.POST["password"].encode(), user.password_hash.encode()):
            messages.error(request, "Invalid email or password.")
            return redirect("/login")
        
        if not user.is_active:
            messages.error(request, "Your account is disabled. Please contact the administrator.")
            return redirect("login")
        
        request.session["user_id"] = user.id
        return redirect("/dashboard")

    return render(request, "login.html")


def signup(request):
    if "user_id" in request.session:
        return redirect("/dashboard")

    if request.method == "POST":
        errors = models.User.objects.validate_user_registration(request.POST)
        if len(errors) > 0:
            for key in errors:
                messages.error(request, errors[key])
            return redirect("/signup")

        password = request.POST["password"]
        pw_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

        user = models.create_user(request.POST, pw_hash)

        request.session["user_id"] = user.id
        return redirect("/dashboard")

    return render(request, "signup.html")





def dashboard(request):
    if "user_id" not in request.session:
        return redirect("login")

    current_user = models.get_current_user(request.session["user_id"])

    total_drugs = models.Drug.objects.count()
    in_stock_drugs = models.Drug.objects.filter(stock_quantity__gt=0).count()
    out_of_stock_drugs = models.Drug.objects.filter(stock_quantity=0).count()
    total_categories = models.Category.objects.count()
    total_interactions = models.DrugInteraction.objects.count()

    low_stock_threshold = 5
    low_stock_drugs = models.Drug.objects.filter(
        stock_quantity__gt=0,
        stock_quantity__lte=low_stock_threshold
    ).select_related("category").order_by("stock_quantity", "name")

    categories = models.get_all_categories()
    categories_stats = []
    for category in categories:
        count = models.Drug.objects.filter(category=category).count()
        categories_stats.append(
            {
                "category": category,
                "drug_count": count,
            }
        )

    top_categories_stats = []
    if categories_stats:
        total_for_percent = 0
        for item in categories_stats:
            total_for_percent += item["drug_count"]

        sorted_categories = sorted(
            categories_stats,
            key=lambda x: x["drug_count"],
            reverse=True
        )
        sorted_categories = sorted_categories[:5]

        for item in sorted_categories:
            percentage = 0
            if total_for_percent > 0:
                percentage = round((item["drug_count"] * 100.0) / total_for_percent)
            top_categories_stats.append(
                {
                    "category": item["category"],
                    "drug_count": item["drug_count"],
                    "percentage": percentage,
                }
            )

    categories_chart_labels = []
    categories_chart_counts = []
    if categories_stats:
        sorted_for_chart = sorted(
            categories_stats,
            key=lambda x: x["drug_count"],
            reverse=True
        )
        top_for_chart = sorted_for_chart[:5]
        others_for_chart = sorted_for_chart[5:]

        other_count = 0
        for item in others_for_chart:
            other_count += item["drug_count"]

        for item in top_for_chart:
            categories_chart_labels.append(item["category"].name)
            categories_chart_counts.append(item["drug_count"])

        if other_count > 0:
            categories_chart_labels.append("Other")
            categories_chart_counts.append(other_count)

    users_total = 0
    users_active = 0
    users_disabled = 0
    admins_count = 0
    pharmacists_count = 0

    if current_user.role == "admin":
        users_qs = models.User.objects.all()
        users_total = users_qs.count()
        users_active = users_qs.filter(is_active=True).count()
        users_disabled = users_qs.filter(is_active=False).count()
        admins_count = users_qs.filter(role="admin").count()
        pharmacists_count = users_qs.filter(role="pharmacist").count()

    context = {
        "current_user": current_user,
        "total_drugs": total_drugs,
        "in_stock_drugs": in_stock_drugs,
        "out_of_stock_drugs": out_of_stock_drugs,
        "total_categories": total_categories,
        "total_interactions": total_interactions,
        "low_stock_drugs": low_stock_drugs,
        "categories_stats": categories_stats,
        "top_categories_stats": top_categories_stats,
        "categories_chart_labels": categories_chart_labels,
        "categories_chart_counts": categories_chart_counts,
        "users_total": users_total,
        "users_active": users_active,
        "users_disabled": users_disabled,
        "admins_count": admins_count,
        "pharmacists_count": pharmacists_count,
    }

    return render(request, "dashboard.html", context)



def logout(request):
    if "user_id" in request.session:
        del request.session["user_id"]
    return redirect("/login")


def add_drug(request):
    if "user_id" not in request.session:
        return redirect("login")

    current_user = models.get_current_user(request.session["user_id"])
    if current_user.role != "admin":
        return redirect("drugs")
    
    if request.method == "POST":
        errors = models.Drug.objects.validate_drug(request.POST)
        if len(errors) > 0:
            for key in errors:
                messages.error(request, errors[key])
            return redirect("add_drug")

        user_id = request.session["user_id"]
        models.create_drug(request.POST, user_id)
        messages.success(request, "Drug created successfully.")
        return redirect("drugs")

    categories = models.get_all_categories()

    context = {
        "current_user": current_user,
        "categories": categories
    }
    return render(request, "add_drug.html", context)



def drugs_list(request):
    if "user_id" not in request.session:
        return redirect("login")

    current_user = models.get_current_user(request.session["user_id"])
    categories = models.get_all_categories()

    search_query = ""
    selected_category_id = 0
    in_stock_only = False

    if "q" in request.GET:
        search_query = request.GET["q"]

    if "category_id" in request.GET:
        if len(request.GET["category_id"]) > 0:
            selected_category_id = int(request.GET["category_id"])

    if "in_stock_only" in request.GET:
        in_stock_only = request.GET["in_stock_only"] == "on"

    qs = models.get_filtered_drugs(search_query, selected_category_id, in_stock_only)

    page_size = 5
    page_param = "1"
    if "page" in request.GET:
        page_param = request.GET["page"]

    try:
        page = int(page_param)
    except ValueError:
        page = 1

    if page < 1:
        page = 1

    total_count = qs.count()
    total_pages = ceil(total_count / page_size) if total_count > 0 else 1

    if page > total_pages:
        page = total_pages

    page_numbers = range(1, total_pages + 1)

    offset = (page - 1) * page_size
    limit = offset + page_size

    drugs = qs[offset:limit]

    has_previous = page > 1
    has_next = page < total_pages

    context = {
        "current_user": current_user,
        "categories": categories,
        "drugs": drugs,
        "search_query": search_query,
        "selected_category_id": selected_category_id,
        "in_stock_only": in_stock_only,
        "page": page,
        "total_pages": total_pages,
        "has_previous": has_previous,
        "has_next": has_next,
        "page_numbers": page_numbers,
    }
    return render(request, "drugs.html", context)





def categories_list(request):
    if "user_id" not in request.session:
        return redirect("login")

    current_user = models.get_current_user(request.session["user_id"])
    categories = models.get_all_categories()

    context = {
        "current_user": current_user,
        "categories": categories
    }
    return render(request, "categories.html", context)


def add_category(request):
    if "user_id" not in request.session:
        return redirect("login")

    if request.method != "POST":
        return redirect("categories")

    errors = models.Category.objects.validate_category(request.POST)
    if len(errors) > 0:
        for key in errors:
            messages.error(request, errors[key])
        return redirect("categories")

    models.create_category(request.POST)
    return redirect("categories")

def drug_details(request, drug_id):
    if "user_id" not in request.session:
        return redirect("login")

    current_user = models.get_current_user(request.session["user_id"])
    selected_drug = models.get_drug_by_id(drug_id)
    alternatives = models.get_alternatives_for_drug(drug_id)
    all_drugs = models.get_all_drugs()

    context = {
        "current_user": current_user,
        "selected_drug": selected_drug,
        "alternatives": alternatives,
        "all_drugs": all_drugs
    }
    return render(request, "drug_details.html", context)

def add_alternative(request, drug_id):
    if "user_id" not in request.session:
        return redirect("login")

    if request.method != "POST":
        return redirect("drug_details", drug_id=drug_id)

    errors = models.DrugAlternative.objects.validate_alternative(request.POST)
    if len(errors) > 0:
        for key in errors:
            messages.error(request, errors[key])
        return redirect("drug_details", drug_id=drug_id)

    models.create_alternative(request.POST)
    messages.success(request, "Alternative added successfully.")
    return redirect("drug_details", drug_id=drug_id)

def remove_alternative(request, drug_id, alt_id):
    if "user_id" not in request.session:
        return redirect("login")

    models.delete_alternative_by_id(alt_id)
    messages.success(request, "Alternative removed successfully.")
    return redirect("drug_details", drug_id=drug_id)

def interaction_checker(request):
    if "user_id" not in request.session:
        return redirect("login")

    current_user = models.get_current_user(request.session["user_id"])
    all_drugs = models.get_all_drugs()

    selected_drug_a_id = 0
    selected_drug_b_id = 0
    interactions = []
    has_checked = False

    if "drug_a_id" in request.GET and "drug_b_id" in request.GET:
        if len(request.GET["drug_a_id"]) > 0 and len(request.GET["drug_b_id"]) > 0:
            selected_drug_a_id = int(request.GET["drug_a_id"])
            selected_drug_b_id = int(request.GET["drug_b_id"])
            has_checked = True
            interactions = models.get_interactions_between(selected_drug_a_id, selected_drug_b_id)

    context = {
        "current_user": current_user,
        "all_drugs": all_drugs,
        "selected_drug_a_id": selected_drug_a_id,
        "selected_drug_b_id": selected_drug_b_id,
        "interactions": interactions,
        "has_checked": has_checked,
    }
    return render(request, "interaction_checker.html", context)


def add_interaction(request):
    if "user_id" not in request.session:
        return redirect("login")

    if request.method == "POST":
        errors = models.DrugInteraction.objects.validate_interaction(request.POST)
        if len(errors) > 0:
            for key in errors:
                messages.error(request, errors[key])
            return redirect("add_interaction")

        models.create_interaction(request.POST)
        return redirect("interaction_checker")

    current_user = models.get_current_user(request.session["user_id"])
    all_drugs = models.get_all_drugs()

    context = {
        "current_user": current_user,
        "all_drugs": all_drugs
    }
    return render(request, "add_interaction.html", context)



def update_drug_stock(request, drug_id):
    if "user_id" not in request.session:
        return redirect("login")

    if request.method != "POST":
        return redirect("drug_details", drug_id=drug_id)

    errors = models.Drug.objects.validate_stock_update(request.POST)
    if len(errors) > 0:
        for key in errors:
            messages.error(request, errors[key])
        return redirect("drug_details", drug_id=drug_id)

    new_stock = int(request.POST["stock_quantity"])
    drug = models.update_drug_stock(drug_id, new_stock)

    if new_stock == 0 and settings.SENDGRID_API_KEY is not None:
        admin_emails = models.get_admin_emails()
        if len(admin_emails) > 0:
            subject = "Drug out of stock: " + drug.name
            plain_text = "The following drug is now out of stock: " + drug.name
            app_url = request.build_absolute_uri(reverse("drugs"))
            html_content = render_to_string(
                "emails/out_of_stock.html",
                {
                    "drug": drug,
                    "app_url": app_url
                }
            )
            try:
                print(settings.SENDGRID_API_KEY)
                sg = SendGridAPIClient(settings.SENDGRID_API_KEY)
                message = Mail(
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    to_emails=admin_emails,
                    subject=subject,
                    plain_text_content=plain_text,
                    html_content=html_content,
                )
                sg.send(message)
            except HTTPError as e:
                print("SendGrid HTTPError status:", e.status_code)
                print("SendGrid body:", e.body)
            except Exception as e:
                print("Error sending email:", e)
    messages.success(request, "Stock value was updated successfully.")
    return redirect("drug_details", drug_id=drug_id)


def edit_drug(request, drug_id):
    if "user_id" not in request.session:
        return redirect("login")

    current_user = models.get_current_user(request.session["user_id"])
    if current_user.role != "admin":
        return redirect("drug_details", drug_id=drug_id)
    
    selected_drug = models.get_drug_by_id(drug_id)
    categories = models.get_all_categories()

    if request.method == "POST":
        errors = models.Drug.objects.validate_drug(request.POST)
        if len(errors) > 0:
            for key in errors:
                messages.error(request, errors[key])
            return redirect("edit_drug", drug_id=drug_id)

        models.update_drug_details(drug_id, request.POST)
        messages.success(request, "Drug updated successfully.")
        return redirect("drug_details", drug_id=drug_id)

    context = {
        "current_user": current_user,
        "selected_drug": selected_drug,
        "categories": categories
    }
    return render(request, "edit_drug.html", context)


def user_management(request):
    if "user_id" not in request.session:
        return redirect("login")

    current_user = models.get_current_user(request.session["user_id"])
    if current_user.role != "admin":
        return redirect("drugs")

    users = models.get_all_users()

    context = {
        "current_user": current_user,
        "users": users
    }
    return render(request, "user_management.html", context)


def update_user_admin(request, user_id):
    if "user_id" not in request.session:
        return redirect("login")

    current_user = models.get_current_user(request.session["user_id"])
    if current_user.role != "admin":
        return redirect("drugs")

    if request.method != "POST":
        return redirect("user_management")

    errors = models.User.objects.validate_user_update(request.POST)
    if len(errors) > 0:
        for key in errors:
            messages.error(request, errors[key])
        return redirect("user_management")

    models.update_user_from_admin(user_id, request.POST)
    messages.success(request, "User updated successfully.")
    return redirect("user_management")


def profile(request):
    if "user_id" not in request.session:
        return redirect("login")

    current_user = models.get_current_user(request.session["user_id"])

    if request.method == "POST":
        form_type = request.POST["form_type"]

        if form_type == "profile":
            errors = models.User.objects.validate_profile_update(request.POST)
            if len(errors) > 0:
                for key in errors:
                    messages.error(request, errors[key])
                return redirect("profile")

            models.update_user_name(current_user.id, request.POST)
            return redirect("profile")

        if form_type == "password":
            errors = models.User.objects.validate_password_change(request.POST)
            if len(errors) > 0:
                for key in errors:
                    messages.error(request, errors[key])
                return redirect("profile")

            if not bcrypt.checkpw(request.POST["current_password"].encode(), current_user.password_hash.encode()):
                messages.error(request, "Current password is incorrect.")
                return redirect("profile")

            models.update_user_password(current_user.id, request.POST["new_password"])
            return redirect("profile")

    context = {
        "current_user": current_user
    }
    return render(request, "profile.html", context)


def about(request):
    if "user_id" not in request.session:
        return redirect("login")
    current_user = models.get_current_user(request.session["user_id"])
    context = {
        "current_user": current_user
    }
    return render(request, "about.html", context)
