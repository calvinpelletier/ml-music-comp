from constants import *
import data_generator
import tensorflow as tf
import numpy as np

sizes = [126, 122]
x = tf.placeholder(tf.float32, shape=[BATCH_SIZE, steps, sizes[0]])
# x = tf.transpose(x, [1, 0, 2])
# x = tf.reshape(x, [-1, sizes[0]])
# x = tf.split(x, steps, 0)
y_ = tf.placeholder(tf.float32, shape=[BATCH_SIZE, steps, sizes[1]])
# y_ = tf.transpose(y_, [1, 0, 2])
# s = tf.placeholder(tf.float32, shape=[])

W = tf.Variable(tf.random_normal([sizes[0], sizes[1]]))
b = tf.Variable(tf.random_normal([sizes[1]]))

lstm = tf.nn.rnn_cell.BasicLSTMCell(sizes[0], forget_bias=0.0)
# outputs, state = tf.nn.rnn(lstm, tf.unpack(tf.transpose(x, [1, 0, 2])), dtype=tf.float32)
output, state = tf.nn.dynamic_rnn(lstm, x, dtype=tf.float32)
# output = tf.transpose(tf.pack(outputs), [1, 0, 2])
output = tf.reshape(output, [-1, sizes[0]])
y = tf.nn.sigmoid(tf.matmul(output, W) + b)
y = tf.reshape(y, [-1, steps, sizes[1]])


cross_entropy = tf.reduce_mean(-tf.reduce_sum(y_ * tf.log(y), [1, 2]))
train_step = tf.train.AdadeltaOptimizer().minimize(cross_entropy)

sess = tf.InteractiveSession()
sess.run(tf.global_variables_initializer())
for i in range(500):
    batch_x, batch_y = data_generator.get_batch(pieces)
    # batch_x = np.array(batch_x).transpose((1, 0, 2))
    # batch_y = np.array(batch_y).transpose((1, 0, 2))
    _, error = sess.run([train_step, cross_entropy], feed_dict={x: batch_x, y_: batch_y})
    print str(i) + ': ' + str(error)

# save vars
weights = W.eval()
biases = b.eval()
np.savetxt('W.csv', weights, delimiter=',')
np.savetxt('b.csv', biases, delimiter=',')











#
