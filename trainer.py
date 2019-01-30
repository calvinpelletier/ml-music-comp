import thread
import matplotlib.pyplot as plot
from constants import *
from data_generator import *
from mlp import *


def train(model, generator):
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


def adadelta(lr, tparams, grads, x, mask, y, cost):
    """
    Parameters
    ----------
    lr : Theano SharedVariable
        Initial learning rate
    tpramas: Theano SharedVariable
        Model parameters
    grads: Theano variable
        Gradients of cost w.r.t to parameres
    x: Theano variable
        Model inputs
    mask: Theano variable
        Sequence mask
    y: Theano variable
        Targets
    cost: Theano variable
        Objective fucntion to minimize
    """

    zipped_grads = [theano.shared(p.get_value() * numpy_floatX(0.), name='%s_grad' % k) for k, p in tparams.items()]
    running_up2 = [theano.shared(p.get_value() * numpy_floatX(0.), name='%s_rup2' % k) for k, p in tparams.items()]
    running_grads2 = [theano.shared(p.get_value() * numpy_floatX(0.), name='%s_rgrad2' % k) for k, p in tparams.items()]
    zgup = [(zg, g) for zg, g in zip(zipped_grads, grads)]
    rg2up = [(rg2, 0.95 * rg2 + 0.05 * (g ** 2)) for rg2, g in zip(running_grads2, grads)]
    f_grad_shared = theano.function([x, mask, y], cost, updates=zgup + rg2up, name='adadelta_f_grad_shared')

    updir = [-tensor.sqrt(ru2 + 1e-6) / tensor.sqrt(rg2 + 1e-6) * zg for zg, ru2, rg2 in zip(zipped_grads, running_up2, running_grads2)]
    ru2up = [(ru2, 0.95 * ru2 + 0.05 * (ud ** 2)) for ru2, ud in zip(running_up2, updir)]
    param_up = [(p, p + ud) for p, ud in zip(tparams.values(), updir)]
    f_update = theano.function([lr], [], updates=ru2up + param_up, on_unused_input='ignore', name='adadelta_f_update')

    return f_grad_shared, f_update


def user_input_thread():
    _ = raw_input()
    print 'Waiting for last epoch to finish...'
    global stop_training
    stop_training = True
