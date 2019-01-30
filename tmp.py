     import data_generator
     import tensorflow as tf
     import numpy as np

     pieces = data_generator.load_pieces(5)

     batches = 100
     sizes = [126, 122]
     steps = 128
     layers = 2

     x = tf.placeholder(tf.float32, shape=[batches, steps, sizes[0]])
     y_ = tf.placeholder(tf.float32, shape=[batches, steps, sizes[1]])

     W = tf.Variable(tf.random_normal([sizes[0], sizes[1]]))
     b = tf.Variable(tf.random_normal([sizes[1]]))

     layer = tf.nn.rnn_cell.BasicLSTMCell(sizes[0], forget_bias=0.0)
     lstm = tf.nn.rnn_cell.MultiRNNCell([layer] * layers)

     # ~~~~~ code from linked post ~~~~~
     def get_state_variables(batch_size, cell):
         # For each layer, get the initial state and make a variable out of it
         # to enable updating its value.
         state_variables = []
         for state_c, state_h in cell.zero_state(batch_size, tf.float32):
             state_variables.append(tf.nn.rnn_cell.LSTMStateTuple(
                 tf.Variable(state_c, trainable=False),
                 tf.Variable(state_h, trainable=False)))
         # Return as a tuple, so that it can be fed to dynamic_rnn as an initial state
         return tuple(state_variables)

     states = get_state_variables(batches, lstm)

     outputs, new_states = tf.nn.dynamic_rnn(lstm, x, initial_state=states, dtype=tf.float32)

     def get_state_update_op(state_variables, new_states):
         # Add an operation to update the train states with the last state tensors
         update_ops = []
         for state_variable, new_state in zip(state_variables, new_states):
             # Assign the new state to the state variables on this layer
             update_ops.extend([state_variable[0].assign(new_state[0]),
                                state_variable[1].assign(new_state[1])])
         # Return a tuple in order to combine all update_ops into a single operation.
         # The tuple's actual value should not be used.
         return tf.tuple(update_ops)

     update_op = get_state_update_op(states, new_states)
     # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

     output = tf.reshape(outputs, [-1, sizes[0]])
     y = tf.nn.sigmoid(tf.matmul(output, W) + b)
     y = tf.reshape(y, [-1, steps, sizes[1]])

     cross_entropy = tf.reduce_mean(-tf.reduce_sum(y_ * tf.log(y), [1, 2]))
     # train_step = tf.train.AdadeltaOptimizer().minimize(cross_entropy)

     sess = tf.InteractiveSession()
     sess.run(tf.global_variables_initializer())
     batch_x, batch_y = data_generator.get_batch(pieces)
     for i in range(500):
         error, _ = sess.run([cross_entropy, update_op], feed_dict={x: batch_x, y_: batch_y})
         print str(i) + ': ' + str(error)
