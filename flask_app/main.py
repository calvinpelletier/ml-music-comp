import threading
import traceback
import sys
import random
import os

from flask import Flask, render_template, request, make_response

app = Flask(__name__, static_url_path="/static")

# Read in secret key for Flask from local text file
f = open("flask_key.txt")
app.config['SECRET_KEY'] = f.readline()
f.close()

@app.route('/', methods=['GET'])
def get_landing_page():
    src, category, idx = get_random_song()
    return render_template('index.html', src=src, category=category, idx=idx)

@app.route('/', methods=['POST'])
def submit_form():
    # print '~~~~~~~~~~~~~~~~~~~~~~'
    # print request.form
    with open('data.txt', 'a') as f:
        line = ','.join([request.form['category'], request.form['idx'], request.form['rating'], request.form['hc']])
        f.write(line + '\n')
    src, category, idx = get_random_song()
    return render_template('index.html', src=src, category=category, idx=idx)

def get_random_song():
    category = random.choice(['actual', 'char', 'genetic', 'normal', 'rev', 'rev_norm'])
    category_dir = 'static/songs/' + category
    songs = os.listdir('flask_app/' + category_dir)
    song = random.choice(songs)
    idx = song.split('.')[0]
    return category_dir + '/' + song, category, idx


# @socketio.on('add')
# def handle_add(message):
#     party, user_id, error = init_socket_event(message)
#     if error: return
#
#     # check if we need to emit a new now_playing song
#     if party.now_playing == None:
#         party.add_song(user_id, message['song_url'], message['title'])
#         emit_nowplaying(party)
#     else:
#         party.add_song(user_id, message['song_url'], message['title'])
#
#     emit_queue(party)
#
# def emit_queue(party):
#     # emit the queue to each user individually
#     for user_id in party.users:
#         queue_json = party.get_queue_json(user_id)
#         print "Emitting a list update: # of songs=", len(queue_json)
#         socketio.emit('update_list',
#                       {
#                           "queue": queue_json
#                       },room=get_room(party, user_id))

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80, debug=False)
