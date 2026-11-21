import unittest

import gspread
import gspread.utils as utils


class UtilsTest(unittest.TestCase):
    def test_extract_id_from_url(self):
        url_id_list = [
            # New-style url
            (
                "https://docs.google.com/spreadsheets/d/"
                "1qpyC0X3A0MwQoFDE8p-Bll4hps/edit#gid=0",
                "1qpyC0X3A0MwQoFDE8p-Bll4hps",
            ),
            (
                "https://docs.google.com/spreadsheets/d/"
                "1qpyC0X3A0MwQoFDE8p-Bll4hps/edit",
                "1qpyC0X3A0MwQoFDE8p-Bll4hps",
            ),
            (
                "https://docs.google.com/spreadsheets/d/" "1qpyC0X3A0MwQoFDE8p-Bll4hps",
                "1qpyC0X3A0MwQoFDE8p-Bll4hps",
            ),
            # Old-style url
            (
                "https://docs.google.com/spreadsheet/"
                "ccc?key=1qpyC0X3A0MwQoFDE8p-Bll4hps&usp=drive_web#gid=0",
                "1qpyC0X3A0MwQoFDE8p-Bll4hps",
            ),
        ]

        for url, id in url_id_list:
            self.assertEqual(id, utils.extract_id_from_url(url))

    def test_no_extract_id_from_url(self):
        self.assertRaises(
            gspread.NoValidUrlKeyFound, utils.extract_id_from_url, "http://example.org"
        )

    def test_a1_to_rowcol(self):
        self.assertEqual(utils.a1_to_rowcol("ABC3"), (3, 731))

    def test_rowcol_to_a1(self):
        self.assertEqual(utils.rowcol_to_a1(3, 731), "ABC3")
        self.assertEqual(utils.rowcol_to_a1(1, 104), "CZ1")

    def test_addr_converters(self):
        for row in range(1, 257):
            for col in range(1, 512):
                addr = utils.rowcol_to_a1(row, col)
                r, c = utils.a1_to_rowcol(addr)
                self.assertEqual((row, col), (r, c))

    def test_get_gid(self):
        gid = "od6"
        self.assertEqual(utils.wid_to_gid(gid), "0")
        gid = "osyqnsz"
        self.assertEqual(utils.wid_to_gid(gid), "1751403737")
        gid = "ogsrar0"
        self.assertEqual(utils.wid_to_gid(gid), "1015761654")

    def test_numericise(self):
        self.assertEqual(utils.numericise("faa"), "faa")
        self.assertEqual(utils.numericise("3"), 3)
        self.assertEqual(utils.numericise("3_2"), "3_2")
        self.assertEqual(
            utils.numericise("3_2", allow_underscores_in_numeric_literals=False), "3_2"
        )
        self.assertEqual(
            utils.numericise("3_2", allow_underscores_in_numeric_literals=True), 32
        )
        self.assertEqual(utils.numericise("3.1"), 3.1)
        self.assertEqual(utils.numericise("", empty2zero=True), 0)
        self.assertEqual(utils.numericise("", empty2zero=False), "")
        self.assertEqual(utils.numericise("", default_blank=None), None)
        self.assertEqual(utils.numericise("", default_blank="foo"), "foo")
        self.assertEqual(utils.numericise(""), "")
        self.assertEqual(utils.numericise(None), None)

        # test numericise_all
        inputs = ["1", "2", "3"]
        expected = [1, 2, 3]
        self.assertEqual(utils.numericise_all(inputs), expected)

        # skip non digit values
        inputs + ["a"]
        expected + ["a"]
        self.assertEqual(utils.numericise_all(inputs), expected)

        # skip ignored columns
        inputs + ["5", "5"]
        expected + ["5", 5]
        self.assertEqual(utils.numericise_all(inputs, ignore=[5]), expected)

        # provide explicit `None` as ignored list
        self.assertEqual(utils.numericise_all(inputs, ignore=None), expected)

    def test_a1_to_grid_range_simple(self):
        expected_single_dimension = {
            "startRowIndex": 0,
            "endRowIndex": 10,
            "startColumnIndex": 0,
            "endColumnIndex": 1,
        }
        actual_single_dimension = utils.a1_range_to_grid_range("A1:A10")

        expected_two_dimensional = {
            "startRowIndex": 2,
            "endRowIndex": 4,
            "startColumnIndex": 0,
            "endColumnIndex": 2,
        }
        actual_two_dimensional = utils.a1_range_to_grid_range("A3:B4")

        expected_with_sheet_id = {
            "sheetId": 0,
            "startRowIndex": 0,
            "endRowIndex": 10,
            "startColumnIndex": 0,
            "endColumnIndex": 1,
        }
        actual_with_sheet_id = utils.a1_range_to_grid_range("A1:A10", sheet_id=0)

        self.assertEqual(actual_single_dimension, expected_single_dimension)
        self.assertEqual(actual_two_dimensional, expected_two_dimensional)
        self.assertEqual(actual_with_sheet_id, expected_with_sheet_id)

    def test_a1_to_grid_range_unbounded(self):
        expected_unbounded = {
            "startRowIndex": 4,
            "startColumnIndex": 0,
            "endColumnIndex": 2,
        }
        actual_unbounded = utils.a1_range_to_grid_range("A5:B")

        expected_full_columns = {"startColumnIndex": 0, "endColumnIndex": 2}
        actual_full_columns = utils.a1_range_to_grid_range("A:B")

        expected_with_sheet_id = {
            "sheetId": 0,
            "startRowIndex": 4,
            "startColumnIndex": 0,
            "endColumnIndex": 2,
        }
        actual_with_sheet_id = utils.a1_range_to_grid_range("A5:B", sheet_id=0)

        self.assertEqual(actual_unbounded, expected_unbounded)
        self.assertEqual(actual_full_columns, expected_full_columns)
        self.assertEqual(actual_with_sheet_id, expected_with_sheet_id)

    def test_a1_to_grid_range_improper_range(self):
        expected_single_cell = {
            "startRowIndex": 0,
            "endRowIndex": 1,
            "startColumnIndex": 0,
            "endColumnIndex": 1,
        }
        actual_single_cell = utils.a1_range_to_grid_range("A1")

        expected_single_column = {"startColumnIndex": 0, "endColumnIndex": 1}
        actual_single_column = utils.a1_range_to_grid_range("A")

        expected_single_row = {"startRowIndex": 0, "endRowIndex": 1}
        actual_single_row = utils.a1_range_to_grid_range("1")

        expected_with_sheet = {
            "sheetId": 0,
            "startRowIndex": 0,
            "endRowIndex": 1,
            "startColumnIndex": 0,
            "endColumnIndex": 1,
        }
        actual_with_sheet = utils.a1_range_to_grid_range("A1", sheet_id=0)

        self.assertEqual(actual_single_cell, expected_single_cell)
        self.assertEqual(actual_single_column, expected_single_column)
        self.assertEqual(actual_single_row, expected_single_row)
        self.assertEqual(actual_with_sheet, expected_with_sheet)

    def test_a1_to_grid_range_other_directions(self):
        from_top_left = utils.a1_range_to_grid_range("C2:D4")
        from_bottom_right = utils.a1_range_to_grid_range("D4:C2")
        from_top_right = utils.a1_range_to_grid_range("D2:C4")
        from_bottom_left = utils.a1_range_to_grid_range("C4:D2")

        self.assertEqual(from_top_left, from_bottom_right)
        self.assertEqual(from_top_left, from_bottom_left)
        self.assertEqual(from_top_left, from_top_right)

    def test_column_letter_to_index(self):
        # All the input values to test one after an other
        # [0] input value
        # [1] expected return value
        # [2] expected exception to raise
        inputs = [
            ("", None, gspread.exceptions.InvalidInputValue),
            ("A", 1, None),
            ("Z", 26, None),
            ("AA", 27, None),
            ("AAA", 703, None),
            ("ABCDEFGHIJKLMNOPQRSTUVWXYZ", 256094574536617744129141650397448476, None),
            ("!@#$%^&*()", None, gspread.exceptions.InvalidInputValue),
        ]

        for label, expected, exception in inputs:
            if exception is not None:
                # assert the exception is raised
                with self.assertRaises(exception):
                    utils.column_letter_to_index(label)
            else:
                # assert the return values is correct
                result = utils.column_letter_to_index(label)
                self.assertEqual(
                    result,
                    expected,
                    "could not convert column letter '{}' to the right value '{}".format(
                        label, expected
                    ),
                )

    def test_combine_merge_values(self):
        sheet_data = [
            [1, None, None, None],
            [None, None, "title", None],
            [None, None, 2, None],
            ["num", "val", None, 0],
        ]
        sheet_metadata = {
            "properties": {"sheetId": 0},
            "merges": [
                {
                    "startRowIndex": 0,
                    "endRowIndex": 2,
                    "startColumnIndex": 0,
                    "endColumnIndex": 2,
                },
                {
                    "startRowIndex": 1,
                    "endRowIndex": 2,
                    "startColumnIndex": 2,
                    "endColumnIndex": 4,
                },
                {
                    "startRowIndex": 2,
                    "endRowIndex": 4,
                    "startColumnIndex": 2,
                    "endColumnIndex": 3,
                },
            ],
        }
        expected_combine = [
            [1, 1, None, None],
            [1, 1, "title", "title"],
            [None, None, 2, None],
            ["num", "val", 2, 0],
        ]

        actual_combine = utils.combined_merge_values(sheet_metadata, sheet_data, 0, 0)

        self.assertEqual(actual_combine, expected_combine)

    def test_convert_colors_to_hex_value(self):
        color = {"red": 1, "green": 0.49803922, "blue": 0}
        expected_hex = "#FF7F00"

        # successful convert from colors
        hex = utils.convert_colors_to_hex_value(**color)
        self.assertEqual(hex, expected_hex)

        # successful convert from partial input
        hex = utils.convert_colors_to_hex_value(green=1)
        self.assertEqual(hex, "#00FF00")

        # throw ValueError on color values out of range (0-1)
        with self.assertRaises(ValueError):
            utils.convert_colors_to_hex_value(1.23, 0, -50)

    def test_combine_merge_values_outside_range(self):
        """Make sure that merges outside the range of the sheet are ignored or partially ignored
        see issue #1298
        """
        sheet_data = [
            [1, None, None, None],
            [None, None, "title", None],
            [None, None, 2, None],
            ["num", "val", None, 0],
        ]
        sheet_metadata = {
            "properties": {"sheetId": 0},
            "merges": [
                {
                    "startRowIndex": 7,
                    "endRowIndex": 9,
                    "startColumnIndex": 7,
                    "endColumnIndex": 9,
                },
                {
                    "startRowIndex": 3,
                    "endRowIndex": 5,
                    "startColumnIndex": 1,
                    "endColumnIndex": 2,
                },
            ],
        }
        expected_combine = [
            [1, None, None, None],
            [None, None, "title", None],
            [None, None, 2, None],
            ["num", "val", None, 0],
        ]

        actual_combine = utils.combined_merge_values(sheet_metadata, sheet_data, 0, 0)

        self.assertEqual(actual_combine, expected_combine)

    def test_combine_merge_values_from_centre_of_sheet(self):
        """Make sure that merges start from the right index when the sheet is not at the top left
        see issue #1330
        """
        sheet_data = [
            [1, None, None, None],
            [None, None, "title", None],
            [None, None, 2, None],
            ["num", "val", None, 0],
        ]
        sheet_metadata = {
            "properties": {"sheetId": 0},
            "merges": [
                {
                    "startRowIndex": 0,
                    "endRowIndex": 2,
                    "startColumnIndex": 0,
                    "endColumnIndex": 2,
                },
                {
                    "startRowIndex": 1,
                    "endRowIndex": 2,
                    "startColumnIndex": 2,
                    "endColumnIndex": 4,
                },
                {
                    "startRowIndex": 2,
                    "endRowIndex": 4,
                    "startColumnIndex": 2,
                    "endColumnIndex": 3,
                },
            ],
        }
        sheet_data_cropped = [sheet_data[1:] for sheet_data in sheet_data][1:]
        # [None, "title", None],
        # [None, 2, None],
        # ["val", None, 0]
        expected_combined_cropped = [
            [None, "title", "title"],
            [None, 2, None],
            ["val", 2, 0],
        ]

        actual_combine = utils.combined_merge_values(
            sheet_metadata, sheet_data_cropped, start_row_index=1, start_col_index=1
        )

        self.assertEqual(actual_combine, expected_combined_cropped)

    def test_convert_hex_to_color(self):
        hexcolor = "#FF7F00"
        expected_color = {"red": 1, "green": 0.49803922, "blue": 0}

        # successful convert from hex to color
        rgbcolor = utils.convert_hex_to_colors_dict(hexcolor)
        for key, rgbvalue in rgbcolor.items():
            self.assertAlmostEqual(rgbvalue, expected_color[key])

        # successful ignore alpha
        rgbcolor = utils.convert_hex_to_colors_dict(f"{hexcolor}42")
        for key, rgbvalue in rgbcolor.items():
            self.assertAlmostEqual(rgbvalue, expected_color[key])

        # raise ValueError on invalid hex length
        with self.assertRaises(ValueError):
            utils.convert_hex_to_colors_dict("123456abcdef")

        # raise ValueError on invalid hex characters
        with self.assertRaises(ValueError):
            utils.convert_hex_to_colors_dict("axbcde")

    def test_fill_gaps(self):
        """test fill_gaps function"""
        matrix = [
            [1, 2, 3, 4],
            [5, 6, 7, 8],
        ]
        expected = [
            [1, 2, 3, 4, "", ""],
            [5, 6, 7, 8, "", ""],
            ["", "", "", "", "", ""],
        ]
        actual = utils.fill_gaps(matrix, 3, 6)

        self.assertEqual(actual, expected)

    def test_fill_gaps_with_value(self):
        """test fill_gaps function"""
        matrix = [
            [1, 2, 3, 4],
            [5, 6, 7, 8],
        ]
        expected = [
            [1, 2, 3, 4, "a", "a"],
            [5, 6, 7, 8, "a", "a"],
            ["a", "a", "a", "a", "a", "a"],
        ]
        actual = utils.fill_gaps(matrix, 3, 6, "a")

        self.assertEqual(actual, expected)

        expected = [
            [1, 2, 3, 4, 3, 3],
            [5, 6, 7, 8, 3, 3],
            [3, 3, 3, 3, 3, 3],
        ]
        actual = utils.fill_gaps(matrix, 3, 6, 3)

        self.assertEqual(actual, expected)

    def test_fill_gaps_with_non_square_array(self):
        """test fill_gaps function"""
        matrix = [
            [1, 2, 3, 4],
            [5, 6, 7, 8],
            [9],
        ]
        expected = [
            [1, 2, 3, 4, "", "", ""],
            [5, 6, 7, 8, "", "", ""],
            [9, "", "", "", "", "", ""],
            ["", "", "", "", "", "", ""],
        ]
        actual = utils.fill_gaps(matrix, 4, 7)

        self.assertEqual(actual, expected)

    def test_is_full_a1_notation(self):
        """test is_full_a1_notation function"""
        self.assertTrue(utils.is_full_a1_notation("A1:B2"))
        self.assertTrue(utils.is_full_a1_notation("Sheet1!A1:B2"))
        self.assertTrue(utils.is_full_a1_notation("AZ1:BBY2"))
        self.assertTrue(utils.is_full_a1_notation("AZ142:BBY122"))

        self.assertFalse(utils.is_full_a1_notation("Sheet1"))
        self.assertFalse(utils.is_full_a1_notation("A:B"))
        self.assertFalse(utils.is_full_a1_notation("1:2"))
        self.assertFalse(utils.is_full_a1_notation("1:"))
        self.assertFalse(utils.is_full_a1_notation("A1"))
        self.assertFalse(utils.is_full_a1_notation("A"))
        self.assertFalse(utils.is_full_a1_notation("1"))
        self.assertFalse(utils.is_full_a1_notation(""))

    def test_extract_title_from_range(self):
        """test extract_title_from_range function"""
        # quoted title with spaces
        self.assertEqual(
            utils.extract_title_from_range("'Sheet Name'!A1:Z100"), "Sheet Name"
        )
        # unquoted title
        self.assertEqual(utils.extract_title_from_range("Sheet1!A1:Z100"), "Sheet1")
        # quoted title without range
        self.assertEqual(utils.extract_title_from_range("'Sheet''1'!A1:B2"), "Sheet'1")
        self.assertEqual(
            utils.extract_title_from_range("'Sheet''''1'!A1:B2"), "Sheet''1"
        )
        # invalid input raises exception
        with self.assertRaises(gspread.exceptions.InvalidInputValue):
            utils.extract_title_from_range("no_exclamation_mark")

    def test_get_a1_from_absolute_range(self):
        """test get_a1_from_absolute_range function"""
        self.assertEqual(utils.get_a1_from_absolute_range("'Sheet1'!A1:B2"), "A1:B2")
        self.assertEqual(utils.get_a1_from_absolute_range("'Sheet1'!A1:B"), "A1:B")
        self.assertEqual(utils.get_a1_from_absolute_range("Sheet1!A1:B2"), "A1:B2")
        self.assertEqual(utils.get_a1_from_absolute_range("A1:B2"), "A1:B2")
        self.assertEqual(utils.get_a1_from_absolute_range("A1:B"), "A1:B")
        self.assertEqual(utils.get_a1_from_absolute_range("2"), "2")

    def test_to_records_empty_args(self):
        """Test to_records with empty args"""

        self.assertListEqual(utils.to_records([], []), [])
        self.assertListEqual(utils.to_records([], [[]]), [{}])
        self.assertListEqual(utils.to_records(["a1", "b2"], []), [])
        self.assertListEqual(utils.to_records(["a1", "b2"], [[]]), [{}])
        self.assertListEqual(utils.to_records([], [["a1"]]), [{}])
        self.assertListEqual(utils.to_records([], [["a1"], ["a2"]]), [{}, {}])
        self.assertListEqual(utils.to_records([], [[], ["a2"]]), [{}, {}])

    def test_to_records(self):
        """Test to_records with values"""

        headers = ["HA", "HB", "HC"]
        values = [["A2", "B2", "C2"], ["A3", "B3"], ["", "B4", "C4"]]

        records = utils.to_records(headers, values)

        self.assertEqual(len(values), len(records))

        for i in range(len(records)):
            record = records[i]
            keys = record.keys()

            # Some rows have shorter values ("A3", "B3")
            # so the list of keys is smaller
            # but never bigger than the list of headers
            self.assertLessEqual(len(keys), len(headers))

            # Each resulting key must be part of the given header
            for key in keys:
                self.assertIn(key, headers)

                # given key are unordered
                # but they must match a value from the given input values
                self.assertIn(record[key], values[i])

    def test_find_table_simple(self):
        """Test find table with basic case"""
        values = [
            ["A1", "B1", "C1", "D1"],
            ["", "B2", "C2", "", "E2"],
            ["", "B3", "C3", "D3", "E3"],
            ["A4", "", "C4", "D4", "E4"],
        ]

        table = utils.find_table(
            values,
            "B2",
            utils.TableDirection.table,
        )

        table_max_row_max_column = utils.find_table(
            values,
            "D3",
            utils.TableDirection.table,
        )
        right = utils.find_table(
            values,
            "B2",
            utils.TableDirection.right,
        )
        down = utils.find_table(
            values,
            "B2",
            utils.TableDirection.down,
        )
        single = utils.find_table(values, "D1", utils.TableDirection.table)
        no_values = utils.find_table(values, "A2", utils.TableDirection.table)

        table_values = [
            ["B2", "C2"],
            ["B3", "C3"],
        ]

        for rowindex, row in enumerate(table_values):
            self.assertListEqual(row, table[rowindex])

        table_max_row_max_column_values = [
            ["D3", "E3"],
            ["D4", "E4"],
        ]

        for rowindex, row in enumerate(table_max_row_max_column):
            self.assertListEqual(row, table_max_row_max_column_values[rowindex])

        right_values = [
            ["B2", "C2"],
        ]
        for rowindex, row in enumerate(right_values):
            self.assertListEqual(row, right[rowindex])

        bottom_values = [
            ["B2"],
            ["B3"],
        ]
        for rowindex, row in enumerate(bottom_values):
            self.assertListEqual(row, down[rowindex])

        self.assertEqual(len(single), 1)
        self.assertEqual(len(single[0]), 1)
        self.assertEqual(single[0][0], "D1")
        self.assertEqual(no_values, [])

    def test_find_table_inner_gap(self):
        """Test find table with gap in header"""
        values = [
            ["A1", "B1", "C1", ""],
            ["A2", "", "C2", ""],
            ["A3", "B3", "C3", ""],
            ["", "", "", ""],
        ]
        expected_table = [
            ["A1", "B1", "C1"],
            ["A2", "", "C2"],
            ["A3", "B3", "C3"],
        ]

        table = utils.find_table(
            values,
            "A1",
            utils.TableDirection.table,
        )

        for rowindex, row in enumerate(expected_table):
            self.assertListEqual(row, table[rowindex])

    def test_find_table_first_row_gap(self):
        """Test find table with first cell empty"""
        values = [
            ["A1", "", "C1", ""],
            ["A2", "B2", "C2", ""],
            ["A3", "B3", "C3", ""],
            ["", "", "", ""],
        ]
        expected_table = [
            ["A1"],
            ["A2"],
            ["A3"],
        ]

        table = utils.find_table(
            values,
            "A1",
            utils.TableDirection.table,
        )

        for rowindex, row in enumerate(expected_table):
            self.assertListEqual(row, table[rowindex])

    def test_find_table_first_column_gap(self):
        """Test find table with a gap in first column"""
        values = [
            ["A1", "B1", "C1", ""],
            ["", "B2", "C2", ""],
            ["A3", "B3", "C3", ""],
            ["", "", "", ""],
        ]
        expected_table = [
            ["A1", "B1", "C1"],
        ]

        table = utils.find_table(
            values,
            "A1",
            utils.TableDirection.table,
        )

        for rowindex, row in enumerate(expected_table):
            self.assertListEqual(row, table[rowindex])

    def test_find_table_last_column_gap(self):
        """Test find table with a gap in last column"""
        values = [
            ["A1", "B1", "C1", ""],
            ["A2", "B2", "", ""],
            ["A3", "B3", "C3", ""],
            ["", "", "", ""],
        ]
        expected_table = [
            ["A1", "B1", "C1"],
            ["A2", "B2", ""],
            ["A3", "B3", "C3"],
        ]

        table = utils.find_table(
            values,
            "A1",
            utils.TableDirection.table,
        )

        for rowindex, row in enumerate(expected_table):
            self.assertListEqual(row, table[rowindex])

    def test_find_table_empty_top_left_corner(self):
        """Test find table with an empty top left cell and empty adjacent cells"""

        values = [
            ["", "", "C1", ""],
            ["", "B2", "C2", ""],
            ["", "B3", "C3", ""],
        ]

        table = utils.find_table(values, "A1", utils.TableDirection.table)

        self.assertListEqual(table, [], "resulting table should be empty")


