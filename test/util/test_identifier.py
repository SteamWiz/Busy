import unittest
import tempfile
from pathlib import Path

from busy.util.identifier import Identifier


class TestIdentifier(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.temp_path = Path(self.temp_dir.name)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_init_valid_address(self):
        """Test constructor with valid address creates counter file"""
        identifier = Identifier('A', str(self.temp_path))
        counter_file = self.temp_path / 'counter'
        self.assertTrue(counter_file.exists())
        with open(counter_file, 'r') as f:
            self.assertEqual(f.read(), '00000')

    def test_init_invalid_address(self):
        """Test constructor with invalid address raises ValueError"""
        with self.assertRaises(ValueError) as cm:
            Identifier('Z', str(self.temp_path))
        self.assertIn("Invalid device address Z", str(cm.exception))

    def test_init_custom_width(self):
        """Test constructor with custom width"""
        identifier = Identifier('0', str(self.temp_path), width=3)
        self.assertEqual(identifier.width, 3)

    def test_encode_normal(self):
        """Test _encode method with normal values"""
        identifier = Identifier('0', str(self.temp_path))
        self.assertEqual(identifier._encode(0), '00000')
        self.assertEqual(identifier._encode(1), '00001')
        self.assertEqual(identifier._encode(32), '00010')

    def test_encode_overflow(self):
        """Test _encode method with overflow raises ValueError"""
        identifier = Identifier('0', str(self.temp_path))
        with self.assertRaises(ValueError) as cm:
            identifier._encode(32 ** 5)
        self.assertIn("exceeds 5 characters", str(cm.exception))

    def test_decode_normal(self):
        """Test _decode method with normal values"""
        identifier = Identifier('0', str(self.temp_path))
        self.assertEqual(identifier._decode('00000'), 0)
        self.assertEqual(identifier._decode('00001'), 1)
        self.assertEqual(identifier._decode('00010'), 32)

    def test_decode_wrong_length(self):
        """Test _decode method with wrong length raises ValueError"""
        identifier = Identifier('0', str(self.temp_path))
        with self.assertRaises(ValueError) as cm:
            identifier._decode('000')
        self.assertIn("must have 5 characters", str(cm.exception))

    def test_decode_invalid_character(self):
        """Test _decode method with invalid character raises ValueError"""
        identifier = Identifier('0', str(self.temp_path))
        with self.assertRaises(ValueError) as cm:
            identifier._decode('0000Z')
        self.assertIn("Invalid base32 character: Z", str(cm.exception))

    def test_increment_normal(self):
        """Test increment method normal operation"""
        identifier = Identifier('B', str(self.temp_path))
        result = identifier.increment()
        self.assertEqual(result, 'B00001')

        # Test sequential increment
        result2 = identifier.increment()
        self.assertEqual(result2, 'B00002')

    def test_increment_empty_file(self):
        """Test increment method with empty file raises RuntimeError"""
        identifier = Identifier('0', str(self.temp_path))
        counter_file = self.temp_path / 'counter'

        # Empty the file
        with open(counter_file, 'w') as f:
            f.write('')

        with self.assertRaises(RuntimeError) as cm:
            identifier.increment()
        self.assertIn("Data missing from", str(cm.exception))
