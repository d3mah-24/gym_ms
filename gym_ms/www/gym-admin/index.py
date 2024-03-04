import frappe
import frappe.www.list
from frappe import _

no_cache = 1


def get_context(context):
    if frappe.session.user == "Guest":
        frappe.throw(_("You need to be logged in to access this page"), frappe.PermissionError)
    context.current_user = frappe.get_doc("User", frappe.session.user)
    context.active = "dashboard" 

    context["no_material"] = frappe.db.count("Gym Facility")
    context["no_plan"] = frappe.db.count("Gym Workout Plan")
    context["no_customer"] = frappe.db.count("Gym Member")
    context["no_coach"] = frappe.db.count("Gym Coach")
    context["payments"] = frappe.get_all("Gym Payment", fields=["modified","full_name","amount","irn","status"],order_by="modified")

    return context
