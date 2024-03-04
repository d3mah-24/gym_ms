
frappe.ui.form.on("Gym Payment", "onload", function(frm){
    frm.set_query("user", function(){
        return {
            filters: {
                "ignore_user_type": 1
            }
        }
    });
});