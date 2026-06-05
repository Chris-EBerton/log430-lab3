"""
Tests for orders manager
SPDX - License - Identifier: LGPL - 3.0 - or -later
Auteurs : Gabriel C. Ullmann, Fabio Petrillo, 2025
"""

import json
import pytest
from store_manager import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_health(client):
    result = client.get('/health-check')
    assert result.status_code == 200
    assert result.get_json() == {'status':'ok'}

def test_stock_flow(client):
    #  Création  article (`POST /products`)
    product_data = {'name': 'Some Item', 'sku': '12345', 'price': 99.90}
    response = client.post('/products',
                          data=json.dumps(product_data),
                          content_type='application/json')
    
    assert response.status_code == 201
    data = response.get_json()
    assert data['product_id'] > 0 
    product_id = data['product_id']

    #  Ajout 5 unités article (`POST /stocks`)
    stock_data = {'product_id': product_id, 'quantity': 5}
    response = client.post('/stocks',
                          data=json.dumps(stock_data),
                          content_type='application/json')
    assert response.status_code == 201
    
    #  Vérification du  stock, votre article devra avoir 5 unités dans le stock (`GET /stocks/:id`)
    response = client.get(f'/stocks/{product_id}')
    assert response.status_code == 200
    stock_info = response.get_json()
    assert stock_info['quantity'] == 5
    """
    # Create a user for the order
    user_data = {'name': 'Test User', 'email': 'test@example.com'}
    response = client.post('/users',
                          data=json.dumps(user_data),
                          content_type='application/json')
    assert response.status_code == 201
    user_id = response.get_json()['user_id']
    """
    
    # Commande de l'article : 2 unités (`POST /orders`)
    order_data = {
        'user_id': 1,
        'items': [
            {
                'product_id': product_id,
                'quantity': 2,
                'unit_price': 99.90
            }
        ]
    }
    response = client.post('/orders',
                          data=json.dumps(order_data),
                          content_type='application/json')
    assert response.status_code == 201
    order_id = response.get_json()['order_id']
    
    # Vérification du stock (`GET /stocks/:id`)
    response = client.get(f'/stocks/{product_id}')
    assert response.status_code == 200
    stock_info = response.get_json()
    assert stock_info['quantity'] == 3  # 5 - 2 = 3
    
    # Suppression  commande et verification du  stock post delete. 
    # Résultat attendu :  augmentation.
    response = client.delete(f'/orders/{order_id}')
    assert response.status_code == 200
    assert response.get_json()['deleted'] == True
    
    # Verify stock is back to 5
    response = client.get(f'/stocks/{product_id}')
    assert response.status_code == 200
    stock_info = response.get_json()
    assert stock_info['quantity'] == 5