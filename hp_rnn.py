import tensorflow as tf
import hp_format_converter
import hp_data_generator
import random
from numpy.random import choice
import math

def reset_graph():
    if 'sess' in globals() and sess:
        sess.close()
    tf.reset_default_graph()


def build_graph(
    num_outputs = 26,
    num_inputs = 22,
    num_hidden0 = 300,
    # num_hidden1 = 200,
    num_steps = 50,
    num_batches = 10,
    num_lstm_layers = 2,
    dropout_keep_prob=0.7,
    learning_rate = 1e-4):

    reset_graph()

    x = tf.placeholder(tf.float32, [num_batches, num_steps, num_inputs], name='input_placeholder')
    y_ = tf.placeholder(tf.float32, [num_batches, num_steps, num_outputs], name='labels_placeholder')
    # W0 = tf.Variable(tf.random_normal([num_hidden0, num_hidden1]))
    # b0 = tf.Variable(tf.random_normal([num_hidden1]))
    W1 = tf.Variable(tf.random_normal([num_hidden0, num_outputs]))
    b1 = tf.Variable(tf.random_normal([num_outputs]))

    dropout = tf.constant(dropout_keep_prob)
    cell = tf.nn.rnn_cell.LSTMCell(num_hidden0, state_is_tuple=True)
    cell = tf.nn.rnn_cell.DropoutWrapper(cell, input_keep_prob=dropout)
    cell = tf.nn.rnn_cell.MultiRNNCell([cell] * num_lstm_layers, state_is_tuple=True)
    cell = tf.nn.rnn_cell.DropoutWrapper(cell, output_keep_prob=dropout)
    init_state = cell.zero_state(num_batches, tf.float32)
    rnn_outputs, final_state = tf.nn.dynamic_rnn(cell, x, dtype=tf.float32, initial_state=init_state)

    output = tf.reshape(rnn_outputs, [-1, num_hidden0])
    # y0 = tf.tanh(tf.matmul(output, W0) + b0)
    y1 = tf.matmul(output, W1) + b1
    # pred = tf.reshape(tf.nn.softmax(y1), [-1, num_steps, num_outputs])
    pred = tf.reshape(tf.nn.tanh(y1), [-1, num_steps, num_outputs])
    y = tf.reshape(y1, [-1, num_steps, num_outputs])

    total_loss = tf.reduce_mean(tf.nn.softmax_cross_entropy_with_logits(logits=y, labels=y_))
    # train_step = tf.train.AdadeltaOptimizer().minimize(total_loss)
    train_step = tf.train.AdamdeltaOptimizer().minimize(total_loss)

    return dict(
        x = x,
        y_ = y_,
        init_state = init_state,
        final_state = final_state,
        total_loss = total_loss,
        train_step = train_step,
        y = y,
        saver = tf.train.Saver(),
        pred = pred
    )


def train_network(g, num_epochs=10000, test_freq=500, test_epochs=100, batch_size=10, num_steps=50, verbose=True, save_freq=None):
    # tf.set_random_seed(2345)
    with tf.Session() as sess:
        sess.run(tf.global_variables_initializer())
        data_generator = hp_data_generator.DataGenerator(batch_size, num_steps, test_freq is not None)
        for i in range(num_epochs):
            batch_x, batch_y = data_generator.get_train_batch()
            _, error = sess.run([g['train_step'], g['total_loss']], feed_dict={g['x']: batch_x, g['y_']: batch_y})
            if verbose:
                print 'Train error for epoch ' + str(i) + ': ' + str(error)

            if test_freq is not None and i % test_freq == 0 and i != 0:
                average_error = 0.0
                for j in range(test_epochs):
                    batch_x, batch_y = data_generator.get_test_batch()
                    error = sess.run(g['total_loss'], feed_dict={g['x']: batch_x, g['y_']: batch_y})
                    average_error += error
                average_error /= float(test_epochs)
                print 'Average test error after epoch ' + str(i) + ': ' + str(average_error)

            if save_freq is not None and i % save_freq == 0 and i != 0:
                g['saver'].save(sess, 'models/' + str(i) + '.tf')
        g['saver'].save(sess, 'models/final.tf')

# TODO
def compose(g, savefile, num_songs=1, num_measures=8):
    with tf.Session() as sess:
        sess.run(tf.global_variables_initializer())
        g['saver'].restore(sess, savefile)
        for i in range(num_songs):
            print 'song: ' + str(i)
            state = None
            step = 0
            notes = []
            time_sig = [random.choice([0., 1.])]
            inputs = [0.] * 21 + time_sig
            while step < num_measures * 16:
                if state is not None:
                    output, state = sess.run([g['pred'], g['final_state']], {g['x']: [[inputs]], g['init_state']: state})
                else:
                    output, state = sess.run([g['pred'], g['final_state']], {g['x']: [[inputs]]})

                if len(notes) > 0:
                    prev_note = notes[-1][0]
                else:
                    prev_note = 66

                while True:
                    # decision = choice(range(-12, 14), 1, p=output[0][0])[0]
                    decision = choice(range(-12, 14), 1, p=normalize(output[0][0]))[0]
                    if decision == 13: # hold
                        if len(notes) == 0: # first note
                            continue
                        notes[-1][1] += 1
                        break
                    else: # new note
                        note = prev_note + decision
                        notes.append([note, 1])
                        break
                step += 1

                input_data_note = [0.] * 12
                input_data_note[notes[-1][0] % 12] = 1.
                input_data_position = hp_format_converter.get_note_position_from_val(notes[-1][0])
                input_data_duration = hp_format_converter.dec_to_4bit_bin_array(notes[-1][1])
                input_data_beat = hp_format_converter.dec_to_4bit_bin_array(step)
                inputs = input_data_note + input_data_position + input_data_duration + input_data_beat + time_sig
            hp_format_converter.note_array_to_abc(notes, time_sig, 'generated_songs/' + str(i) + '.abc')


def softmax(arr, scale=1.0):
    denominator = 0.0
    for val in arr:
        denominator += math.exp(scale * val)
    ret = []
    for val in arr:
        ret.append(math.exp(scale * val) / denominator)
    return ret


def normalize(arr, scale=1.0):
    denominator = 0.0
    for val in arr:
        denominator += val ** scale
    ret = []
    for val in arr:
        ret.append((val ** scale) / denominator)
    return ret


g = build_graph()
train_network(g, save_freq=2000)
# g = build_graph(num_steps=1, num_batches=1, dropout_keep_prob=1.0)
# compose(g, 'models/2000.tf', num_songs=5)
















#
