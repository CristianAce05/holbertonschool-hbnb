import unittest

from hbnb.persistence.sqlalchemy_repository import SQLAlchemyRepository, Base


class SQLAlchemyRepositoryIntegrationTest(unittest.TestCase):
    def setUp(self):
        # use in-memory SQLite for fast tests
        self.repo = SQLAlchemyRepository(database_uri="sqlite:///:memory:")
        # create required tables on the repository engine
        Base.metadata.create_all(self.repo._engine)

    def test_crud_lifecycle(self):
        payload = {"name": "TestItem", "value": 123}
        created = self.repo.create("Item", payload)
        self.assertIn("id", created)
        obj_id = created["id"]
        self.assertEqual(created["name"], "TestItem")

        # get
        fetched = self.repo.get("Item", obj_id)
        self.assertIsNotNone(fetched)
        self.assertEqual(fetched["id"], obj_id)

        # list
        items = self.repo.list("Item")
        self.assertTrue(any(i["id"] == obj_id for i in items))

        # update
        updated = self.repo.update("Item", obj_id, {"name": "Updated", "extra": "OK"})
        self.assertIsNotNone(updated)
        self.assertEqual(updated.get("name"), "Updated")
        self.assertEqual(updated.get("extra"), "OK")

        # count
        self.assertEqual(self.repo.count("Item"), 1)

        # list_all
        all_objs = self.repo.list_all()
        self.assertIn("Item", all_objs)

        # delete
        deleted = self.repo.delete("Item", obj_id)
        self.assertTrue(deleted)
        self.assertIsNone(self.repo.get("Item", obj_id))

    def test_clear_and_multiple(self):
        a = self.repo.create("A", {"x": 1})
        b = self.repo.create("A", {"x": 2})
        c = self.repo.create("B", {"y": 3})
        self.assertEqual(self.repo.count("A"), 2)
        self.assertEqual(self.repo.count("B"), 1)
        self.repo.clear()
        self.assertEqual(self.repo.count("A"), 0)
        self.assertEqual(self.repo.count("B"), 0)


if __name__ == "__main__":
    unittest.main()
