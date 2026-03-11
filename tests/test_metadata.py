import unittest
from unittest.mock import patch, MagicMock
from core.metadata import get_existing_genre, write_genre_to_metadata

class TestMetadata(unittest.TestCase):

    @patch('core.metadata.EasyID3')
    def test_get_existing_genre_mp3(self, mock_easyid3):
        mock_audio = MagicMock()
        mock_audio.get.return_value = ['House']
        mock_easyid3.return_value = mock_audio
        
        genre = get_existing_genre("song.mp3")
        self.assertEqual(genre, "House")
        mock_easyid3.assert_called_once_with("song.mp3")

    @patch('core.metadata.EasyID3')
    def test_write_genre_to_metadata_mp3(self, mock_easyid3):
        mock_audio = MagicMock()
        mock_easyid3.return_value = mock_audio
        
        success = write_genre_to_metadata("song.mp3", "Techno")
        self.assertTrue(success)
        mock_easyid3.assert_called_once_with("song.mp3")
        self.assertEqual(mock_audio.__setitem__.call_args[0], ('genre', 'Techno'))
        mock_audio.save.assert_called_once()

    @patch('core.metadata.EasyID3')
    def test_write_genre_error_handling(self, mock_easyid3):
        mock_easyid3.side_effect = Exception("File locked")
        success = write_genre_to_metadata("song.mp3", "Techno")
        self.assertFalse(success)

if __name__ == '__main__':
    unittest.main()
