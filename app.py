from flask import Flask, render_template, request, redirect, url_for, flash
import csv
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)  # Needed for flashing messages

# Global variable to store Q&A pairs
qa_bank = []
current_interview_question_index = 0 # To track progress for a given session (simplified)
conversation_history = [] # To store Q&A pairs for the summary


@app.route('/')
def hello_world():
    return render_template('index.html')

@app.route('/start_chat')
def start_chat():
    global current_interview_question_index, conversation_history
    current_interview_question_index = 0 # Reset for a new chat session
    conversation_history = [] # Clear history for a new interview
    return render_template('chat.html')

@app.route('/chat_message', methods=['POST'])
def chat_message():
    global qa_bank, current_interview_question_index, conversation_history

    data = request.get_json()
    user_answer = data.get('answer')
    client_question_index = data.get('question_index') # Index of the question the user just answered

    if not qa_bank:
        return jsonify({'error': 'No Q&A data loaded. Please upload a CSV first.', 'question': None, 'end_of_interview': False})

    # Store the previous question and current answer if a user_answer is provided
    if user_answer is not None and client_question_index is not None:
        if 0 <= client_question_index < len(qa_bank):
            answered_question = qa_bank[client_question_index]['Question']
            conversation_history.append({"question": answered_question, "answer": user_answer})

    # Determine next question
    if current_interview_question_index < len(qa_bank):
        question_to_ask = qa_bank[current_interview_question_index]['Question']
        response_data = {
            'question': question_to_ask,
            'next_question_index': current_interview_question_index + 1,
            'end_of_interview': False
        }
        current_interview_question_index += 1 # Prepare for the next question
        return jsonify(response_data)
    else:
        # All questions answered
        return jsonify({
            'message': 'You have answered all questions. End of interview. Click the link below to see your summary.',
            'question': None, 
            'next_question_index': None,
            'end_of_interview': True,
            'summary_link': url_for('interview_summary')
        })

@app.route('/interview_summary')
def interview_summary():
    global conversation_history
    return render_template('summary_report.html', history=conversation_history)

@app.route('/upload_qa', methods=['GET', 'POST'])
def upload_qa():
    global qa_bank, conversation_history
    if request.method == 'POST':
        # Optionally clear conversation history when a new Q&A bank is uploaded
        # conversation_history = [] 
        # current_interview_question_index = 0
        if 'file' not in request.files:
            flash('No file part', 'error')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('No selected file', 'error')
            return redirect(request.url)
        if file and file.filename.endswith('.csv'):
            try:
                # Read the CSV file
                stream = file.stream.read().decode("utf-8")
                csvfile = stream.splitlines()
                reader = csv.DictReader(csvfile)
                
                new_qas = []
                for row in reader:
                    if 'Question' in row and 'Answer' in row:
                        new_qas.append({'Question': row['Question'], 'Answer': row['Answer']})
                    else:
                        flash('CSV must have "Question" and "Answer" columns', 'error')
                        return redirect(request.url)
                
                qa_bank.clear() # Clear existing bank before loading new Q&As
                qa_bank.extend(new_qas) 
                flash(f'{len(new_qas)} Q&A pairs uploaded and replaced successfully!', 'success')
                return redirect(url_for('upload_qa'))
            except Exception as e:
                flash(f'Error processing CSV file: {e}', 'error')
                return redirect(request.url)
        else:
            flash('Invalid file type. Please upload a CSV file.', 'error')
            return redirect(request.url)
    return render_template('upload_qa.html')

if __name__ == '__main__':
    app.run(debug=True)