class RowDeletionPlanningTest(unittest.TestCase):
    """Tests for the row range merge/subtract/plan helpers."""

    def test_merge_row_ranges_overlapping_unsorted_and_adjacent(self):
        self.assertEqual(
            utils.merge_row_ranges([(5, 9), (2, 4), (8, 12), (20, 20)]),
            [(2, 12), (20, 20)],
        )
        # adjacent ranges collapse into a single contiguous range
        self.assertEqual(utils.merge_row_ranges([(3, 5), (6, 8)]), [(3, 8)])
        # lists and tuples are both accepted, duplicates merge away
        self.assertEqual(utils.merge_row_ranges([[3, 3], (3, 5)]), [(3, 5)])
        self.assertEqual(utils.merge_row_ranges([]), [])

    def test_merge_row_ranges_validation(self):
        malformed = [
            [(1,)],
            [(1, 2, 3)],
            [(0, 2)],
            [(5, 3)],
            [(1, 2.5)],
        ]
        for ranges in malformed:
            with self.assertRaises(ValueError):
                utils.merge_row_ranges(ranges)

    def test_subtract_row_ranges(self):
        base = utils.merge_row_ranges([(1, 10)])
        self.assertEqual(
            utils.subtract_row_ranges(base, [(4, 4), (8, 8)]),
            [(1, 3), (5, 7), (9, 10)],
        )
        # subtracting the whole range leaves nothing
        self.assertEqual(
            utils.subtract_row_ranges(utils.merge_row_ranges([(2, 9)]), [(2, 9)]),
            [],
        )
        # non-overlapping protected ranges leave the base untouched
        self.assertEqual(
            utils.subtract_row_ranges(base, [(20, 30)]),
            [(1, 10)],
        )
        # protected range spanning several merged blocks
        self.assertEqual(
            utils.subtract_row_ranges(
                utils.merge_row_ranges([(1, 4), (6, 10)]), [(3, 7)]
            ),
            [(1, 2), (8, 10)],
        )

    def test_plan_row_deletions_merges_and_subtracts_keep_ranges(self):
        planned = utils.plan_row_deletions(
            [(2, 6), (5, 9)], 20, keep_ranges=[(4, 4), (8, 8)]
        )
        self.assertEqual(planned, [(2, 3), (5, 7), (9, 9)])

    def test_plan_row_deletions_returns_empty_when_keep_covers_everything(self):
        # no request must be needed: empty plan rather than an error
        self.assertEqual(
            utils.plan_row_deletions([(5, 7)], 20, keep_ranges=[(5, 7)]),
            [],
        )
        self.assertEqual(utils.plan_row_deletions([], 20), [])

    def test_plan_row_deletions_rejects_ranges_past_worksheet_size(self):
        with self.assertRaises(ValueError):
            utils.plan_row_deletions([(1, 21)], 20)
        with self.assertRaises(ValueError):
            utils.plan_row_deletions([(1, 5)], 20, keep_ranges=[(19, 21)])

    def test_plan_row_deletions_rejects_deleting_every_row(self):
        # a single rule covering the whole sheet
        with self.assertRaises(ValueError):
            utils.plan_row_deletions([(1, 20)], 20)
        # ... including adjacent rules that together cover every row
        with self.assertRaises(ValueError):
            utils.plan_row_deletions([(1, 10), (11, 15), (16, 20)], 20)
        # keeping at least one row makes the same input acceptable
        self.assertEqual(
            utils.plan_row_deletions([(1, 10), (11, 20)], 20, keep_ranges=[(7, 7)]),
            [(1, 6), (8, 20)],
        )

    def test_plan_row_deletions_rejects_malformed_ranges(self):
        with self.assertRaises(ValueError):
            utils.plan_row_deletions([(0, 3)], 20)
        with self.assertRaises(ValueError):
            utils.plan_row_deletions([(3, 2)], 20)


