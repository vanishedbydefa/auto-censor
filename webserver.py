import webbrowser

from flask import Flask, render_template, request, jsonify, send_from_directory
from threading import Timer

from main import main, calculate_progress, set_stop_threads
from main import prepare_parameters, reset_img_counter

def create_flask_app():
    app = Flask(__name__)

    @app.route('/', methods=['GET'])
    def index():
        return render_template('index.html')

    @app.route('/stop-censoring', methods=['POST'])
    def stop_running_censor():
        set_stop_threads(value=True)
        reset_img_counter()
        return render_template('index.html')

    @app.route('/progress', methods=['GET'])
    def progress():
        # You need to calculate the progress of your image processing function
        # Replace this with your actual progress calculation
        progress_percentage = calculate_progress()
        return jsonify({'progress': progress_percentage})

    @app.route('/start-censoring', methods=['POST'])
    def start_censoring():
        gender = request.form.getlist('gender')
        exposure = request.form.getlist('exposure')
        body_parts = request.form.getlist('body_part')
        face = request.form.get('face')
        recursive = request.form.get('recursive')
        method = request.form.get('method')
        path = request.form.get('path')
        thread_amount = int(request.form.get('threads'))
        
        # Reset STOP_THREADS to False and reset img counter
        reset_img_counter()
        set_stop_threads(value=False)

        # Check that path isn't empty
        if path == "":
            return render_template('error.html', error="You need to specify a path to the images you would like to censor!")

        to_censors = prepare_parameters(gender, exposure, body_parts, face)
        all_images, detected_images, censored_images = main(to_censors, method, path=path, recursive=recursive, thread_amount=thread_amount)

        return render_template('result.html', all_images=all_images, detected_images=detected_images, censored_images=censored_images)
    
    @app.route('/favicon.ico', methods=['GET'])
    def favicon():
        return send_from_directory(app.root_path, 'icon.png', mimetype='image/vnd.microsoft.icon')


    return app

def open_browser():
    webbrowser.open_new("http://127.0.0.1:5000")

if __name__ == '__main__':
    app = create_flask_app()
    Timer(1, open_browser).start()
    app.run(debug=False)
