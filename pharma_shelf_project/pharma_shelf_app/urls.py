
from django.urls import path
from . import views

urlpatterns = [
    path("", views.login, name="login"),
    path("login/", views.login, name="login"),
    path("signup/", views.signup, name="signup"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("logout/", views.logout, name="logout"),
   
    path("drugs/", views.drugs_list, name="drugs"),
    path("drugs/add/", views.add_drug, name="add_drug"),
    path("drugs/<int:drug_id>/", views.drug_details, name="drug_details"),
    path("drugs/<int:drug_id>/alternatives/add/", views.add_alternative, name="add_alternative"),
    path("drugs/<int:drug_id>/alternatives/<int:alt_id>/remove/", views.remove_alternative, name="remove_alternative"),
    path("drugs/<int:drug_id>/edit/", views.edit_drug, name="edit_drug"),
    path("drugs/<int:drug_id>/stock/update/", views.update_drug_stock, name="update_drug_stock"),
    
    path("categories/", views.categories_list, name="categories"),
    path("categories/add/", views.add_category, name="add_category"),
    
    path("interactions/check/", views.interaction_checker, name="interaction_checker"),
    path("interactions/add/", views.add_interaction, name="add_interaction"),

    path("users/", views.user_management, name="user_management"),
    path("users/<int:user_id>/update/", views.update_user_admin, name="update_user_admin"),

    path("profile/", views.profile, name="profile"),

    path("about/", views.about, name="about"),

    
]