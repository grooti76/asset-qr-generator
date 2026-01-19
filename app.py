from flask import Flask, render_template_string, jsonify
import qrcode
import io
import base64

app = Flask(__name__)

# Load asset codes
with open("asset.txt") as f:
    asset_codes = [line.strip() for line in f if line.strip()]

HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Asset QR Audit</title>

    <style>
        table { width: 100%; border-collapse: collapse; }
        td { padding: 8px; vertical-align: middle; }
        img { max-width: 120px; }
        button { padding: 5px 10px; cursor: pointer; }
    </style>

    <script>
        function toggleQR(code, rowId, btn) {
            const qrCell = document.getElementById(rowId);

            // Hide QR if already visible
            if (qrCell.innerHTML.trim() !== "") {
                qrCell.innerHTML = "";
                btn.innerText = "Show QR";
                return;
            }

            // Show QR
            fetch('/generate_qr/' + code)
                .then(res => res.json())
                .then(data => {
                    qrCell.innerHTML =
                        '<img src="data:image/png;base64,' + data.qr + '">';
                    btn.innerText = "Hide QR";
                });
        }
    </script>
</head>
<body>

<h2>Asset QR Audit List</h2>

<table border="1">
{% for code in assets %}
<tr>
    <!-- Asset Code -->
    <td width="260">
        {{ code }}
    </td>

    <!-- Checkbox (Audit Purpose) -->
    <td width="50" align="center">
        <input type="checkbox">
    </td>

    <!-- Show / Hide Button -->
    <td width="120">
        <button onclick="toggleQR('{{ code }}', 'qr{{ loop.index }}', this)">
            Show QR
        </button>
    </td>

    <!-- QR Display (Right Side) -->
    <td id="qr{{ loop.index }}" width="160"></td>
</tr>
{% endfor %}
</table>

</body>
</html>
"""

@app.route("/")
def home():
    return render_template_string(HTML, assets=asset_codes)

@app.route("/generate_qr/<code>")
def generate_qr(code):
    img = qrcode.make(code)
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    qr_base64 = base64.b64encode(buffer.getvalue()).decode()
    return jsonify({"qr": qr_base64})

if __name__ == "__main__":
    app.run(debug=True)
