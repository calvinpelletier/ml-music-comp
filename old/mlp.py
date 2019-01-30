import theano
import theano.tensor as T
import numpy
import six.moves.cPickle as pickle
import thread
import matplotlib.pyplot as plot
import format_converter
import music21
from constants import *
import composer


class MLP(object):
    def __init__(self, rng, input, n_in, n_hidden, n_out):
        self.hidden_layer0 = HiddenLayer(rng, input, n_in, n_hidden)
        self.hidden_layer1 = HiddenLayer(rng, self.hidden_layer0.output, n_hidden, n_hidden)
        self.hidden_layer2 = HiddenLayer(rng, self.hidden_layer1.output, n_hidden, n_hidden)
        self.output_layer = OutputLayer(self.hidden_layer2.output, n_hidden, n_out)
        self.L1 = abs(self.hidden_layer0.W).sum() + abs(self.hidden_layer1.W).sum() + abs(self.hidden_layer2.W).sum() + abs(self.output_layer.W).sum()
        self.L2_sqr = (self.hidden_layer0.W ** 2).sum() + (self.hidden_layer1.W ** 2).sum() + (self.hidden_layer2.W ** 2).sum() + (self.output_layer.W ** 2).sum()
        self.negative_log_likelihood = self.output_layer.negative_log_likelihood
        self.params = self.hidden_layer0.params + self.hidden_layer1.params + self.hidden_layer2.params + self.output_layer.params
        self.input = input


class HiddenLayer(object):
    def __init__(self, rng, input, n_in, n_out, W=None, b=None, activation=T.tanh):
        if W is None:
            W_values = numpy.asarray(
                rng.uniform(
                    low=-numpy.sqrt(6. / (n_in + n_out)),
                    high=numpy.sqrt(6. / (n_in + n_out)),
                    size=(n_in, n_out)
                ),
                dtype=theano.config.floatX
            )
            if activation == T.nnet.sigmoid:
                W_values *= 4
            W = theano.shared(value=W_values, name='W', borrow=True)
        if b is None:
            b_values = numpy.zeros((n_out,), dtype=theano.config.floatX)
            b = theano.shared(value=b_values, name='b', borrow=True)
        self.W = W
        self.b = b
        self.output = activation(T.dot(input, self.W) + self.b)
        self.params = [self.W, self.b]


class OutputLayer(object):
    def __init__(self, input, n_in, n_out):
        self.W = theano.shared(
            value=numpy.zeros((n_in, n_out), dtype=theano.config.floatX),
            name='W',
            borrow=True
        )
        self.b = theano.shared(
            value=numpy.zeros((n_out,), dtype=theano.config.floatX),
            name='b',
            borrow=True
        )
        self.output = T.nnet.softmax(T.dot(input, self.W) + self.b)
        self.params = [self.W, self.b]
        self.input = input

    def negative_log_likelihood(self, y):
        return T.neg(T.mean(T.log(self.output)[T.arange(y.shape[0]), y]))

def train(
    learning_rate=0.01,
    L1_reg=0.00,
    L2_reg=0.0001,
    dataset='training_data/version0.csv',
    batch_size=10000,
    n_in=79,
    n_hidden=300,
    n_out=3,
    n_samples=2000000
):
    print 'Preparing data...'
    x_data = []
    y_data = []
    with open(dataset, 'r') as f:
        count = 0
        for line in f:
            data = [float(i) for i in line.strip().split(',')]
            x_data.append(data[:n_in])
            y_data.append(data[-1])
            count += 1
            if count > n_samples:
                break
    n_batches = len(x_data) / batch_size

    print 'Copying to GPU...'
    shared_x = theano.shared(numpy.asarray(x_data, dtype=theano.config.floatX), borrow=True)
    shared_y = T.cast(theano.shared(numpy.asarray(y_data, dtype=theano.config.floatX), borrow=True), 'int32')

    print 'Building model...'
    index = T.lscalar()
    x = T.matrix('x')
    y = T.ivector('y')
    rng = numpy.random.RandomState()
    mlp = MLP(
        rng=rng,
        input=x,
        n_in=n_in,
        n_hidden=n_hidden,
        n_out=n_out
    )
    cost = mlp.negative_log_likelihood(y) + L1_reg * mlp.L1 + L2_reg * mlp.L2_sqr
    gparams = [T.grad(cost, param) for param in mlp.params]
    updates = [(param, param - learning_rate * gparam) for param, gparam in zip(mlp.params, gparams)]
    model = theano.function(
        inputs=[index],
        outputs=cost,
        updates=updates,
        givens={
            x: shared_x[index * batch_size:(index + 1) * batch_size],
            y: shared_y[index * batch_size:(index + 1) * batch_size]
        }
    )

    print 'Training... press enter to stop...'
    thread.start_new_thread(user_input_thread, ())
    global stop_training
    stop_training = False
    cost_over_time = []
    while not stop_training:
        epoch_tot_cost = 0.0
        for batch_idx in range(n_batches):
            batch_avg_cost = model(batch_idx)
            epoch_tot_cost += batch_avg_cost
        epoch_avg_cost = epoch_tot_cost / float(n_batches)
        cost_over_time.append(epoch_avg_cost)
        plot.plot(cost_over_time)
        plot.savefig('out.png')
    print 'TODO: save model'
    # with open('model.pkl', 'wb') as f:
    #     pickle.dump(mlp, f)

    print 'Generating a song...'
    generator = theano.function(
        inputs=[mlp.input],
        outputs=mlp.output_layer.output
    )
    composer.compose_song(generator, 32)
    print 'Done.'


def user_input_thread():
    _ = raw_input()
    print 'Waiting for last epoch to finish...'
    global stop_training
    stop_training = True


if __name__ == '__main__':
    train(learning_rate=0.2)
