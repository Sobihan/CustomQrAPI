from flask import Flask, jsonify, request, send_file
import qrcode
from io import BytesIO

app = Flask(__name__)

def get_config(request):
    version = request.args.get('version')
    if version is None:
        version = 1
    else:
        version = int(version)
        if version < 1 or version > 40:
            raise ValueError('Invalid version')
    box_size = request.args.get('box_size')
    if box_size is None:
        box_size = 10
    else:
        box_size = int(box_size)
    border = request.args.get('border')
    if border is None:
        border = 5
    else:
        border = int(border)
    fill_color = request.args.get('fill_color')
    if fill_color is None:
        fill_color = 'black'
    else:
        fill_color = str(fill_color)
    back_color = request.args.get('back_color')
    if back_color is None:
        back_color = 'white'
    else:
        back_color = str(back_color)
    return version, box_size, border, fill_color, back_color

@app.route('/qrcode', methods=['GET'])
def generate_qrcode():
    text = request.args.get('text')
    if text is None:
        return jsonify({"error":"missing text"}), 400
    try:
        version, box_size, border, fill_color, back_color = get_config(request)
    except Exception as e:
        return jsonify({"error":f"{e}"})
    qr = qrcode.QRCode(version=version, box_size=box_size, border=border)
    qr.add_data(text)
    qr.make(fit=True)
    try:
        img = qr.make_image(fill_color=fill_color, back_color=back_color)
    except ValueError as e:
        print(f"Error: {e}")
        return jsonify({"error":f"{e}"})
    byte_io = BytesIO()
    img.save(byte_io, 'PNG')
    byte_io.seek(0)
    response = send_file(byte_io, mimetype='image/png')
    response.headers["Content-Disposition"] = "attachment; filename=qrcode.png"
    return response

@app.route('/', methods=['GET', 'POST'])
def index():
    return jsonify({"Error": "use /qrcode instead, with text in the parameter"}, 400)


@app.errorhandler(404)
def page_not_found(e):
    return jsonify({"Error": "use /qrcode instead, with text in the parameter"}, 404)

if __name__ == '__main__':
    app.run(debug=True)
