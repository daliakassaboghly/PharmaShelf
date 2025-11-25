from django.db import models
import re
import bcrypt





class UserManager(models.Manager):
    def validate_user_registration(self, postData):
        errors = {}
        EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$")
        if len(postData["name"]) < 2:
            errors["name"] = "Name must be at least 2 characters long."

        if len(postData["email"]) == 0:
            errors["email"] = "Email is required."
        elif not EMAIL_REGEX.match(postData["email"]):
            errors["email"] = "Invalid email format."
        else:
            existing_users = User.objects.filter(email=postData["email"])
            if len(existing_users) > 0:
                errors["email"] = "This email is already registered."

        if len(postData["password"]) < 8:
            errors["password"] = "Password must be at least 8 characters long."

        if postData["password"] != postData["confirm_password"]:
            errors["confirm_password"] = "Password and confirmation do not match."

        return errors
    def validate_user_update(self, postData):
        errors = {}
        if len(postData["role"]) == 0:
            errors["role"] = "Role is required."
        elif postData["role"] not in ["admin", "pharmacist"]:
            errors["role"] = "Invalid role."
        return errors
    
    def validate_profile_update(self, postData):
        errors = {}
        if len(postData["name"]) == 0:
            errors["name"] = "Name is required."
        return errors

    def validate_password_change(self, postData):
        errors = {}
        if len(postData["current_password"]) == 0:
            errors["current_password"] = "Current password is required."
        if len(postData["new_password"]) < 8:
            errors["new_password"] = "Password must be at least 8 characters."
        if postData["new_password"] != postData["confirm_password"]:
            errors["confirm_password"] = "Passwords do not match."
        return errors
    
class DrugManager(models.Manager):
    def validate_drug(self, postData):
        errors = {}
        if len(postData["name"]) == 0:
            errors["name"] = "Drug name is required."
        if len(postData["active_ingredient"]) == 0:
            errors["active_ingredient"] = "Active ingredient is required."
        if len(postData["dosage_form"]) == 0:
            errors["dosage_form"] = "Dosage form is required."
        if len(postData["indications"]) < 10:
            errors["indications"] = "Indications should be at least 10 characters long."
        if len(postData["side_effects"]) > 0 and len(postData["side_effects"]) < 5:
            errors["side_effects"] = "Side effects should be at least 5 characters long if provided."
        if len(postData["stock_quantity"]) > 0:
            try:
                qty = int(postData["stock_quantity"])
                if qty < 0:
                    errors["stock_quantity"] = "Stock quantity cannot be negative."
            except ValueError:
                errors["stock_quantity"] = "Stock quantity must be a number."
        return errors

    def validate_stock_update(self, postData):
        errors = {}
        if len(postData["stock_quantity"]) == 0:
            errors["stock_quantity"] = "Stock quantity is required."
        else:
            try:
                qty = int(postData["stock_quantity"])
                if qty < 0:
                    errors["stock_quantity"] = "Stock quantity cannot be negative."
            except ValueError:
                errors["stock_quantity"] = "Stock quantity must be a number."
        return errors


class CategoryManager(models.Manager):
    def validate_category(self, postData):
        errors = {}

        if len(postData["name"]) == 0:
            errors["name"] = "Category name is required."

        if len(postData["description"]) > 0 and len(postData["description"]) < 3:
            errors["description"] = "Description should be at least 3 characters long if provided."

        return errors


class DrugInteractionManager(models.Manager):
    def validate_interaction(self, postData):
        errors = {}

        if len(postData["drug_a_id"]) == 0:
            errors["drug_a_id"] = "First drug is required."

        if len(postData["drug_b_id"]) == 0:
            errors["drug_b_id"] = "Second drug is required."

        if len(postData["drug_a_id"]) > 0 and len(postData["drug_b_id"]) > 0:
            if postData["drug_a_id"] == postData["drug_b_id"]:
                errors["drug_b_id"] = "Select two different drugs for an interaction."

        if len(postData["severity"]) == 0:
            errors["severity"] = "Severity is required."

        if len(postData["description"]) > 0 and len(postData["description"]) < 5:
            errors["description"] = "Description should be at least 5 characters long if provided."

        return errors
    
class DrugAlternativeManager(models.Manager):
    def validate_alternative(self, postData):
        errors = {}

        if len(postData["alternative_drug_id"]) == 0:
            errors["alternative_drug_id"] = "Alternative drug is required."

        if len(postData["drug_id"]) == 0:
            errors["drug_id"] = "Main drug is required."

        if len(postData["drug_id"]) > 0 and len(postData["alternative_drug_id"]) > 0:
            if postData["drug_id"] == postData["alternative_drug_id"]:
                errors["alternative_drug_id"] = "Alternative must be a different drug."

        if len(postData["note"]) > 0 and len(postData["note"]) < 3:
            errors["note"] = "Note should be at least 3 characters long if provided."

        return errors



class User(models.Model):
    name = models.CharField(max_length=150)
    email = models.CharField(max_length=150)
    password_hash = models.CharField(max_length=255)
    role = models.CharField(max_length=50, default="pharmacist")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = UserManager()


class Category(models.Model):
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = CategoryManager()


class Drug(models.Model):
    name = models.CharField(max_length=150)
    active_ingredient = models.CharField(max_length=150)
    dosage_form = models.CharField(max_length=150)
    indications = models.TextField()
    side_effects = models.TextField(blank=True)
    stock_quantity = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, related_name="drugs_created", on_delete=models.CASCADE)
    category = models.ForeignKey(Category, related_name="drugs", on_delete=models.CASCADE)

    objects = DrugManager()


