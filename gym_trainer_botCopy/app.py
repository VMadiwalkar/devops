import os
import io
import psycopg2 
from psycopg2 import Error
from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename
# import google.generativeai as genai
from google import genai
from google.genai import types

from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# Configuration
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Configure Gemini
if GEMINI_API_KEY:
    system_instruction = "You are an elite personal gym trainer. You provide workout plans, diet advice, and form checks based on user input and uploaded files (images/PDFs).Be motivational, precise, and helpful. If user provide their injuries details or diet restrictions, consider them carefully in your advice."
    

    client = genai.Client()
    modelchat = client.chats.create(
        model='gemini-2.5-flash',
        config= types.GenerateContentConfig(
            system_instruction= system_instruction
        )
    )
    

    # genai.configure(api_key=GEMINI_API_KEY)
    # model = genai.GenerativeModel('gemini-2.5-flash')
else:
    print("WARNING: GEMINI_API_KEY not found in environment variables.")


def connect_to_db():
    
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_NAME = os.getenv("POSTGRES_DB", "postgres")
    DB_USER = os.getenv("POSTGRES_USER", "postgres")
    DB_PASSWORD = os.getenv("POSTGRES_PASSWORD", "mysecretpassword")
    DB_PORT = os.getenv("DB_PORT", "5432")

    connection = None
    try:
        # Establish connection
        connection = psycopg2.connect(
            host=DB_HOST, database=DB_NAME, user=DB_USER, 
            password=DB_PASSWORD, port=DB_PORT
        )
        print("Database connection established successfully...")
        print(f"db host: {DB_HOST}, db name: {DB_NAME}, db user: {DB_USER}, db port: {DB_PORT}")

    except Exception as e:
        print(f"Error connecting to the database: {e}")
        return None

    return connection

def init_db():
    """Initialize database table for storing uploaded files."""
    conn = connect_to_db()
    if conn is None:
        print("Could not initialize database.")
        return
    
    try:
        cursor = conn.cursor()
        create_table_query = """
        CREATE TABLE IF NOT EXISTS uploaded_files(
            id SERIAL PRIMARY KEY,
            filename VARCHAR(255) NOT NULL,
            mimetype VARCHAR(100),
            file_data BYTEA NOT NULL,
            gemini_file_id VARCHAR(500),
            uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        cursor.execute(create_table_query)
        conn.commit()
        print("Database table initialized successfully.")
        # print("Create table result:", res)  
    except Error as e:
        print(f"Error initializing database table: {e}")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

def save_file_to_db(filename, mimetype,file_data, gemini_file_id=None):
    """Save uploaded file to PostgreSQL database."""
    conn = connect_to_db()
    if conn is None:
        print("Could not connect to database.")
        return None
    
    try:
        cursor = conn.cursor()
        insert_query = """
        INSERT INTO uploaded_files(filename,file_data, mimetype, gemini_file_id)
        VALUES (%s, %s, %s, %s)
        RETURNING id;
        """
        cursor.execute(insert_query, (filename, file_data, mimetype, gemini_file_id))
        file_id = cursor.fetchone()[0]
        conn.commit()
        print(f"File saved to database with ID: {file_id}")
        return file_id
    except Error as e:
        print(f"Error saving file to database: {e}")
        return None
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    user_message = request.form.get('message', '')
    files = request.files.getlist('files')

    # Prepare for Gemini
    gemini_parts = []
    
    if user_message:
        gemini_parts.append(user_message)

    try:
        import tempfile
        import pathlib

        for file in files:
            if file and file.filename:
                filename = secure_filename(file.filename)
                
                file_data = file.read() 
                file.seek(0) # Reset pointer
                mimetype = file.mimetype

                # Save file to PostgreSQL
                file_id = save_file_to_db(filename, mimetype, file_data)
                print(f"File {filename} saved to database with ID: {file_id}")









                # Upload to Gemini File API
                if GEMINI_API_KEY:
                    # Create a temp file to upload
                    with tempfile.NamedTemporaryFile(delete=False, suffix=pathlib.Path(filename).suffix) as tmp:
                        tmp.write(file_data)
                        tmp_path = tmp.name
                    
                    try:
                        
                        uploaded_file = client.files.upload(
                            file=tmp_path,
                        )
                        # Update database with Gemini file ID
                        # if uploaded_file.name:
                        #     conn = connect_to_db()
                        #     if conn:
                        #         cursor = conn.cursor()
                        #         try:
                        #             update_query = "UPDATE uploaded_files SET gemini_file_id = %s WHERE id = %s;"
                        #             cursor.execute(update_query, (uploaded_file.name, file_id))
                        #             conn.commit()
                        #         except Error as e:
                        #             print(f"Error updating Gemini file ID: {e}")
                        #         finally:
                        #             cursor.close()
                        #             conn.close()
                        gemini_parts.append(uploaded_file)
                    except Exception as upload_error:
                        print(f"Error uploading to Gemini: {upload_error}")
                    finally:
                        # Clean up temp file
                        if os.path.exists(tmp_path):
                            os.remove(tmp_path)

    except Exception as e:
        print(f"File processing error: {e}")
        return jsonify({"response": f"Error processing files: {str(e)}"}), 500

    
    if not GEMINI_API_KEY:
         return jsonify({"response": "Error: Gemini API Key is missing. Please check your .env file."})

    try:
        
        # system_instruction = "You are an elite personal gym trainer. You provide workout plans, diet advice, and form checks based on user input and uploaded files (images/PDFs/Videos). Be motivational, precise, and helpful. Format your response in clean Markdown."
        
        
        
        
        # full_prompt = [system_instruction] + gemini_parts
        full_prompt = gemini_parts
        print("Gemini Parts:", gemini_parts)
        print("Full Prompt to Gemini:", full_prompt)
        # response = model.generate_content(full_prompt)
        # bot_reply = response.text

        

        # response = chat.send_message(full_prompt)
        response = modelchat.send_message(full_prompt)

        bot_reply = response.text
        
        

        return jsonify({"response": bot_reply})

    except Exception as e:
        print(f"Gemini API Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({"response": f"I encountered an error processing your request with Gemini: {str(e)}"}), 500

if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0', port=5000)
