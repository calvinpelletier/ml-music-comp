from constants import *
import data_generator
import tensorflow as tf

X_SIZE = 126
Y_SIZE = 122

pieces = data_generator.load_pieces(5)

print '.'

sess = tf.InteractiveSession()
x = tf.placeholder(tf.float32, shape=[None, X_SIZE])
y_ = tf.placeholder(tf.float32, shape=[None, Y_SIZE])
W = tf.Variable(tf.zeros([X_SIZE, Y_SIZE]))
b = tf.Variable(tf.zeros([Y_SIZE]))

y = tf.matmul(x, W) + b
cross_entropy = tf.reduce_mean(tf.nn.sigmoid_cross_entropy_with_logits(y, y_))
train_step = tf.train.AdadeltaOptimizer().minimize(cross_entropy)

sess.run(tf.global_variables_initializer())

for i in range(100000):
    batch_x, batch_y = data_generator.get_segment(pieces)
    _, error = sess.run([train_step, cross_entropy], feed_dict={x: batch_x, y_: batch_y})
    print str(i) + ': ' + str(error)
