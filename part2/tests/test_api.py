import unittest
import json

from hbnb import create_app


class HBNBApiTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app({"TESTING": True})
        self.client = self.app.test_client()

    def post_json(self, path, payload):
        return self.client.post(path, data=json.dumps(payload), content_type="application/json")

    def put_json(self, path, payload):
        return self.client.put(path, data=json.dumps(payload), content_type="application/json")

    def test_users_crud_and_validation(self):
        # missing email
        r = self.post_json('/api/v1/users', {'password': 'pw'})
        self.assertEqual(r.status_code, 400)
        # missing password
        r = self.post_json('/api/v1/users', {'email': 'a@b.com'})
        self.assertEqual(r.status_code, 400)
        # create
        r = self.post_json('/api/v1/users', {'email': 'a@b.com', 'password': 'pw'})
        self.assertEqual(r.status_code, 201)
        u = r.get_json()
        self.assertIn('id', u)
        self.assertNotIn('password', u)
        uid = u['id']
        # list
        r = self.client.get('/api/v1/users')
        self.assertEqual(r.status_code, 200)
        users = r.get_json()
        self.assertTrue(any(x['id'] == uid for x in users))
        # update
        r = self.put_json(f'/api/v1/users/{uid}', {'first_name': 'Alice'})
        self.assertEqual(r.status_code, 200)
        u2 = r.get_json()
        self.assertEqual(u2.get('first_name'), 'Alice')

    def test_amenity_crud(self):
        # missing name
        r = self.post_json('/api/v1/amenities', {})
        self.assertEqual(r.status_code, 400)
        # create
        r = self.post_json('/api/v1/amenities', {'name': 'Pool'})
        self.assertEqual(r.status_code, 201)
        a = r.get_json(); aid = a['id']
        # list
        r = self.client.get('/api/v1/amenities')
        self.assertEqual(r.status_code, 200)
        items = r.get_json()
        self.assertTrue(any(x['id'] == aid for x in items))
        # get
        r = self.client.get(f'/api/v1/amenities/{aid}')
        self.assertEqual(r.status_code, 200)
        # update
        r = self.put_json(f'/api/v1/amenities/{aid}', {'name': 'Big Pool'})
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.get_json().get('name'), 'Big Pool')

    def test_place_validation_and_relations(self):
        # create user and amenity
        r = self.post_json('/api/v1/users', {'email': 'owner@example.com', 'password': 'pw'})
        owner = r.get_json(); uid = owner['id']
        r = self.post_json('/api/v1/amenities', {'name': 'Wifi'})
        aid = r.get_json()['id']
        # missing user_id (new validation): should fail
        r = self.post_json('/api/v1/places', {'name': 'NoOwner'})
        self.assertEqual(r.status_code, 400)
        # missing name
        r = self.post_json('/api/v1/places', {'user_id': uid})
        self.assertEqual(r.status_code, 400)
        # invalid price
        r = self.post_json('/api/v1/places', {'name': 'P', 'price_by_night': -5})
        self.assertEqual(r.status_code, 400)
        # create valid place
        payload = {'name': 'P', 'user_id': uid, 'amenity_ids': [aid], 'price_by_night': 10, 'latitude': 1.2, 'longitude': 3.4}
        r = self.post_json('/api/v1/places', payload)
        self.assertEqual(r.status_code, 201)
        p = r.get_json(); pid = p['id']
        # place includes owner and amenities
        r = self.client.get(f'/api/v1/places/{pid}')
        self.assertEqual(r.status_code, 200)
        p2 = r.get_json()
        self.assertIn('owner', p2)
        self.assertEqual(p2['owner']['id'], uid)
        self.assertTrue(isinstance(p2.get('amenities', []), list))
        # update price
        r = self.put_json(f'/api/v1/places/{pid}', {'price_by_night': 20})
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.get_json().get('price_by_night'), 20)

    def test_review_crud_and_place_includes_reviews(self):
        # create user and place
        r = self.post_json('/api/v1/users', {'email': 'ru@example.com', 'password': 'pw'})
        uid = r.get_json()['id']
        r = self.post_json('/api/v1/places', {'name': 'RPlace', 'user_id': uid})
        pid = r.get_json()['id']
        # create review
        r = self.post_json('/api/v1/reviews', {'user_id': uid, 'place_id': pid, 'text': 'Nice'})
        self.assertEqual(r.status_code, 201)
        rev = r.get_json(); rid = rev['id']
        # get
        r = self.client.get(f'/api/v1/reviews/{rid}'); self.assertEqual(r.status_code, 200)
        # place includes review
        r = self.client.get(f'/api/v1/places/{pid}'); self.assertEqual(r.status_code, 200)
        place = r.get_json(); self.assertTrue(any(x['id'] == rid for x in place.get('reviews', [])))
        # update review
        r = self.put_json(f'/api/v1/reviews/{rid}', {'text': 'Updated'})
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.get_json().get('text'), 'Updated')
        # delete
        r = self.client.delete(f'/api/v1/reviews/{rid}')
        self.assertEqual(r.status_code, 204)
        # now 404
        r = self.client.get(f'/api/v1/reviews/{rid}')
        self.assertEqual(r.status_code, 404)


if __name__ == '__main__':
    unittest.main()
