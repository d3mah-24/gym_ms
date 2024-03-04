from collections import defaultdict

import frappe
import frappe.www.list
from frappe import _

no_cache = 1


def get_context(context):
    if frappe.session.user == "Guest":
        frappe.throw(_("You need to be logged in to access this page"), frappe.PermissionError)

    context.current_user = frappe.get_doc("User", frappe.session.user)
    context.active = "workout_plan"
    Plan_query = """
               SELECT 
                   GWP.price,
                   GWP.name,
                   GWP.plan_name,
                    GF.facility_name AS facility,
                    JSON_OBJECT(  GS.day,  GS.name ) AS shift, 
                   GC.full_name AS Coach,
                   GWE.exercise_name
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


               JOIN
                   `tabGym Coach` AS GC 
               ON
                   GC.name = GWP.coach


               JOIN
                   `tabGym Workout Exercise Detail` AS GWED
               ON
                   GWED.parent = GWP.name
               JOIN
                   `tabGym Workout Exercise` AS GWE
               ON
                   GWED.exercise = GWE.name 


               JOIN
                   `tabGym Facility Detail` AS GFD
               ON
                   GFD.parent = GWP.name
               JOIN
                   `tabGym Facility` AS GF
               ON
                   GFD.facility = GF.name

           """
    data = frappe.db.sql(Plan_query, as_dict=1)
    result = defaultdict(lambda: defaultdict(lambda: defaultdict(set)))
    for item in data:
        price = item['price']
        plan_name = item['plan_name']
        facility = item['facility']
        shift = eval(item['shift'])
        coach = item['Coach']
        exercise_name = item['exercise_name']
        for day, details in shift.items():
            result[day][plan_name]['facility'].add(facility)
            result[day][plan_name]['exercise_name'].add(exercise_name)
            result[day][plan_name]['price'] = price
            result[day][plan_name]['coach'] = coach
            result[day][plan_name]['name'] = item['name']
            result[day][plan_name]['detail'] = details.split("-")[1]
    res = defaultdict(list)
    for plan in list(dict(result).values()):
        for workout, data in plan.items():
            res[workout] = data
    context["workout_plans"] = res
    return context
