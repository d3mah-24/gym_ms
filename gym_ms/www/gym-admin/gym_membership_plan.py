import frappe
import frappe.www.list
from frappe import _

no_cache = 1


def get_context(context):
    if frappe.session.user == "Guest":
        frappe.throw(_("You need to be logged in to access this page"), frappe.PermissionError)

    context.current_user = frappe.get_doc("User", frappe.session.user)
    context.active = "membership_plan"

    Plan_query = """
               SELECT  
                   GM.start_date,
                   GM.end_date,
                   GM.total_price,
                   GC.full_name,
                   GM.name,
                   GM.shift,
                   GWP.plan_name
                   
               FROM 
                   `tabGym Membership` AS GM

 
               JOIN
                   `tabGym Workout Plan` AS GWP
               ON
                   GM.plan = GWP.name  
               JOIN
                   `tabGym Coach` AS GC
               ON
                   GWP.coach = GC.name 



              JOIN
                    `tabGym Shift` AS GS
               On
                    GS.name = GM.shift
                
           """
    data = frappe.db.sql(Plan_query, as_dict=1)
    context["membership_plans"] = data

    return context
