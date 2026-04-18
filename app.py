import cv2
import pytesseract
from flask import Flask, request, send_file

# 🔴 Set your Tesseract path
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def upload():
    if request.method == "POST":
        file = request.files["file"]

        if not file:
            return "No file uploaded"

        file_path = "input.jpg"
        file.save(file_path)

        # Read image
        image = cv2.imread(file_path)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # OCR
        text = pytesseract.image_to_string(gray)

        # Edge detection
        edges = cv2.Canny(gray, 50, 150)

        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        suspicious = False

        for cnt in contours:
            x, y, w, h = cv2.boundingRect(cnt)
            if w > 50 and h > 20:
                cv2.rectangle(image, (x, y), (x+w, y+h), (0, 0, 255), 2)
                suspicious = True

        output_path = "output.jpg"
        cv2.imwrite(output_path, image)

        explanation = []

        if suspicious:
            explanation.append("Irregular regions detected (possible editing)")
        if len(text.strip()) == 0:
            explanation.append("No readable text found")
        if not explanation:
            explanation.append("No major issues detected")

        score = 0
        if suspicious: score += 70
        if len(text.strip()) == 0: score += 30

        return f"""
        <!DOCTYPE html>
        <html>
        <head>
        <title>Result - DocuShield</title>
        <style>
        body {{
            font-family: Arial;
            background: #eef2f7;
            text-align: center;
        }}
        .card {{
            background: white;
            margin: 50px auto;
            padding: 25px;
            width: 650px;
            border-radius: 15px;
            box-shadow: 0px 8px 20px rgba(0,0,0,0.15);
        }}
        h2 {{
            color: #2c3e50;
        }}
        .score {{
            font-size: 18px;
            color: #007bff;
            font-weight: bold;
        }}
        ul {{
            text-align: left;
            display: inline-block;
        }}
        img {{
            margin-top: 15px;
            border-radius: 10px;
        }}
        a {{
            text-decoration: none;
            color: #007bff;
            font-weight: bold;
        }}
        </style>
        </head>
        <body>

        <div class="card">
            <h2>{'🚨 Forgery Suspicious' if suspicious else '✅ Looks Clean'}</h2>
            <p class="score">Confidence Score: {score}%</p>

            <h3>Explanation:</h3>
            <ul>
                {''.join([f"<li>{e}</li>" for e in explanation])}
            </ul>

            <h3>Extracted Text:</h3>
            <pre>{text}</pre>

            <h3>Detected Image:</h3>
            <img src="/output" width="400"><br><br>

            <a href="/">⬅ Upload Another</a>
        </div>

        </body>
        </html>
        """

    return '''
    <!DOCTYPE html>
    <html>
    <head>
    <title>DocuShield</title>
    <style>
    body {
        font-family: Arial;
        background: linear-gradient(to right, #4facfe, #00f2fe);
        text-align: center;
    }
    .container {
        background: white;
        padding: 30px;
        margin: 100px auto;
        width: 400px;
        border-radius: 15px;
        box-shadow: 0px 8px 25px rgba(0,0,0,0.2);
    }
    h1 {
        color: #2c3e50;
    }
    p {
        color: #555;
    }
    input[type=file] {
        margin: 20px 0;
    }
    button {
        padding: 12px 25px;
        background: #4facfe;
        color: white;
        border: none;
        border-radius: 25px;
        cursor: pointer;
        font-size: 16px;
    }
    button:hover {
        background: #007bff;
    }
    </style>
    </head>
    <body>

    <div class="container">
        <h1>🔍 DocuShield</h1>
        <p>AI-Based Document Forgery Detection</p>

        <form method="post" enctype="multipart/form-data">
            <input type="file" name="file"><br>
            <button type="submit">Analyze Document</button>
        </form>
    </div>

    </body>
    </html>
    '''

@app.route("/output")
def output():
    return send_file("output.jpg", mimetype='image/jpeg')

if __name__ == "__main__":
    app.run(debug=True)