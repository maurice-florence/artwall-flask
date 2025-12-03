import unittest
from unittest.mock import MagicMock, patch
from app.services.firebase_service import get_paginated_posts


class TestPagination(unittest.TestCase):
    @patch("app.services.firebase_service.get_db_ref")
    def test_get_paginated_posts_first_page(self, mock_get_db_ref):
        # Mock database reference and query chain
        mock_ref = MagicMock()
        mock_query = MagicMock()
        mock_get_db_ref.return_value = mock_ref
        mock_ref.order_by_key.return_value = mock_query
        mock_query.limit_to_last.return_value = mock_query

        # Mock data: 5 posts (limit 4)
        # Firebase returns ascending by key (oldest first)
        # Keys: 1, 2, 3, 4, 5. Newest is 5.
        mock_data = {
            "1": {"title": "Post 1", "timestamp": 100},
            "2": {"title": "Post 2", "timestamp": 200},
            "3": {"title": "Post 3", "timestamp": 300},
            "4": {"title": "Post 4", "timestamp": 400},
            "5": {"title": "Post 5", "timestamp": 500},
        }
        mock_query.get.return_value = mock_data

        # Call function
        posts, next_cursor = get_paginated_posts(limit=4)

        # Verify results
        # Should return 4 newest posts: 5, 4, 3, 2
        self.assertEqual(len(posts), 4)
        self.assertEqual(posts[0]["id"], "5")
        self.assertEqual(posts[1]["id"], "4")
        self.assertEqual(posts[2]["id"], "3")
        self.assertEqual(posts[3]["id"], "2")

        # Next cursor should be the last item of this page: "2"
        self.assertEqual(next_cursor, "2")

    @patch("app.services.firebase_service.get_db_ref")
    def test_get_paginated_posts_next_page(self, mock_get_db_ref):
        # Mock database reference and query chain
        mock_ref = MagicMock()
        mock_query = MagicMock()
        mock_get_db_ref.return_value = mock_ref
        mock_ref.order_by_key.return_value = mock_query
        mock_query.end_at.return_value = mock_query
        mock_query.limit_to_last.return_value = mock_query

        # Mock data: Previous page ended at "2".
        # We query end_at="2", limit=3 (limit 2 + 1).
        # Should return: 1, 2.
        mock_data = {
            "1": {"title": "Post 1", "timestamp": 100},
            "2": {"title": "Post 2", "timestamp": 200},
        }
        mock_query.get.return_value = mock_data

        # Call function with cursor "2"
        posts, next_cursor = get_paginated_posts(limit=2, end_at="2")

        # Verify results
        # Logic:
        # 1. Receive {1, 2}
        # 2. Sort reverse: [2, 1]
        # 3. Pop "2" (cursor): [1]
        # 4. Return [1]

        self.assertEqual(len(posts), 1)
        self.assertEqual(posts[0]["id"], "1")

        # Next cursor should be None (end of list)
        self.assertIsNone(next_cursor)

    @patch("app.services.firebase_service.get_db_ref")
    def test_get_paginated_posts_middle_page(self, mock_get_db_ref):
        # Mock database reference and query chain
        mock_ref = MagicMock()
        mock_query = MagicMock()
        mock_get_db_ref.return_value = mock_ref
        mock_ref.order_by_key.return_value = mock_query
        mock_query.end_at.return_value = mock_query
        mock_query.limit_to_last.return_value = mock_query

        # Mock data: Middle page.
        # DB has 0, 1, 2, 3.
        # We ask for limit=2, end_at="3".
        # We fetch limit+1 = 3 items ending at 3.
        # Should return 1, 2, 3.
        mock_data = {
            "1": {"title": "Post 1", "timestamp": 100},
            "2": {"title": "Post 2", "timestamp": 200},
            "3": {"title": "Post 3", "timestamp": 300},
        }
        mock_query.get.return_value = mock_data

        # Call function
        posts, next_cursor = get_paginated_posts(limit=2, end_at="3")

        # Verify results
        # Logic:
        # 1. Receive {1, 2, 3}
        # 2. Sort reverse: [3, 2, 1]
        # 3. Pop "3" (cursor): [2, 1]
        # 4. Return [2, 1]

        self.assertEqual(len(posts), 2)
        self.assertEqual(posts[0]["id"], "2")
        self.assertEqual(posts[1]["id"], "1")

        # Next cursor should be "1" because we fetched a full batch (3 items)
        # and we have exactly limit (2) items left.
        self.assertEqual(next_cursor, "1")


if __name__ == "__main__":
    unittest.main()
