# -*- coding: utf-8 -*-
from odoo import http, _, exceptions
from odoo.http import request
import json
import  werkzeug.wrappers
from werkzeug.wrappers import Response
import base64
import io
from PIL import Image
from base64 import b64encode, b64decode
import xmlrpc, xmlrpc.client
import logging
_logger = logging.getLogger(__name__)


class ApiDataProduct(http.Controller):
    @http.route(['/api/product'], csrf=False, type='json', auth='public', methods=['POST'], cors='*')        
    def create_product(self, **params):
        name = params.get("name")
        price = params.get("price")
        description = params.get("description")

        vals = {
            'name': name,
            'price': price,
            'description': description
        }
        
        create_product = http.request.env['data_product'].sudo().create(vals)
        header = request.httprequest.headers
        data = {
            'message': 'success',
            'name': name
        }
        return data
    
    @http.route('/api/get_product',csrf=False,cors='*', type='http', auth='public', methods=['GET'])
    def get_product(self, **kwargs):
        product = request.env['data_product'].sudo().search([])
        if product: 
            product_data = []
            for product in product:
                product_data.append({
                    'name': product.name,
                    'price': product.price,
                    'description': product.description
                })
            return request.make_response(json.dumps(product_data), headers={'Content-Type': 'application/json'})
        else:
            return request.make_response(json.dumps({'error': 'Product not found'}), headers={'Content-Type': 'application/json'}, status=404)
        
    @http.route('/api/update_product/<int:id>', csrf=False, cors='*', type='json', auth='public', methods=['PUT'])
    def update_product(self, id, **kwargs):
        product = request.env['data_product'].sudo().search([('id', '=', id)])
        if product:
            data = json.loads(request.httprequest.data)
            product.write({
                'name': data.get('name', product.name),
                'price': data.get('price', product.price),
                'description': data.get('description', product.description)
            })
            response_data = {'success': 'Product updated successfully'}
            return response_data
        else:
            return {'error': 'Product not found'}, 404
        
    @http.route('/api/delete_product/<int:id>', csrf=False, cors='*', type='http', auth='public', methods=['DELETE'])
    def delete_product(self,id, **kwargs):
        product = request.env['data_product'].sudo().search([('id', '=', id)])
        if product: 
            product.unlink()
            return request.make_response(json.dumps({'success': 'Product deleted successfully'}), headers={'Content-Type': 'application/json'})
        else:
            return request.make_response(json.dumps({'error': 'Product not found'}), headers={'Content-Type': 'application/json'}, status=404)
