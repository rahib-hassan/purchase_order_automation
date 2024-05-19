import frappe
from frappe.utils import add_days

def create_purchase_order(doc, event):
    sales_order_items = frappe.get_all(
        "Sales Order Item",
        filters={"parent": doc.name},
        fields=["item_code", "qty", "rate", "custom_custom_supplier"]
    )

    supplier_groups = {}
    for item in sales_order_items:
        supplier = item.get("custom_custom_supplier")
        if supplier and (supplier not in supplier_groups):
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



@frappe.whitelist(allow_guest=True)
def make_sales_order(**args):
	so = frappe.new_doc("Sales Order")
	args = frappe._dict(args)
	if args.transaction_date:
		so.transaction_date = args.transaction_date

	so.set_warehouse = ""
	so.company = args.company
	so.customer = args.customer
	so.currency = args.currency
	if args.selling_price_list:
		so.selling_price_list = args.selling_price_list

	if args.item_list:
		for item in args.item_list:
			so.append("items", item)

	else:
		so.append(
			"items",
			{
				"item_code": args.item or args.item_code,
				"warehouse": args.warehouse,
				"qty": args.qty or 10,
				"uom": args.uom or None,
				"price_list_rate": args.price_list_rate or None,
				"discount_percentage": args.discount_percentage or None,
				"rate": args.rate or (None if args.price_list_rate else 100),
			},
		)

	so.delivery_date = add_days(so.transaction_date, 10)

	so.save(ignore_permissions=True)
	so.submit()

	return so