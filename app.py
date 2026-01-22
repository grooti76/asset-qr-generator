from flask import Flask, render_template_string, jsonify
import qrcode
import io
import base64
import os

app = Flask(__name__)

# ============================
# Load asset codes
# ============================
with open("asset.txt") as f:
    asset_codes = [line.strip() for line in f if line.strip()]

# ============================
# QR AUDIT WEB APP
# ============================
QR_HTML = """
<!DOCTYPE html>
<html>
<head>
<title>Asset QR Audit</title>

<style>
body { font-family: Arial; }
table { width: 100%; border-collapse: collapse; }
td { padding: 8px; vertical-align: middle; border-bottom: 1px solid #ddd; }
img { max-width: 120px; }
button { padding: 6px 12px; cursor: pointer; }
</style>

<script>
function toggleQR(code, rowId, btn) {
    const cell = document.getElementById(rowId);

    if (cell.innerHTML.trim() !== "") {
        cell.innerHTML = "";
        btn.innerText = "Show QR";
        return;
    }

    fetch('/generate_qr/' + code)
        .then(res => res.json())
        .then(data => {
            cell.innerHTML =
                '<img src="data:image/png;base64,' + data.qr + '">';
            btn.innerText = "Hide QR";
        });
}
</script>
</head>

<body>

<h2>Asset QR Audit</h2>

<p>
<a href="/mobile">📱 Open Mobile Copy App</a>
</p>

<table>
{% for code in assets %}
<tr>
    <td width="260">{{ code }}</td>

    <!-- Audit checkbox -->
    <td width="50" align="center">
        <input type="checkbox">
    </td>

    <!-- Show / Hide -->
    <td width="120">
        <button onclick="toggleQR('{{ code }}','qr{{ loop.index }}',this)">
            Show QR
        </button>
    </td>

    <!-- QR image -->
    <td id="qr{{ loop.index }}" width="160"></td>
</tr>
{% endfor %}
</table>

</body>
</html>
"""

# ============================
# MOBILE COPY APP
# ============================
MOBILE_HTML = """
<!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1">

<title>Asset Code Copier</title>

<style>
body { font-family: Arial; padding: 10px; }
.row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 12px;
    border-bottom: 1px solid #ddd;
    font-size: 16px;
}
button {
    background: #1976d2;
    color: white;
    border: none;
    padding: 6px 16px;
    border-radius: 6px;
    font-size: 14px;
}
</style>

<script>
function copyText(text, btn) {
    navigator.clipboard.writeText(text).then(() => {
        btn.innerText = "Copied ✓";
        setTimeout(() => btn.innerText = "Copy", 1200);
    });
}
</script>
</head>

<body>

<h3>Asset Codes</h3>

{% for code in assets %}
<div class="row">
    <div>{{ code }}</div>
    <button onclick="copyText('{{ code }}', this)">Copy</button>
</div>
{% endfor %}

</body>
</html>
"""

# ============================
# ROUTES
# ============================

@app.route("/")
def audit():
    return render_template_string(QR_HTML, assets=asset_codes)

@app.route("/mobile")
def mobile():
    return render_template_string(MOBILE_HTML, assets=asset_codes)

@app.route("/generate_qr/<code>")
def generate_qr(code):
    img = qrcode.make(code)
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")

    return jsonify({
        "qr": base64.b64encode(buffer.getvalue()).decode()
    })


# ============================
# RENDER PORT BINDING
# ============================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
