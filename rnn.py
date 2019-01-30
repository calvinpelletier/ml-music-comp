from constants import *
import data_generator
import tensorflow as tf
import numpy as np
import thread
import random
import format_converter

pieces = data_generator.load_pieces()

sizes = [126, 122]
steps = SEQUENCE_SIZE
layers = 4

x = tf.placeholder(tf.float32, shape=[None, steps, sizes[0]])
y_ = tf.placeholder(tf.float32, shape=[None, steps, sizes[1]])

W = tf.Variable(tf.random_normal([sizes[0], sizes[1]]))
b = tf.Variable(tf.random_normal([sizes[1]]))

layer = tf.nn.rnn_cell.BasicLSTMCell(sizes[0], forget_bias=1.0)
layer = tf.nn.rnn_cell.DropoutWrapper(layer, output_keep_prob=0.5)
lstm = tf.nn.rnn_cell.MultiRNNCell([layer] * layers)

outputs, state = tf.nn.dynamic_rnn(lstm, x, dtype=tf.float32)

output = tf.reshape(outputs, [-1, sizes[0]])
y = tf.nn.sigmoid(tf.matmul(output, W) + b)
y = tf.reshape(y, [-1, steps, sizes[1]])

cross_entropy = tf.reduce_mean(-tf.reduce_sum(y_ * tf.log(y), [1, 2]))
train_step = tf.train.AdadeltaOptimizer().minimize(cross_entropy)

# comp_x = tf.placeholder(tf.float32, shape=[1, steps, sizes[0]])
# comp_outputs, comp_state = tf.nn.dynamic_rnn(lstm, comp_x, dtype=tf.float32)
# comp_output = tf.reshape(comp_outputs, [-1, sizes[0]])
# comp_y = tf.nn.sigmoid(tf.matmul(comp_output, W) + b)
# comp_y = tf.reshape(comp_y, [-1, steps, sizes[1]])

def user_input_thread():
    _ = raw_input()
    print 'Waiting for last epoch to finish...'
    global stop_training
    stop_training = True

sess = tf.InteractiveSession()
sess.run(tf.global_variables_initializer())
print 'Training... press enter to stop...'
thread.start_new_thread(user_input_thread, ())
global stop_training
stop_training = False
cost_over_time = []
count = 0
while not stop_training:
    batch_x, batch_y = data_generator.get_batch(pieces)
    _, error, y_out = sess.run([train_step, cross_entropy, y], feed_dict={x: batch_x, y_: batch_y})
    if count % 500 == 0:
        tmp = []
        for timestep in y_out[0][0]:
            tmp.append([1 if random.random() < prob else 0 for prob in timestep])
        format_converter.output_matrix_to_midi(tmp, str(count) + '.mid')
    print str(count) + ': ' + str(error)
    count += 1


print 'Composing...'
song_len = BEATS_PER_MEASURE * 16
song_count = 0
while True:
    print 'song: ' + str(song_count)
    output_matrix = []
    input_matrix = [[[0] * 122 + [1] * 4 for _ in range(steps)]]
    for i in range(song_len):
        if i < len(input_matrix[0]):
            idx = i
        else:
            idx = len(input_matrix[0]) - 1
        out = sess.run([y], feed_dict={x: input_matrix})
        bin_out = []
        for prob in out[0][0][idx]:
            if random.random() < prob:
                bin_out.append(1)
            else:
                bin_out.append(0)
        # out = [1 if random.random() < prob else 0 for prob in out[0][idx]]
        output_matrix.append(bin_out)
        next_beat = [0] * 4
        if (i+1) % 16 == 0:
            next_beat[0] = 1
        if (i+1) % 8 == 0:
            next_beat[1] = 1
        if (i+1) % 4 == 0:
            next_beat[2] = 1
        if (i+1) % 2 == 0:
            next_beat[3] = 1
        bin_out += next_beat
        if i+1 < len(input_matrix[0]):
            input_matrix[0][i+1] = bin_out
        else:
            input_matrix[0].pop(0)
            input_matrix[0].append(bin_out)
    format_converter.output_matrix_to_midi(output_matrix, filename=SONG_FOLDER+'/'+str(song_count)+'.mid')
    song_count += 1







#
