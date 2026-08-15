import unittest

from utils.sort_boxes import sort_texts_by_boxes


class SortTextsByBoxesTests(unittest.TestCase):
    def test_orders_rows_then_columns(self):
        texts = ["B", "A", "C"]
        boxes = [
            [10, 0, 20, 10],
            [0, 0, 5, 10],
            [0, 20, 5, 30],
        ]

        result = sort_texts_by_boxes(texts, boxes, 0.3)

        self.assertEqual(result, ["A", "B", "C"])

    def test_returns_empty_list_for_empty_input(self):
        self.assertEqual(sort_texts_by_boxes([], [], 0.3), [])

    def test_rejects_mismatched_lengths(self):
        with self.assertRaises(ValueError):
            sort_texts_by_boxes(["A"], [], 0.3)


if __name__ == "__main__":
    unittest.main()
