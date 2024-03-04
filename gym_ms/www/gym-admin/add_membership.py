from collections import defaultdict

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
    context.active = "membership_plan"

    context.members = frappe.get_all(
        doctype="Gym Member"
    )

    context.shifts = frappe.get_all(
        doctype="Gym Shift"
    )
    Plan_query = """
               SELECT 
                   GWP.name, 
                     GS.name  AS shift
               FROM 
                   `tabGym Workout Plan` AS GWP

               JOIN
                   `tabGym Shift Detail` AS GSD 
               ON
                   GSD.parent = GWP.name
               JOIN
                   `tabGym Shift` AS GS 
               ON
                   GSD.shift = GS.name
                   
                
           """
    data = frappe.db.sql(Plan_query, as_dict=1)
    grouped_data = defaultdict(list)

    for entry in data:
        name = entry['name']
        grouped_data[name].append(entry['shift'])
    context.plans = dict(grouped_data)
    return context
