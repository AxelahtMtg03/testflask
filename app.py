from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/')
def home():
    return jsonify({"message": "Hello Flask sur Vercel!"})

@app.route('/api/users')
def users():
    return jsonify({"users": ["user1", "user2", "user3"]})

# Pour Vercel, on utilise app directement
if __name__ == '__main__':
    app.run(debug=True)