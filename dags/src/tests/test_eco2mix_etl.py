import unittest
from datetime import datetime
from unittest.mock import patch
import io   
from dags.src.main.update_data import get_last_date, fetch_data, repair_data, del_excel_files
import os

class TestGetLastDate(unittest.TestCase):

    @patch('dags.src.main.update_data.datetime')
    def test_get_last_date(self, mock_datetime):
        # Mock la date actuelle pour être le 16 juin 2024
        mock_datetime.now.return_value = datetime(2024, 6, 16)
        
        # Appeler la fonction
        day, month, year = get_last_date()
        
        # Vérifier les résultats
        self.assertEqual(day, 15)
        self.assertEqual(month, '06')
        self.assertEqual(year, 2024)
    
    @patch('dags.src.main.update_data.datetime')
    def test_get_last_date_single_digit_day_month(self, mock_datetime):
        # Mock la date actuelle pour être le 1er mars 2024
        mock_datetime.now.return_value = datetime(2024, 3, 1)
        
        # Appeler la fonction
        day, month, year = get_last_date()
        
        # Vérifier les résultats
        self.assertEqual(day, 29)
        self.assertEqual(month, '02')
        self.assertEqual(year, 2024)
    
    @patch('dags.src.main.update_data.datetime')
    def test_get_last_date_new_year(self, mock_datetime):
        # Mock la date actuelle pour être le 1er janvier 2024
        mock_datetime.now.return_value = datetime(2024, 1, 1)
        
        # Appeler la fonction
        day, month, year = get_last_date()
        
        # Vérifier les résultats
        self.assertEqual(day, 31)
        self.assertEqual(month, 12)
        self.assertEqual(year, 2023)


class TestFetchData(unittest.TestCase):

    @patch('dags.src.main.update_data.datetime')
    def test_fetch_data(self, mock_datetime):

        mock_datetime.now.return_value = datetime(2024, 6, 9)
        day, month, year = get_last_date()      

        self.assertEqual(day, "08")
        self.assertEqual(month, "06")
        self.assertEqual(year, 2024)

        fetch_data(day, month, year)
        
        self.assertTrue(os.path.exists(f"./data/eCO2mix_RTE_{year}-{month}-{day}.xls"))
        del_excel_files(day, month, year)
        
    
class TestCleanData(unittest.TestCase):

    @patch('dags.src.main.update_data.datetime')
    def test_repair_data(self, mock_datetime):

        ...

    @patch('dags.src.main.update_data.datetime')
    def test_del_excel_files(self, mock_datetime):

        mock_datetime.now.return_value = datetime(2024, 6, 9)
        day, month, year = get_last_date()      

        self.assertEqual(day, "08")
        self.assertEqual(month, "06")
        self.assertEqual(year, 2024)

        fetch_data(day, month, year)
        repair_data(day, month, year)
        del_excel_files(day, month, year)
        
        self.assertFalse(os.path.exists(f"./data/eCO2mix_RTE_{year}-{month}-{day}.xls"))
        self.assertFalse(os.path.exists(f"./data/eCO2mix_RTE_{year}-{month}-{day}_repaired.xls"))


if __name__ == '__main__':
    unittest.main()
