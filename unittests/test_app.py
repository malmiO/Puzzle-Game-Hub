import unittest
from unittest.mock import patch, MagicMock
import json
from datetime import datetime

# Import your modules
import db
from app import handle_player_answer

# ---------------------------------------------
# Test 1: Saving player answers to the database
# ---------------------------------------------

class TestSavePlayerAnswer(unittest.TestCase):

    @patch('db.get_db_connection')
    def test_save_player_answer_success(self, mock_get_db_connection):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_db_connection.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        player_name = "TestPlayer"
        correct_solution = [0, 4, 7, 5, 2, 6, 1, 3]

        db.save_player_answer(player_name, correct_solution)

        mock_get_db_connection.assert_called_once()
        mock_conn.cursor.assert_called_once()
        mock_cursor.execute.assert_called_once_with(
            '''
    INSERT INTO player_answers (player_name, correct_solution, created_at)
    VALUES (%s, %s, %s)
    ''',
            (player_name, json.dumps(correct_solution), unittest.mock.ANY)
        )
        mock_conn.commit.assert_called_once()
        mock_conn.close.assert_called_once()

    @patch('db.get_db_connection')
    def test_save_player_answer_failure(self, mock_get_db_connection):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_db_connection.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.execute.side_effect = Exception("DB Insert Error")

        player_name = "TestPlayer"
        correct_solution = [0, 4, 7, 5, 2, 6, 1, 3]

        with self.assertRaises(Exception):
            db.save_player_answer(player_name, correct_solution)

# ---------------------------------------------
# Test 2: Reset after all solutions are found
# ---------------------------------------------

class TestResetAfterAllSolutionsFound(unittest.TestCase):

    @patch('db.reset_player_solutions')
    @patch('db.count_unique_player_solutions')
    def test_reset_when_all_solutions_found(self, mock_count_unique_solutions, mock_reset_player_solutions):
        mock_count_unique_solutions.return_value = 92

        if db.count_unique_player_solutions() >= 92:
            db.reset_player_solutions()

        mock_reset_player_solutions.assert_called_once()

    @patch('db.reset_player_solutions')
    @patch('db.count_unique_player_solutions')
    def test_no_reset_if_not_all_solutions_found(self, mock_count_unique_solutions, mock_reset_player_solutions):
        mock_count_unique_solutions.return_value = 50

        if db.count_unique_player_solutions() >= 92:
            db.reset_player_solutions()

        mock_reset_player_solutions.assert_not_called()

# ---------------------------------------------
# Test 3: Solution already recognized warning
# ---------------------------------------------

class TestSolutionRecognition(unittest.TestCase):

    @patch('app.save_player_answer')
    @patch('app.is_solution_recognized')
    @patch('app.player_solution_exists', return_value=False)
    @patch('app.is_solved', return_value=True)
    @patch('app.count_queens', return_value=8)
    @patch('app.st')
    def test_solution_already_recognized(self, mock_st, mock_count_queens, mock_is_solved, mock_player_solution_exists, 
                                         mock_is_solution_recognized, mock_save_player_answer):
        player_name = "Test Player"
        current_solution = [0, 4, 7, 5, 2, 6, 1, 3]

        mock_is_solution_recognized.return_value = True

        handle_player_answer(player_name, current_solution)

        mock_is_solution_recognized.assert_called_once_with(current_solution)
        mock_st.warning.assert_called_with("This solution has already been recognized by another player. Try a new one.")
        mock_save_player_answer.assert_not_called()

# ---------------------------------------------
# Run all tests
# ---------------------------------------------

if __name__ == '__main__':
    unittest.main()

    
