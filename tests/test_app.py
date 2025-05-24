import unittest
import os
import io
from app import app, qa_bank, conversation_history # Import app and global variables

class AppTestCase(unittest.TestCase):

    def setUp(self):
        """Set up test client and other test variables."""
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False # Disable CSRF for testing forms
        app.config['SECRET_KEY'] = 'test_secret_key' # Set a secret key for session, flash messages
        self.client = app.test_client()

        # Reset global variables before each test
        qa_bank.clear()
        conversation_history.clear()
        # Reset chat index if it's also global and modified directly (it is in app.py)
        app.current_interview_question_index = 0


    def tearDown(self):
        """Executed after each test."""
        pass

    def test_home_page(self):
        """Test the home page loads."""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Welcome to the Q&A App', response.data)

    def test_upload_qa_csv(self):
        """Test uploading a Q&A CSV file."""
        # Dummy CSV data
        csv_data = "Question,Answer\nWhat is Flask?,A web framework\nWhat is Python?,A programming language"
        data = {'file': (io.BytesIO(csv_data.encode('utf-8')), 'test.csv')}
        
        with self.client: # Use 'with self.client' to handle context for session/flash messages
            response = self.client.post('/upload_qa', data=data, content_type='multipart/form-data', follow_redirects=True)
            self.assertEqual(response.status_code, 200) # Should redirect to upload_qa (GET)
            
            # Check if qa_bank is populated
            self.assertEqual(len(qa_bank), 2)
            self.assertEqual(qa_bank[0]['Question'], 'What is Flask?')
            self.assertEqual(qa_bank[1]['Answer'], 'A programming language')

            # Check for flashed message (requires session handling in tests, which 'with self.client' helps with)
            # Flashed messages are typically in response.data after a redirect
            self.assertIn(b'Q&A pairs uploaded and replaced successfully!', response.data)
            self.assertIn(b'Upload Q&A CSV File', response.data) # Check we are on the upload page

    def test_chat_message_exchange(self):
        """Test basic chat message exchange."""
        # Pre-populate qa_bank for this test
        qa_bank.extend([
            {'Question': 'Q1', 'Answer': 'A1'},
            {'Question': 'Q2', 'Answer': 'A2'}
        ])

        # Simulate starting a chat
        response = self.client.get('/start_chat')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'AI Interview', response.data) # Check chat page loaded

        # Simulate sending an initial message (or rather, client fetching the first question)
        # In the current design, the first question is loaded by client-side JS making a POST
        # Let's simulate that first POST which has 'initial_load: true' or no answer
        response = self.client.post('/chat_message', json={'question_index': 0}) # First question
        self.assertEqual(response.status_code, 200)
        json_data = response.get_json()
        self.assertIn('question', json_data)
        self.assertEqual(json_data['question'], 'Q1')
        self.assertEqual(json_data['next_question_index'], 1)
        
        # Simulate sending an answer to the first question
        response = self.client.post('/chat_message', json={'answer': 'My answer to Q1', 'question_index': 0})
        self.assertEqual(response.status_code, 200)
        json_data = response.get_json()
        self.assertIn('question', json_data)
        self.assertEqual(json_data['question'], 'Q2') # Expecting the second question
        self.assertEqual(json_data['next_question_index'], 2)

        # Check that conversation history was recorded for the first question
        self.assertEqual(len(conversation_history), 1)
        self.assertEqual(conversation_history[0]['question'], 'Q1')
        self.assertEqual(conversation_history[0]['answer'], 'My answer to Q1')

    def test_interview_summary(self):
        """Test the interview summary page."""
        # Pre-populate conversation_history for this test
        conversation_history.extend([
            {"question": "Q1_hist", "answer": "A1_hist"},
            {"question": "Q2_hist", "answer": "A2_hist"}
        ])

        response = self.client.get('/interview_summary')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Interview Summary Report', response.data)
        self.assertIn(b'Q1_hist', response.data)
        self.assertIn(b'A1_hist', response.data)
        self.assertIn(b'Q2_hist', response.data)
        self.assertIn(b'A2_hist', response.data)
        self.assertIn(b'Total Questions Answered: 2', response.data)

    def test_chat_message_end_of_interview(self):
        """Test chat message handling at the end of the interview."""
        qa_bank.extend([{'Question': 'Q_final', 'Answer': 'A_final'}])
        
        # Start chat
        self.client.get('/start_chat')

        # Answer the only question
        # First, the client fetches the question
        self.client.post('/chat_message', json={'question_index': 0}) 
        # Then, client sends the answer
        response = self.client.post('/chat_message', json={'answer': 'My final answer', 'question_index': 0})
        self.assertEqual(response.status_code, 200)
        json_data = response.get_json()

        self.assertIn('message', json_data)
        self.assertIn('End of interview', json_data['message'])
        self.assertIsNone(json_data['question']) # No more questions
        self.assertTrue(json_data['end_of_interview'])
        self.assertIn('/interview_summary', json_data['summary_link'])

        # Verify conversation history
        self.assertEqual(len(conversation_history), 1)
        self.assertEqual(conversation_history[0]['question'], 'Q_final')
        self.assertEqual(conversation_history[0]['answer'], 'My final answer')


if __name__ == '__main__':
    unittest.main()
