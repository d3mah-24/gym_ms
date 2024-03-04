 
frappe.ui.form.on("Gym Member", "onload", function(frm){
    frm.set_query("customer", function(){ 
        return {
            filters: {
                "ignore_user_type": 1
            }
        }
    });
});