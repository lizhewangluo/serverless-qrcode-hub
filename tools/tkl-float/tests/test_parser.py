import unittest
import sys
import os

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'app'))

from parser import TaokoulingParser, InvalidInputError

class TestTaokoulingParser(unittest.TestCase):
    """Test cases for TaokoulingParser"""
    
    def setUp(self):
        self.parser = TaokoulingParser()
    
    def test_extract_codes_yuan_format(self):
        """Test extracting ￥xxx￥ format"""
        text = "这里有￥ABC123￥淘口令"
        codes = self.parser.extract_codes(text)
        self.assertEqual(codes, ["ABC123"])
    
    def test_extract_codes_euro_format(self):
        """Test extracting €xxx€ format"""
        text = "分享€DEF456€淘口令"
        codes = self.parser.extract_codes(text)
        self.assertEqual(codes, ["DEF456"])
    
    def test_extract_codes_slash_format(self):
        """Test extracting 9/xxx/ format"""
        text = "优惠9/GHI789/淘口令"
        codes = self.parser.extract_codes(text)
        self.assertEqual(codes, ["GHI789"])
    
    def test_extract_codes_multiple(self):
        """Test extracting multiple codes"""
        text = "￥ABC123￥和€DEF456€还有9/GHI789/"
        codes = self.parser.extract_codes(text)
        self.assertEqual(set(codes), {"ABC123", "DEF456", "GHI789"})
    
    def test_extract_codes_duplicates(self):
        """Test extracting duplicate codes"""
        text = "￥ABC123￥和￥ABC123￥"
        codes = self.parser.extract_codes(text)
        self.assertEqual(codes, ["ABC123"])
    
    def test_extract_codes_empty(self):
        """Test extracting from empty text"""
        codes = self.parser.extract_codes("")
        self.assertEqual(codes, [])
    
    def test_extract_codes_none(self):
        """Test extracting from None text"""
        codes = self.parser.extract_codes(None)
        self.assertEqual(codes, [])
    
    def test_normalize_code_valid(self):
        """Test normalizing valid code"""
        code = self.parser.normalize_code("  ABC123  ")
        self.assertEqual(code, "ABC123")
    
    def test_normalize_code_with_dash(self):
        """Test normalizing code with dash"""
        code = self.parser.normalize_code("ABC-123")
        self.assertEqual(code, "ABC-123")
    
    def test_normalize_code_with_underscore(self):
        """Test normalizing code with underscore"""
        code = self.parser.normalize_code("ABC_123")
        self.assertEqual(code, "ABC_123")
    
    def test_normalize_code_empty(self):
        """Test normalizing empty code"""
        with self.assertRaises(InvalidInputError):
            self.parser.normalize_code("")
    
    def test_normalize_code_invalid_chars(self):
        """Test normalizing code with invalid characters"""
        with self.assertRaises(InvalidInputError):
            self.parser.normalize_code("ABC@123")
    
    def test_normalize_code_whitespace_only(self):
        """Test normalizing whitespace-only code"""
        with self.assertRaises(InvalidInputError):
            self.parser.normalize_code("   ")

if __name__ == "__main__":
    unittest.main()