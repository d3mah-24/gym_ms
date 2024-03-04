import frappe
import frappe.www.list
from frappe import _

no_cache = 1


def get_context(context):
    if frappe.session.user == "Guest":
        frappe.throw(_("You need to be logged in to access this page"), frappe.PermissionError)

    context.current_user = frappe.get_doc("User", frappe.session.user)
    context.active = "class"

    data = frappe.get_all("Gym Class", fields=["class_name",
                                               "coach.full_name",
                                               "price",
                                               "shift"])
    context["gym_class"] = data

    return context