class DrugAlternative(models.Model):
    drug = models.ForeignKey(Drug, related_name="alternatives", on_delete=models.CASCADE)
    alternative_drug = models.ForeignKey(Drug, related_name="alternative_for", on_delete=models.CASCADE)
    note = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = DrugAlternativeManager()


class DrugInteraction(models.Model):
    drug_a = models.ForeignKey(Drug, related_name="interactions_as_a", on_delete=models.CASCADE)
    drug_b = models.ForeignKey(Drug, related_name="interactions_as_b", on_delete=models.CASCADE)
    severity = models.CharField(max_length=150)
    description = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = DrugInteractionManager()


def create_user(postData, pw_hash):
    user = User.objects.create(
        name=postData["name"],
        email=postData["email"],
        password_hash=pw_hash,
        role=""
    )
    return user


def get_user_by_email(inputEmail):
    users = User.objects.filter(email=inputEmail)
    return users


def get_current_user(id):
    user = User.objects.get(id=id)
    return user


def get_all_categories():
    all_categories = Category.objects.all()
    return all_categories


def create_drug(postData, user_id):
    current_user = User.objects.get(id=user_id)
    category = Category.objects.get(id=postData["category_id"])

    stock_quantity = 0
    if len(postData["stock_quantity"]) > 0:
        stock_quantity = int(postData["stock_quantity"])

    drug = Drug.objects.create(
        name=postData["name"],
        active_ingredient=postData["active_ingredient"],
        dosage_form=postData["dosage_form"],
        indications=postData["indications"],
        side_effects=postData["side_effects"],
        stock_quantity=stock_quantity,
        created_by=current_user,
        category=category
    )
    return drug

def get_all_drugs():
    all_drugs = Drug.objects.all()
    return all_drugs



def create_category(postData):
    category = Category.objects.create(
        name=postData["name"],
        description=postData["description"]
    )
    return category

def get_drug_by_id(drug_id):
    drug = Drug.objects.get(id=drug_id)
    return drug


def create_interaction(postData):
    drug_a = Drug.objects.get(id=postData["drug_a_id"])
    drug_b = Drug.objects.get(id=postData["drug_b_id"])

    interaction = DrugInteraction.objects.create(
        drug_a=drug_a,
        drug_b=drug_b,
        severity=postData["severity"],
        description=postData["description"]
    )
    return interaction


def get_interactions_between(drug_a_id, drug_b_id):
    interactions = DrugInteraction.objects.filter(drug_a_id=drug_a_id, drug_b_id=drug_b_id)
    if len(interactions) == 0:
        interactions = DrugInteraction.objects.filter(drug_a_id=drug_b_id, drug_b_id=drug_a_id)
    return interactions


def get_alternatives_for_drug(drug_id):
    alternatives = DrugAlternative.objects.filter(drug_id=drug_id)
    return alternatives


def create_alternative(postData):
    drug = Drug.objects.get(id=postData["drug_id"])
    alternative_drug = Drug.objects.get(id=postData["alternative_drug_id"])

    alternative = DrugAlternative.objects.create(
        drug=drug,
        alternative_drug=alternative_drug,
        note=postData["note"]
    )
    return alternative


def delete_alternative_by_id(alt_id):
    alternative = DrugAlternative.objects.get(id=alt_id)
    alternative.delete()


def update_drug_stock(drug_id, new_stock):
    drug = Drug.objects.get(id=drug_id)
    drug.stock_quantity = new_stock
    drug.save()
    return drug


def get_admin_emails():
    admins = User.objects.filter(role="admin")
    emails = []
    for admin in admins:
        if len(admin.email) > 0:
            emails.append(admin.email)
    return emails


def update_drug_details(drug_id, postData):
    drug = Drug.objects.get(id=drug_id)
    category = Category.objects.get(id=postData["category_id"])

    stock_quantity = 0
    if len(postData["stock_quantity"]) > 0:
        stock_quantity = int(postData["stock_quantity"])

    drug.name = postData["name"]
    drug.active_ingredient = postData["active_ingredient"]
    drug.dosage_form = postData["dosage_form"]
    drug.indications = postData["indications"]
    drug.side_effects = postData["side_effects"]
    drug.stock_quantity = stock_quantity
    drug.category = category
    drug.save()
    return drug


def get_all_users():
    users = User.objects.all()
    return users


def update_user_from_admin(user_id, postData):
    user = User.objects.get(id=user_id)
    user.role = postData["role"]
    is_active = False
    if "is_active" in postData:
        is_active = True
    user.is_active = is_active
    user.save()
    return user


def update_user_name(user_id, postData):
    user = User.objects.get(id=user_id)
    user.name = postData["name"]
    user.save()
    return user


def update_user_password(user_id, new_password):
    user = User.objects.get(id=user_id)
    pw_hash = bcrypt.hashpw(new_password.encode(), bcrypt.gensalt()).decode()
    user.password_hash = pw_hash
    user.save()
    return user


def get_filtered_drugs(search_query, selected_category_id, in_stock_only):
    qs = Drug.objects.all()

    if search_query is not None and len(search_query) > 0:
        qs = qs.filter(name__icontains=search_query)

    if selected_category_id > 0:
        qs = qs.filter(category_id=selected_category_id)

    if in_stock_only:
        qs = qs.filter(stock_quantity__gt=0)

    qs = qs.order_by("name")
    return qs
