from collections import defaultdict
import frappe
from frappe import _
from frappe.utils import escape_html
from frappe.website.utils import is_signup_disabled


@frappe.whitelist(allow_guest=True)
def get_shift(**kwargs): 
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
    return dict(grouped_data)


@frappe.whitelist(allow_guest=True)
def custom_delete(**kwargs):
    name = kwargs["name"] 
    doc = kwargs["doc"]
    doc = frappe.get_doc(doc, name)
    if doc.docstatus == 1:
        doc.cancel() 
    doc.delete(delete_permanently=1, force=1)
    
    frappe.db.commit() 



@frappe.whitelist(allow_guest=True)
def delete(**kwargs):
    doctype = kwargs["doc"]
    name = kwargs["name"]
    doc = frappe.get_doc(doctype=doctype, name=name)
    if doc:
        try:
            for field in doc.meta.fields:
                if field.fieldtype == "Link":
                    linked_docname = doc.get_db_value(field.fieldname)
                    if linked_docname:
                        linked_doc = frappe.get_doc(field.options, linked_docname)
                        if linked_doc:
                            if linked_doc.docstatus == 1:
                                linked_doc.cancel()
                            linked_doc.delete(delete_permanently=1, force=1)
                            frappe.db.commit()

            other_doc = frappe.get_list(
                doctype="Gym Membership", filters={"customer": doc.name}
            )
            for docc in other_doc:
                temp = frappe.get_doc("Gym Membership", docc.name)
                if temp.docstatus == 1:
                    temp._cancel()
                temp.delete(delete_permanently=1, force=1)
            doc.delete(delete_permanently=1, force=1)
            frappe.db.commit()
        except Exception as e:
            print(e)
        return f"{doctype} '{name}' and its linked documents deleted successfully"
    else:
        return f"{doctype} '{name}' not found"


@frappe.whitelist(allow_guest=True)
def sign_up(*args, **kwargs):
    if is_signup_disabled():
        frappe.throw(_("Sign Up is disabled"), title=_("Not Allowed"))

    user = frappe.db.get("User", {"email": kwargs["email"]})
    if user:
        if user.enabled:
            return 0, _("Already Registered")
        else:
            return 0, _("Registered but disabled")
    else:
        if frappe.db.get_creation_count("User", 60) > 300:
            frappe.respond_as_web_page(
                _("Temporarily Disabled"),
                _(
                    "Too many users signed up recently, so the registration is disabled. Please try back in an hour"
                ),
                http_status_code=429,
            )

        from frappe.utils import random_string

        user = frappe.get_doc(
            {
                "doctype": "User",
                "email": kwargs["email"],
                "first_name": escape_html(kwargs["first_name"]),
                "username": escape_html(kwargs["username"]),
                "enabled": 1,
                "new_password": kwargs["password"],
                "user_type": "Website User",
                "roles": [{"role": "Gym Member"}],
            }
        )

        user.flags.ignore_permissions = True
        user.flags.ignore_password_policy = True
        user.insert()
        redirect_to = kwargs["redirect_to"] or "/login#login"
        if redirect_to:
            frappe.cache.hset("redirect_after_login", user.name, redirect_to)

        if user.flags.email_sent:
            return 1, _("Please check your email for verification")
        else:
            return 2, _("Account Successfully Created"), redirect_to
