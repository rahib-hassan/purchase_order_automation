import frappe

def create_purchase_order(doc, event):
    sales_order_items = frappe.get_all(
        "Sales Order Item",
        filters={"parent": doc.name},
        fields=["item_code", "qty", "rate", "custom_custom_supplier"]
    )

    supplier_groups = {}
    for item in sales_order_items:
        supplier = item.get("custom_custom_supplier")
        if supplier not in supplier_groups:
            supplier_groups[supplier] = []
        supplier_groups[supplier].append(item)

    for supplier, items in supplier_groups.items():
        purchase_order = frappe.get_doc({
            "doctype": "Purchase Order",
            "supplier": supplier,
            "schedule_date": doc.delivery_date,
            "items": []
        })

        for item in items:
            purchase_order.append("items", {
                "item_code": item.get("item_code"),
                "qty": item.get("qty"),
                "rate": item.get("rate"),
            })

        purchase_order.insert(ignore_permissions=True)
        purchase_order.submit()

        frappe.msgprint(f"Purchase Order created for Supplier {supplier}")

