frappe.ui.form.on("Gym Coach", "onload", function(frm){
    frm.set_query("user", function(){ 
        return {
            filters: {
                "ignore_user_type": 1
            }
        }
    });
});