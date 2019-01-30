import theano
import theano.tensor as T
import numpy
from constants import *

class Model:
    def __init__(
        self,
        learning_rate=0.2,
        L1_reg=0.00,
        L2_reg=0.0001,
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
