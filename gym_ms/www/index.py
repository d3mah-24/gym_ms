from collections import defaultdict

import frappe
from frappe.website.utils import get_home_page


def get_context(context):
    redirect_to = frappe.local.request.args.get("redirect-to")
    if frappe.session.user != "Guest":

        if not redirect_to:
            if frappe.session.data.user_type != "System User":
                redirect_to = "/gym-admin"
            else:
                redirect_to = "/app"

        if redirect_to != "login":
            frappe.local.flags.redirect_location = redirect_to
            raise frappe.Redirect
    Plan_query = """
        SELECT 
            GWP.price,
            GWP.plan_name,
             GF.facility_name AS facility,
             JSON_OBJECT(  GS.day,  GS.name ) AS shift, 
            GC.user AS Coach,
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
            result[day][plan_name]['detail'] = details.split("-")[2:]
    days = [

        "Monday", "Tuesday",
        "Wednesday", "Thursday", "Friday"
        , "Saturday", "Sunday"
    ]
    coach = frappe.db.get_all("Gym Coach", fields=["user.user_image", "no_student", "user.full_name", "rate"],
                              order_by="no_student desc")

    Feedback_query = """
    SELECT
        GF.feedback,
        GF.rate,
        Contact.full_name,
        Contact.image
        
    FROM 
        `tabGym Feedback` AS GF
    JOIN 
        `tabGym Member` AS GM
    ON
        GF.user = GM.name
    JOIN 
        `tabContact` AS Contact
    ON
        Contact.name = GM.customer
    ORDER BY GF.rate DESC
   LIMIT 5
    """
    context["no_coach"] = len(coach)  # frappe.db.count("Gym Coach")
    context["all_coach"] = coach[:3]
    context["feedbacks"] = frappe.db.sql(Feedback_query, as_dict=1)
    context["no_material"] = frappe.db.count("Gym Facility", {"facility_type": "Material"})
    context["no_plan"] = frappe.db.count("Gym Workout Plan")
    context["no_customer"] = frappe.db.count("Gym Member")
    context["plans"] = dict(result).items()
    context["days"] = sorted(result.keys(), key=lambda x: days.index(x))