class RowDeletionMappingTest(unittest.TestCase):
    """Tests for the compact bidirectional row number mapping."""

    def setUp(self):
        # deleted 2-3, 5-7 and 9 out of 12 rows
        self.mapping = utils.RowDeletionMapping([(2, 3), (5, 7), (9, 9)], 12)

    def test_counts_and_deleted_ranges(self):
        self.assertEqual(self.mapping.old_row_count, 12)
        self.assertEqual(self.mapping.new_row_count, 6)
        self.assertEqual(self.mapping.deleted_ranges, [(2, 3), (5, 7), (9, 9)])

    def test_old_to_new(self):
        # survivors old 1,4,8,10,11,12 map to new 1,2,3,4,5,6
        expected = {1: 1, 4: 2, 8: 3, 10: 4, 11: 5, 12: 6}
        for old_row, new_row in expected.items():
            self.assertEqual(self.mapping.old_to_new(old_row), new_row)
        for deleted_row in (2, 3, 5, 6, 7, 9):
            self.assertIsNone(self.mapping.old_to_new(deleted_row))
            self.assertTrue(self.mapping.is_deleted(deleted_row))

    def test_new_to_old_round_trip(self):
        for old_row in range(1, 13):
            new_row = self.mapping.old_to_new(old_row)
            if new_row is not None:
                self.assertEqual(self.mapping.new_to_old(new_row), old_row)
                self.assertFalse(self.mapping.is_deleted(old_row))

    def test_out_of_range_lookups_raise(self):
        for bad_row in (0, 13, -1):
            with self.assertRaises(ValueError):
                self.mapping.old_to_new(bad_row)
            with self.assertRaises(ValueError):
                self.mapping.is_deleted(bad_row)
        for bad_row in (0, 7, 12):
            with self.assertRaises(ValueError):
                self.mapping.new_to_old(bad_row)

    def test_identity_mapping_for_empty_deletion(self):
        identity = utils.RowDeletionMapping([], 5)
        self.assertEqual(identity.new_row_count, 5)
        self.assertEqual(identity.deleted_ranges, [])
        for row in range(1, 6):
            self.assertEqual(identity.old_to_new(row), row)
            self.assertEqual(identity.new_to_old(row), row)
            self.assertFalse(identity.is_deleted(row))

    def test_deletion_at_the_top_and_bottom(self):
        # first and last rows removed, survivors keep a stable relative order
        mapping = utils.RowDeletionMapping([(1, 1), (10, 10)], 10)
        self.assertEqual(mapping.new_row_count, 8)
        self.assertEqual(mapping.old_to_new(2), 1)
        self.assertEqual(mapping.old_to_new(9), 8)
        self.assertEqual(mapping.new_to_old(1), 2)
        self.assertEqual(mapping.new_to_old(8), 9)
        self.assertTrue(mapping.is_deleted(1) and mapping.is_deleted(10))

    def test_exhaustive_round_trip(self):
        # every deletion pattern over small sheets: bidirectional lookups
        # must stay consistent without expanding the full table
        for row_count in range(1, 18):
            for pattern in range(1, (1 << min(row_count, 8))):
                deleted_ranges = []
                start = None
                for index in range(row_count):
                    deleted = bool((pattern >> (index % 8)) & 1)
                    row = index + 1
                    if deleted and start is None:
                        start = row
                    elif not deleted and start is not None:
                        deleted_ranges.append((start, row - 1))
                        start = None
                if start is not None:
                    deleted_ranges.append((start, row_count))
                if (
                    len(deleted_ranges) == 0
                    or len(deleted_ranges) == 1
                    and (deleted_ranges[0] == (1, row_count))
                ):
                    continue
                mapping = utils.RowDeletionMapping(deleted_ranges, row_count)
                survivors = [
                    row
                    for row in range(1, row_count + 1)
                    if not mapping.is_deleted(row)
                ]
                self.assertEqual(mapping.new_row_count, len(survivors))
                for new_row, old_row in enumerate(survivors, start=1):
                    self.assertEqual(mapping.old_to_new(old_row), new_row)
                    self.assertEqual(mapping.new_to_old(new_row), old_row)

    def test_repr_is_compact(self):
        # the representation shows ranges, never one entry per row
        text = repr(self.mapping)
        self.assertIn("RowDeletionMapping", text)
        self.assertIn("(2, 3)", text)
