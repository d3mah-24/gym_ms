# Copyright (c) 2024, Ahmed and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import add_to_date


class GymMembership(Document):
    def before_save(self):
        self.total_price = frappe.get_value(
            "Gym Workout Plan", filters={"name": self.plan}, fieldname="price"
        )
        months={
			"1 Month":1,
			"3 Month":3,
			"6 Month":6,
			"1 Year":12,
		}
        after_days = add_to_date(self.start_date, months=months[self.duration], as_string=True)
        self.end_date=after_days
        print(after_days)
        print(self.total_price)
