import unittest
from unittest.mock import patch, MagicMock
from core.classifier import classify_genre

class TestClassifier(unittest.TestCase):

    @patch('core.classifier.subprocess.run')
    def test_classify_genre_ollama(self, mock_run):
        mock_result = MagicMock()
        mock_result.stdout = "House"
        mock_run.return_value = mock_result
        
        # Test fallback / default to Ollama
        genre = classify_genre("test_song", use_gemini=False)
        self.assertEqual(genre, "House")
        mock_run.assert_called_once()
        self.assertIn("ollama", mock_run.call_args[0][0])

    @patch('core.classifier.subprocess.run')
    def test_classify_genre_ollama_fallback_when_gemini_missing_key(self, mock_run):
        # Even if use_gemini=True, if key is missing, it should fallback to Ollama
        mock_result = MagicMock()
        mock_result.stdout = "Techno"
        mock_run.return_value = mock_result
        
        with patch.dict('os.environ', clear=True):
            genre = classify_genre("test_song", use_gemini=True)
            self.assertEqual(genre, "Techno")
            mock_run.assert_called_once()
            
    @patch('core.classifier.genai.Client')
    def test_classify_genre_gemini(self, mock_client_class):
        # Mock the client instance and its generate_content method
        mock_client_instance = MagicMock()
        mock_response = MagicMock()
        
        # The expected response is a JSON string because we request application/json
        mock_response.text = '{"genre": "Deep House"}'
        mock_client_instance.models.generate_content.return_value = mock_response
        
        mock_client_class.return_value = mock_client_instance
        
        # Provide a dummy API key to pass the missing key check
        with patch.dict('os.environ', {'GEMINI_API_KEY': 'dummy_key'}):
            genre = classify_genre("test_song", use_gemini=True)
            
            self.assertEqual(genre, "Deep House")
            mock_client_class.assert_called_once_with(api_key='dummy_key')
            mock_client_instance.models.generate_content.assert_called_once()

if __name__ == '__main__':
    unittest.main()
