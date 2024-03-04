import frappe
import frappe.www.list
from frappe import _

no_cache = 1


def get_context(context):
    if frappe.session.user == "Guest":
        frappe.throw(
            _("You need to be logged in to access this page"), frappe.PermissionError
        )

    context.current_user = frappe.get_doc("User", frappe.session.user)
    context.active = "trainer"

    context["members"] = frappe.get_all(
        "Gym Coach",
        fields=[
            "name",
            "full_name",
            "no_student",
            "experience",
            "rate",
            "user.email",
            "user.mobile_no",
        ],
        order_by="full_name",
    )

    return context
