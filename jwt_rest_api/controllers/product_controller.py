from odoo import http 
from odoo.http import request
from odoo.exceptions import AccessDenied

class ProductController(http.Controller):

    @http.route('/api/products/list',type='json',auth='public',methods=['POST'],csrf=False)
    def get_produts(self):
        jwt_service = request.env['jwt.config'].sudo()
        user = jwt_service.verify_access_token()
        products = request.env['product.product'].with_user(user).search([])
        result = []
        for product in products:
            result.append({
                "id":product.id,
                "name":product.name,
                "sale_price":product.list_price,
                "cost":product.standard_price,
                "internal_reference":product.default_code,
            })
        return {
            "success":True,
            "message":"Products Fetched successfully",
            "count":len(result),
            "data":result
        }
    
    @http.route( '/api/products/create',type='json',auth='public',methods=['POST'],csrf=False)
    def create_products(self,**kwargs):
        jwt_service  = request.env['jwt.config'].sudo()
        user = jwt_service.verify_access_token()
        name  = kwargs.get('name')
        list_price = kwargs.get('list_price',0)
        if not name:
            return{
                "success":False,
                "message":"Product Name is required."
            }
        product = request.env["product.product"].with_user(user).create({
            "name":name,
            "list_price":list_price
        })
        return{
            "success":True,
            "message":"Product Created successfully.",
            "data":{
                "id":product.id,
                "name":product.name,
                "price":product.list_price
            }

        }
        

    @http.route( '/api/products/update/<int:product_id>', auth='public',type='json',methods=["POST"],csrf=False)
    def update_products(self,product_id,**kwargs):
        print("UPDATE API CALLED", product_id)
        jwt_service= request.env['jwt.config'].sudo()
        user = jwt_service.verify_access_token()
        product = request.env['product.product'].with_user(user).browse(product_id)
        if not product.exists():
            return {
                "success": False,
                "message": "Product not found."
            }
        values = {}
        if kwargs.get('name'):
            values['name']= kwargs.get('name')
        if kwargs.get("list_price") is not None:
            values["list_price"] = kwargs.get("list_price")

        product.write(values)
        return {
            "success": True,
            "message": "Product updated successfully."
        }
        

    @http.route( '/api/products/delete/<int:product_id>',type='json',auth='public',methods=['POST'],csrf=False)
    def delete_product(self, product_id):
        jwt_service = request.env["jwt.config"].sudo()
        user = jwt_service.verify_access_token()
        product = request.env["product.product"].with_user(user).browse(product_id)
        if not product.exists():
            return {
                "success": False,
                "message": "Product not found."
            }
        product.unlink()
        return {
            "success": True,
            "message": "Product deleted successfully."
        }