# coding:GBK

import numpy
import theano
import theano.tensor as T
import lasagne as L

from config import *
from utils import *
from sample import *


# class SocialPoolingLayer(MergeLayer):
#     @property
#     def output_shape(self):
#         # input (prev_lstms): [SIZE_BATCH, N_NODES, LENGTH_SEQUENCE_INPUT, DIMENSION_HIDDEN_LAYER]
#         # traces: [SIZE_BATCH, N_NODES, LENGTH_SEQUENCE_INPUT, 2]
#         # output: [SIZE_BATCH, N_NODES, LENGTH_SEQUENCE_INPUT, RANGE_NEIGHBORHOOD, RANGE_NEIGHBORHOOD, DIMENSION_HIDDEN_LAYERS]
#         shape = self.input_shape[0], self.input_shape[2], RANGE_NEIGHBORHOOD, RANGE_NEIGHBORHOOD, self.input_shape[3]
#         if any(isinstance(s, T.Variable) for s in shape):
#             raise ValueError("%s returned a symbolic output shape from its "
#                              "get_output_shape_for() method: %r. This is not "
#                              "allowed; shapes must be tuples of integers for "
#                              "fixed-size dimensions and Nones for variable "
#                              "dimensions." % (self.__class__.__name__, shape))
#         return shape
#
#     def get_output_for(self, input, **kwargs):
#         """
#         Propagates the given input through this layer (and only this layer).
#
#         Parameters
#         ----------
#         input : Theano expression
#             The expression to propagate through this layer.
#
#         Returns
#         -------
#         output : Theano expression
#             The output of this layer given the input to this layer.
#
#
#         Notes
#         -----
#         This is called by the base :meth:`get_output()`
#         to propagate data through a network.
#
#         This method should be overridden when implementing a new
#         :class:`Layer` class. By default it raises `NotImplementedError`.
#         """
#         shape = (None, N_NODES, LENGTH_SEQUENCE_INPUT, DIMENSION_SAMPLE)
#         social_hidden_tensor = numpy.zeros(self.output_shape())
#         for ibatch in xrange(SIZE_BATCH):
#             for inode in xrange(self.input_shape[1]):
#                 social_hidden_tensor[ibatch] = self.social_pool(self.traces, self.traces[inode], self.input_layer)
#         return social_hidden_tensor
#
#     # def get_params(self, unwrap_shared=True, **tags):
#     #     return []
#     # """
#     #
#     # :param incomings: [l_in, [l_prev_lstm]]
#     # :rtype: object
#     # """
#         # def __init__(self, incomings, name=None):
#         #     self.input_shapes = [incoming if isinstance(incoming, tuple)
#         #                          else incoming.output_shape
#         #                          for incoming in incomings]
#         #     self.input_layers = [None if isinstance(incoming, tuple)
#         #                          else incoming
#         #                          for incoming in incomings]
#         #     self.name = name
#         #     self.params = OrderedDict()
#         #     self.get_output_kwargs = []


all_traces = read_traces_from_path(PATH_TRACE_FILES)
MAX_SEQUENCES = len(all_traces.items())

N_NODES = len(all_traces)
# if N_NODES_EXPECTED > N_NODES:
#     raise RuntimeError("Cannot find enough nodes in the given path.")
N_NODES = N_NODES_EXPECTED if N_NODES_EXPECTED < N_NODES else N_NODES


# class SocialLSTMCell(L.layers.CustomRecurrentCell):
#     """
#     L.L.layers.recurrent.CustomRecurrentLayer(incoming, input_to_hidden,
#     hidden_to_hidden, nonlinearity=L.L.nonlinearities.rectify,
#     hid_init=L.L.init.Constant(0.), backwards=False,
#     learn_init=False, gradient_steps=-1, grad_clipping=0,
#     unroll_scan=False, precompute_input=True, mask_input=None,
#     only_return_final=False, **kwargs)
#
#     A layer which implements a recurrent connection.
#
#     This layer allows you to specify custom input-to-hidden and
#     hidden-to-hidden connections by instantiating :class:`L.L.layers.Layer`
#     instances and passing them on initialization.  Note that these connections
#     can consist of multiple layers chained together.  The output shape for the
#     provided input-to-hidden and hidden-to-hidden connections must be the same.
#     If you are looking for a standard, densely-connected recurrent layer,
#     please see :class:`RecurrentLayer`.  The output is computed by
#
#     .. math ::
#         h_t = \sigma(f_i(x_t, f_h(h_{t-1})))
#
#     Parameters
#     ----------
#     incoming : a :class:`L.L.layers.Layer` instance or a tuple
#         The layer feeding into this layer, or the expected input shape.
#     input_to_hidden : :class:`L.L.layers.Layer`
#         :class:`L.L.layers.Layer` instance which connects input to the
#         hidden state (:math:`f_i`).  This layer may be connected to a chain of
#         layers, which must end in a :class:`L.L.layers.InputLayer` with the
#         same input shape as `incoming`, except for the first dimension: When
#         ``precompute_input == True`` (the default), it must be
#         ``incoming.output_shape[0]*incoming.output_shape[1]`` or ``None``; when
#         ``precompute_input == False``, it must be ``incoming.output_shape[0]``
#         or ``None``.
#     hidden_to_hidden : :class:`L.L.layers.Layer`
#         Layer which connects the previous hidden state to the new state
#         (:math:`f_h`).  This layer may be connected to a chain of layers, which
#         must end in a :class:`L.L.layers.InputLayer` with the same input
#         shape as `hidden_to_hidden`'s output shape.
#     nonlinearity : callable or None
#         Nonlinearity to apply when computing new state (:math:`\sigma`). If
#         None is provided, no nonlinearity will be applied.
#     hid_init : callable, np.ndarray, theano.shared or :class:`Layer`
#         Initializer for initial hidden state (:math:`h_0`).
#     backwards : bool
#         If True, process the sequence backwards and then reverse the
#         output again such that the output from the layer is always
#         from :math:`x_1` to :math:`x_n`.
#     learn_init : bool
#         If True, initial hidden values are learned.
#     gradient_steps : int
#         Number of timesteps to include in the backpropagated gradient.
#         If -1, backpropagate through the entire sequence.
#     grad_clipping : float
#         If nonzero, the gradient messages are clipped to the given value during
#         the backward pass.  See [1]_ (p. 6) for further explanation.
#     unroll_scan : bool
#         If True the recursion is unrolled instead of using scan. For some
#         graphs this gives a significant speed up but it might also consume
#         more memory. When `unroll_scan` is True, backpropagation always
#         includes the full sequence, so `gradient_steps` must be set to -1 and
#         the input sequence length must be known at compile time (i.e., cannot
#         be given as None).
#     precompute_input : bool
#         If True, precompute input_to_hid before iterating through
#         the sequence. This can result in a speedup at the expense of
#         an increase in memory usage.
#     mask_input : :class:`L.L.layers.Layer`
#         Layer which allows for a sequence mask to be input, for when sequences
#         are of variable length.  Default `None`, which means no mask will be
#         supplied (i.e. all sequences are of the same length).
#     only_return_final : bool
#         If True, only return the final sequential output (e.g. for tasks where
#         a single target value for the entire sequence is desired).  In this
#         case, Theano makes an optimization which saves memory.
#
#     Examples
#     --------
#
#     The following example constructs a simple `CustomRecurrentLayer` which
#     has dense input-to-hidden and hidden-to-hidden connections.
#
#     >>> import lasagne
#     >>> n_batch, n_steps, n_in = (2, 3, 4)
#     >>> n_hid = 5
#     >>> l_in = L.L.layers.InputLayer((n_batch, n_steps, n_in))
#     >>> l_in_hid = L.L.layers.DenseLayer(
#     ...     L.L.layers.InputLayer((None, n_in)), n_hid)
#     >>> l_hid_hid = L.L.layers.DenseLayer(
#     ...     L.L.layers.InputLayer((None, n_hid)), n_hid)
#     >>> l_rec = L.L.layers.CustomRecurrentLayer(l_in, l_in_hid, l_hid_hid)
#
#     The CustomRecurrentLayer can also support "convolutional recurrence", as is
#     demonstrated below.
#
#     >>> n_batch, n_steps, n_channels, width, height = (2, 3, 4, 5, 6)
#     >>> n_out_filters = 7
#     >>> filter_shape = (3, 3)
#     >>> l_in = L.L.layers.InputLayer(
#     ...     (n_batch, n_steps, n_channels, width, height))
#     >>> l_in_to_hid = L.L.layers.Conv2DLayer(
#     ...     L.L.layers.InputLayer((None, n_channels, width, height)),
#     ...     n_out_filters, filter_shape, pad='same')
#     >>> l_hid_to_hid = L.L.layers.Conv2DLayer(
#     ...     L.L.layers.InputLayer(l_in_to_hid.output_shape),
#     ...     n_out_filters, filter_shape, pad='same')
#     >>> l_rec = L.L.layers.CustomRecurrentLayer(
#     ...     l_in, l_in_to_hid, l_hid_to_hid)
#
#     References
#     ----------
#     .. [1] Graves, Alex: "Generating sequences with recurrent neural networks."
#            arXiv preprint arXiv:1308.0850 (2013).
#     """
#     def __init__(self, incoming, incoming_recurrent, input_to_hidden, hidden_to_hidden,
#                  nonlinearity=L.nonlinearities.rectify,
#                  hid_init=L.init.Constant(0.),
#                  grad_clipping=0,
#                  **kwargs):
#         super(L.layers.CustomRecurrentCell, self).__init__(
#             {'input': incoming, 'recurrent_input': incoming_recurrent} if input_to_hidden is not None else {},
#             {'output': hid_init}, **kwargs)
#             # {'output': hid_init, 'input_hidden_previous': hid_init}, **kwargs)
#         self.input_to_hidden = input_to_hidden
#         self.hidden_to_hidden = hidden_to_hidden
#         self.grad_clipping = grad_clipping
#         if nonlinearity is None:
#             self.nonlinearity = L.nonlinearities.identity
#         else:
#             self.nonlinearity = nonlinearity
#
#     def get_params(self, **tags):
#         step = tags.pop('step', False)
#         tags.pop('step_only', None)
#         precompute_input = tags.pop('precompute_input', False)
#
#         if self.input_to_hidden is not None:
#             # Check that input_to_hidden and hidden_to_hidden output shapes
#             #  match, but don't check a dimension if it's None for either shape
#             if not all(s1 is None or s2 is None or s1 == s2 for s1, s2
#                        in zip(self.input_to_hidden.output_shape[1:],
#                               self.hidden_to_hidden.output_shape[1:])):
#                 raise ValueError("The output shape for input_to_hidden and "
#                                  "hidden_to_hidden must be equal after the "
#                                  "first dimension, but "
#                                  "input_to_hidden.output_shape={} and "
#                                  "hidden_to_hidden.output_shape={}".format(
#                                      self.input_to_hidden.output_shape,
#                                      self.hidden_to_hidden.output_shape))
#
#             # Check that input_to_hidden's output shape is the same as
#             # hidden_to_hidden's input shape but don't check a dimension if
#             # it's None for either shape
#             if not all(s1 is None or s2 is None or s1 == s2 for s1, s2
#                        in zip(self.input_to_hidden.output_shape[1:],
#                               self.hidden_to_hidden.input_shape[1:])):
#                 raise ValueError("The output shape for input_to_hidden "
#                                  "must be equal to the input shape of "
#                                  "hidden_to_hidden after the first "
#                                  "dimension, but "
#                                  "input_to_hidden.output_shape={} and "
#                                  "hidden_to_hidden.input_shape={}".format(
#                                      self.input_to_hidden.output_shape,
#                                      self.hidden_to_hidden.input_shape))
#
#             # Check that the first dimension of input_to_hidden and
#             # hidden_to_hidden's outputs match when we won't precompute the
#             # input dot product
#             if (not precompute_input and
#                     self.input_to_hidden.output_shape[0] is not None and
#                     self.hidden_to_hidden.output_shape[0] is not None and
#                     (self.input_to_hidden.output_shape[0] !=
#                      self.hidden_to_hidden.output_shape[0])):
#                 raise ValueError(
#                     'When precompute_input == False, '
#                     'input_to_hidden.output_shape[0] must equal '
#                     'hidden_to_hidden.output_shape[0] but '
#                     'input_to_hidden.output_shape[0] = {} and '
#                     'hidden_to_hidden.output_shape[0] = {}'.format(
#                         self.input_to_hidden.output_shape[0],
#                         self.hidden_to_hidden.output_shape[0]))
#
#         params = L.layers.get_all_params(self.hidden_to_hidden, **tags)
#         if not (step and precompute_input):
#             params += L.layers.get_all_params(self.input_to_hidden, **tags)
#         return params
#
#     def precompute_shape_for(self, input_shapes):
#         # if self.input_to_hidden is not None:
#         #     input_shape = input_shapes['input']
#         #     # Check that the input_to_hidden connection can appropriately
#         #     # handle a first dimension of input_shape[0]*input_shape[1] when
#         #     # we will precompute the input dot product
#         #     if (self.input_to_hidden.output_shape[0] is not None and
#         #             input_shape[0] is not None and
#         #             input_shape[1] is not None and
#         #             (self.input_to_hidden.output_shape[0] !=
#         #              input_shape[0]*input_shape[1])):
#         #         raise ValueError(
#         #             'When precompute_input == True, '
#         #             'input_to_hidden.output_shape[0] must equal '
#         #             'incoming.output_shape[0]*incoming.output_shape[1] '
#         #             '(i.e. n_batch*sequence_length) or be None but '
#         #             'input_to_hidden.output_shape[0] = {} and '
#         #             'incoming.output_shape[0]*incoming.output_shape[1] = '
#         #             '{}'.format(self.input_to_hidden.output_shape[0],
#         #                         input_shape[0]*input_shape[1]))
#         return {}
#
#     def get_output_shape_for(self, input_shapes):
#         return {'output': self.hidden_to_hidden.output_shape}
#
#     def precompute_for(self, inputs, **kwargs):
#         # if self.input_to_hidden is not None:
#         #     input = inputs['input']
#         #     seq_len, n_batch = input.shape[0], input.shape[1]
#         #
#         #     # Because the input is given for all time steps, we can precompute
#         #     # the inputs to hidden before scanning. First we need to reshape
#         #     # from (seq_len, n_batch, trailing dimensions...) to
#         #     # (seq_len*n_batch, trailing dimensions...)
#         #     # This strange use of a generator in a tuple was because
#         #     # input.shape[2:] was raising a Theano error
#         #     trailing_dims = tuple(input.shape[n] for n in range(2, input.ndim))
#         #     input = T.reshape(input, (seq_len*n_batch,) + trailing_dims)
#         #     input = L.layers.get_output(
#         #         self.input_to_hidden, input, **kwargs)
#         #
#         #     # Reshape back to (seq_len, n_batch, trailing dimensions...)
#         #     trailing_dims = tuple(input.shape[n] for n in range(1, input.ndim))
#         #     input = T.reshape(input, (seq_len, n_batch) + trailing_dims)
#         #     return {'input': input}
#
#         # raise RuntimeError("SocialLSTMCell::precompute_for @ model: \n\tUnexpected access of this block.")
#         return {}
#
#     def get_output_for(self, inputs, precompute_input = False, **kwargs):
#         """
#         Compute this layer's output function given a symbolic input variable.
#
#         Parameters
#         ----------
#         inputs : list of theano.TensorType
#             `inputs[0]` should always be the symbolic input variable.  When
#             this layer has a mask input (i.e. was instantiated with
#             `mask_input != None`, indicating that the lengths of sequences in
#             each batch vary), `inputs` should have length 2, where `inputs[1]`
#             is the `mask`.  The `mask` should be supplied as a Theano variable
#             denoting whether each time step in each sequence in the batch is
#             part of the sequence or not.  `mask` should be a matrix of shape
#             ``(n_batch, n_time_steps)`` where ``mask[i, j] = 1`` when ``j <=
#             (length of sequence i)`` and ``mask[i, j] = 0`` when ``j > (length
#             of sequence i)``. When the hidden state of this layer is to be
#             pre-filled (i.e. was set to a :class:`Layer` instance) `inputs`
#             should have length at least 2, and `inputs[-1]` is the hidden state
#             to prefill with.
#
#         Returns
#         -------
#         layer_output : theano.TensorType
#             Symbolic output variable.
#         """
#         # Disable precomputing for SocialLSTMCell
#         precompute_input = False
#
#         hid_prev = inputs['output']
#
#         # Compute the hidden-to-hidden activation
#         hid_prev = L.layers.get_output(
#             self.hidden_to_hidden, hid_prev, **kwargs)
#
#         if self.input_to_hidden is not None:
#             input = inputs['input']
#             input_hid = inputs['recurrent_input']
#
#             # If the dot product is precomputed then add it, otherwise
#             # calculate the input_to_hidden values and add them
#             # if precompute_input:
#             #     hid_pre += input
#             # else:
#             hid_curr = L.layers.get_output(
#                 self.input_to_hidden, {input.name: input, input_hid.name: hid_prev}, **kwargs)
#
#         # Clip gradients
#         if self.grad_clipping:
#             hid_curr = theano.gradient.grad_clip(
#                 hid_curr, -self.grad_clipping, self.grad_clipping)
#
#         return {'output': self.nonlinearity(hid_curr)}


class RecurrentContainerLayer(L.layers.MergeLayer):
# class CustomRecurrentLayer(MergeLayer):
    """
    L.layers.recurrent.CustomRecurrentLayer(incoming, input_to_hidden,
    hidden_to_hidden, nonlinearity=L.nonlinearities.rectify,
    hid_init=L.init.Constant(0.), backwards=False,
    learn_init=False, gradient_steps=-1, grad_clipping=0,
    unroll_scan=False, precompute_input=True, mask_input=None,
    only_return_final=False, **kwargs)

    A layer which implements a recurrent connection.

    This layer allows you to specify custom input-to-hidden and
    hidden-to-hidden connections by instantiating :class:`L.layers.Layer`
    instances and passing them on initialization.  Note that these connections
    can consist of multiple layers chained together.  The output shape for the
    provided input-to-hidden and hidden-to-hidden connections must be the same.
    If you are looking for a standard, densely-connected recurrent layer,
    please see :class:`RecurrentLayer`.  The output is computed by

    .. math ::
        h_t = \sigma(f_i(x_t) + f_h(h_{t-1}))

    Parameters
    ----------
    incoming : a :class:`L.layers.Layer` instance or a tuple
        The layer feeding into this layer, or the expected input shape.
    input_to_hidden : :class:`L.layers.Layer`
        :class:`L.layers.Layer` instance which connects input to the
        hidden state (:math:`f_i`).  This layer may be connected to a chain of
        layers, which must end in a :class:`L.layers.InputLayer` with the
        same input shape as `incoming`, except for the first dimension: When
        ``precompute_input == True`` (the default), it must be
        ``incoming.output_shape[0]*incoming.output_shape[1]`` or ``None``; when
        ``precompute_input == False``, it must be ``incoming.output_shape[0]``
        or ``None``.
    hidden_to_hidden : :class:`L.layers.Layer`
        Layer which connects the previous hidden state to the new state
        (:math:`f_h`).  This layer may be connected to a chain of layers, which
        must end in a :class:`L.layers.InputLayer` with the same input
        shape as `hidden_to_hidden`'s output shape.
    nonlinearity : callable or None
        Nonlinearity to apply when computing new state (:math:`\sigma`). If
        None is provided, no nonlinearity will be applied.
    hid_init : callable, np.ndarray, theano.shared or :class:`Layer`
        Initializer for initial hidden state (:math:`h_0`).
    backwards : bool
        If True, process the sequence backwards and then reverse the
        output again such that the output from the layer is always
        from :math:`x_1` to :math:`x_n`.
    learn_init : bool
        If True, initial hidden values are learned.
    gradient_steps : int
        Number of timesteps to include in the backpropagated gradient.
        If -1, backpropagate through the entire sequence.
    grad_clipping : float
        If nonzero, the gradient messages are clipped to the given value during
        the backward pass.  See [1]_ (p. 6) for further explanation.
    unroll_scan : bool
        If True the recursion is unrolled instead of using scan. For some
        graphs this gives a significant speed up but it might also consume
        more memory. When `unroll_scan` is True, backpropagation always
        includes the full sequence, so `gradient_steps` must be set to -1 and
        the input sequence length must be known at compile time (i.e., cannot
        be given as None).
    precompute_input : bool
        If True, precompute input_to_hid before iterating through
        the sequence. This can result in a speedup at the expense of
        an increase in memory usage.
    mask_input : :class:`L.layers.Layer`
        Layer which allows for a sequence mask to be input, for when sequences
        are of variable length.  Default `None`, which means no mask will be
        supplied (i.e. all sequences are of the same length).
    only_return_final : bool
        If True, only return the final sequential output (e.g. for tasks where
        a single target value for the entire sequence is desired).  In this
        case, Theano makes an optimization which saves memory.

    Examples
    --------

    The following example constructs a simple `CustomRecurrentLayer` which
    has dense input-to-hidden and hidden-to-hidden connections.

    >>> import lasagne
    >>> n_batch, n_steps, n_in = (2, 3, 4)
    >>> n_hid = 5
    >>> l_in = L.layers.InputLayer((n_batch, n_steps, n_in))
    >>> l_in_hid = L.layers.DenseLayer(
    ...     L.layers.InputLayer((None, n_in)), n_hid)
    >>> l_hid_hid = L.layers.DenseLayer(
    ...     L.layers.InputLayer((None, n_hid)), n_hid)
    >>> l_rec = L.layers.CustomRecurrentLayer(l_in, l_in_hid, l_hid_hid)

    The CustomRecurrentLayer can also support "convolutional recurrence", as is
    demonstrated below.

    >>> n_batch, n_steps, n_channels, width, height = (2, 3, 4, 5, 6)
    >>> n_out_filters = 7
    >>> filter_shape = (3, 3)
    >>> l_in = L.layers.InputLayer(
    ...     (n_batch, n_steps, n_channels, width, height))
    >>> l_in_to_hid = L.layers.Conv2DLayer(
    ...     L.layers.InputLayer((None, n_channels, width, height)),
    ...     n_out_filters, filter_shape, pad='same')
    >>> l_hid_to_hid = L.layers.Conv2DLayer(
    ...     L.layers.InputLayer(l_in_to_hid.output_shape),
    ...     n_out_filters, filter_shape, pad='same')
    >>> l_rec = L.layers.CustomRecurrentLayer(
    ...     l_in, l_in_to_hid, l_hid_to_hid)

    References
    ----------
    .. [1] Graves, Alex: "Generating sequences with recurrent neural networks."
           arXiv preprint arXiv:1308.0850 (2013).
    """
    def __init__(self, incoming_dict, input_to_hidden, hidden_to_hidden,
                 nonlinearity=L.nonlinearities.rectify,
                 hid_init=L.init.Constant(0.),
                 backwards=False,
                 learn_init=False,
                 gradient_steps=-1,
                 grad_clipping=0,
                 unroll_scan=False,
                 precompute_input=False,
                 mask_input=None,
                 only_return_final=False,
                 **kwargs):

        # This layer inherits from a MergeLayer, because it can have three
        # inputs - the layer input, the mask and the initial hidden state.  We
        # will just provide the layer input as incomings, unless a mask input
        # or initial hidden state was provided.

        # e.g. {'input': layer_in, 'hidden_pre': layer_hid}
        self.incoming_dict = incoming_dict
        if not isinstance(incoming_dict, dict):
            raise ValueError("Arg incoming_dict must be a dictionary.")
        if any(not isinstance(value, L.Layer) for value in incoming_dict.values()):
            raise ValueError("Values in incoming_dict must be instances of lasagne.Layer.")
        incomings = [self.incoming_dict['input']]
        self.mask_incoming_index = -1
        self.hid_init_incoming_index = -1
        if mask_input is not None:
            incomings.append(mask_input)
            self.mask_incoming_index = len(incomings)-1
        if isinstance(hid_init, L.Layer):
            incomings.append(hid_init)
            self.hid_init_incoming_index = len(incomings)-1

        super(L.layers.RecurrentContainerLayer, self).__init__(incomings, **kwargs)

        self.input_to_hidden = input_to_hidden
        self.hidden_to_hidden = hidden_to_hidden
        self.learn_init = learn_init
        self.backwards = backwards
        self.gradient_steps = gradient_steps
        self.grad_clipping = grad_clipping
        self.unroll_scan = unroll_scan
        self.precompute_input = precompute_input
        self.precompute_input = False
        self.only_return_final = only_return_final

        if unroll_scan and gradient_steps != -1:
            raise ValueError(
                "Gradient steps must be -1 when unroll_scan is true.")

        # Retrieve the dimensionality of the incoming layer
        input_shape = self.input_shapes[0]

        if unroll_scan and input_shape[1] is None:
            raise ValueError("Input sequence length cannot be specified as "
                             "None when unroll_scan is True")

        # # Check that the input_to_hidden connection can appropriately handle
        # # a first dimension of input_shape[0]*input_shape[1] when we will
        # # precompute the input dot product
        # if (self.precompute_input and
        #         input_to_hidden.output_shape[0] is not None and
        #         input_shape[0] is not None and
        #         input_shape[1] is not None and
        #         # (batch, sequence, ...) -> (batch * sequence, ...)
        #         (input_to_hidden.output_shape[0] !=
        #          input_shape[0]*input_shape[1])):
        #     raise ValueError(
        #         'When precompute_input == True, '
        #         'input_to_hidden.output_shape[0] must equal '
        #         'incoming.output_shape[0]*incoming.output_shape[1] '
        #         '(i.e. batch_size*sequence_length) or be None but '
        #         'input_to_hidden.output_shape[0] = {} and '
        #         'incoming.output_shape[0]*incoming.output_shape[1] = '
        #         '{}'.format(input_to_hidden.output_shape[0],
        #                     input_shape[0]*input_shape[1]))
        #
        # # Check that the first dimension of input_to_hidden and
        # # hidden_to_hidden's outputs match when we won't precompute the input
        # # dot product
        # if (not self.precompute_input and
        #         input_to_hidden.output_shape[0] is not None and
        #         hidden_to_hidden.output_shape[0] is not None and
        #         (input_to_hidden.output_shape[0] !=
        #          hidden_to_hidden.output_shape[0])):
        #     raise ValueError(
        #         'When precompute_input == False, '
        #         'input_to_hidden.output_shape[0] must equal '
        #         'hidden_to_hidden.output_shape[0] but '
        #         'input_to_hidden.output_shape[0] = {} and '
        #         'hidden_to_hidden.output_shape[0] = {}'.format(
        #             input_to_hidden.output_shape[0],
        #             hidden_to_hidden.output_shape[0]))

        # Check that input_to_hidden and hidden_to_hidden output shapes match,
        # but don't check a dimension if it's None for either shape
        if not all(s1 is None or s2 is None or s1 == s2
                   for s1, s2 in zip(input_to_hidden.output_shape[1:],
                                     hidden_to_hidden.output_shape[1:])):
            raise ValueError("The output shape for input_to_hidden and "
                             "hidden_to_hidden must be equal after the first "
                             "dimension, but input_to_hidden.output_shape={} "
                             "and hidden_to_hidden.output_shape={}".format(
                input_to_hidden.output_shape,
                hidden_to_hidden.output_shape))

        # Check that input_to_hidden's output shape is the same as
        # hidden_to_hidden's input shape but don't check a dimension if it's
        # None for either shape
        if not all(s1 is None or s2 is None or s1 == s2
                   for s1, s2 in zip(input_to_hidden.output_shape[1:],
                                     hidden_to_hidden.input_shape[1:])):
            raise ValueError("The output shape for input_to_hidden "
                             "must be equal to the input shape of "
                             "hidden_to_hidden after the first dimension, but "
                             "input_to_hidden.output_shape={} and "
                             "hidden_to_hidden.input_shape={}".format(
                input_to_hidden.output_shape,
                hidden_to_hidden.input_shape))

        if nonlinearity is None:
            self.nonlinearity = L.nonlinearities.identity
        else:
            self.nonlinearity = nonlinearity

        # Initialize hidden state
        if isinstance(hid_init, L.Layer):
            self.hid_init = hid_init
        else:
            self.hid_init = self.add_param(
                hid_init, (1,) + hidden_to_hidden.output_shape[1:],
                name="hid_init", trainable=learn_init, regularizable=False)

    def get_params(self, **tags):
        # Get all parameters from this layer, the master layer
        params = super(L.layers.CustomRecurrentLayer, self).get_params(**tags)
        # Combine with all parameters from the child layers
        params += L.helper.get_all_params(self.input_to_hidden, **tags)
        params += L.helper.get_all_params(self.hidden_to_hidden, **tags)
        return params

    def get_output_shape_for(self, input_shapes):
        # The shape of the input to this layer will be the first element
        # of input_shapes, whether or not a mask input is being used.
        input_shape = input_shapes[0]
        # When only_return_final is true, the second (sequence step) dimension
        # will be flattened
        if self.only_return_final:
            return (input_shape[0],) + self.hidden_to_hidden.output_shape[1:]
        # Otherwise, the shape will be (n_batch, n_steps, trailing_dims...)
        else:
            return ((input_shape[0], input_shape[1]) +
                    self.hidden_to_hidden.output_shape[1:])

    def get_output_for(self, inputs, **kwargs):
        """
        Compute this layer's output function given a symbolic input variable.

        Parameters
        ----------
        inputs : list of theano.TensorType
            `inputs[0]` should always be the symbolic input variable.  When
            this layer has a mask input (i.e. was instantiated with
            `mask_input != None`, indicating that the lengths of sequences in
            each batch vary), `inputs` should have length 2, where `inputs[1]`
            is the `mask`.  The `mask` should be supplied as a Theano variable
            denoting whether each time step in each sequence in the batch is
            part of the sequence or not.  `mask` should be a matrix of shape
            ``(n_batch, n_time_steps)`` where ``mask[i, j] = 1`` when ``j <=
            (length of sequence i)`` and ``mask[i, j] = 0`` when ``j > (length
            of sequence i)``. When the hidden state of this layer is to be
            pre-filled (i.e. was set to a :class:`Layer` instance) `inputs`
            should have length at least 2, and `inputs[-1]` is the hidden state
            to prefill with.

        Returns
        -------
        layer_output : theano.TensorType
            Symbolic output variable.
        """
        # Retrieve the layer input
        input = inputs[0]
        # Retrieve the mask when it is supplied
        mask = None
        hid_init = None
        if self.mask_incoming_index > 0:
            mask = inputs[self.mask_incoming_index]
        if self.hid_init_incoming_index > 0:
            hid_init = inputs[self.hid_init_incoming_index]

        # Input should be provided as (n_batch, n_time_steps, n_features)
        # but scan requires the iterable dimension to be first
        # So, we need to dimshuffle to (n_time_steps, n_batch, n_features)
        input = input.dimshuffle(1, 0, *range(2, input.ndim))
        seq_len, num_batch = input.shape[0], input.shape[1]

        # if self.precompute_input:
        #     # Because the input is given for all time steps, we can precompute
        #     # the inputs to hidden before scanning. First we need to reshape
        #     # from (seq_len, batch_size, trailing dimensions...) to
        #     # (seq_len*batch_size, trailing dimensions...)
        #     # This strange use of a generator in a tuple was because
        #     # input.shape[2:] was raising a Theano error
        #     trailing_dims = tuple(input.shape[n] for n in range(2, input.ndim))
        #     input = T.reshape(input, (seq_len*num_batch,) + trailing_dims)
        #     input = L.layers.get_output(
        #         self.input_to_hidden, input, **kwargs)
        #
        #     # Reshape back to (seq_len, batch_size, trailing dimensions...)
        #     trailing_dims = tuple(input.shape[n] for n in range(1, input.ndim))
        #     input = T.reshape(input, (seq_len, num_batch) + trailing_dims)

        # We will always pass the hidden-to-hidden layer params to step
        non_seqs = L.helper.get_all_params(self.hidden_to_hidden)
        # When we are not precomputing the input, we also need to pass the
        # input-to-hidden parameters to step
        if not self.precompute_input:
            non_seqs += L.helper.get_all_params(self.input_to_hidden)

        # Create single recurrent computation step function
        def step(input_n, hid_previous, *args):
            # Compute the hidden-to-hidden activation
            hid_pre = L.layers.get_output(
                self.hidden_to_hidden, hid_previous, **kwargs)

            # # If the dot product is precomputed then add it, otherwise
            # # calculate the input_to_hidden values and add them
            # if self.precompute_input:
            #     hid_pre += input_n
            # else:
            #     hid_pre += L.layers.get_output(
            #         self.input_to_hidden, input_n, **kwargs)

            incoming_dict = {}
            for key, value in self.incoming_dict.iteritems():
                if key == 'input':
                    incoming_dict[value] = input_n
                elif key == 'hidden_pre':
                    incoming_dict[value] = hid_pre
                else:
                    raise ValueError("Unknown entry in incoming_dict: ({}: {}).".format(key, value))

            hid_out = L.layers.get_output(self.input_to_hidden, incoming_dict, **kwargs)

            # Clip gradients
            if self.grad_clipping:
                hid_out = theano.gradient.grad_clip(
                    hid_out, -self.grad_clipping, self.grad_clipping)

            return self.nonlinearity(hid_out)

        def step_masked(input_n, mask_n, hid_previous, *args):
            # Skip over any input with mask 0 by copying the previous
            # hidden state; proceed normally for any input with mask 1.
            hid = step(input_n, hid_previous, *args)
            hid_out = T.switch(mask_n, hid, hid_previous)
            return [hid_out]

        if mask is not None:
            mask = mask.dimshuffle(1, 0, 'x')
            sequences = [input, mask]
            step_fun = step_masked
        else:
            sequences = input
            step_fun = step

        if not isinstance(self.hid_init, L.Layer):
            # The code below simply repeats self.hid_init num_batch times in
            # its first dimension.  Turns out using a dot product and a
            # dimshuffle is faster than T.repeat.
            dot_dims = (list(range(1, self.hid_init.ndim - 1)) +
                        [0, self.hid_init.ndim - 1])
            hid_init = T.dot(T.ones((num_batch, 1)),
                             self.hid_init.dimshuffle(dot_dims))

        if self.unroll_scan:
            # Retrieve the dimensionality of the incoming layer
            input_shape = self.input_shapes[0]
            # Explicitly unroll the recurrence instead of using scan
            hid_out = L.utils.unroll_scan(
                fn=step_fun,
                sequences=sequences,
                outputs_info=[hid_init],
                go_backwards=self.backwards,
                non_sequences=non_seqs,
                n_steps=input_shape[1])[0]
        else:
            # Scan op iterates over first dimension of input and repeatedly
            # applies the step function
            hid_out = theano.scan(
                fn=step_fun,
                sequences=sequences,
                go_backwards=self.backwards,
                outputs_info=[hid_init],
                non_sequences=non_seqs,
                truncate_gradient=self.gradient_steps,
                strict=True)[0]

        # When it is requested that we only return the final sequence step,
        # we need to slice it out immediately after scan is applied
        if self.only_return_final:
            hid_out = hid_out[-1]
        else:
            # dimshuffle back to (n_batch, n_time_steps, n_features))
            hid_out = hid_out.dimshuffle(1, 0, *range(2, hid_out.ndim))

            # if scan is backward reverse the output
            if self.backwards:
                hid_out = hid_out[:, ::-1]

        return hid_out


def social_mask(sequences):
    """
    Calculate social hidden-state tensor H for single batch of training sequences for all nodes
    :param sequences: [N_NODES, SIZE_BATCH, LENGTH_SEQUENCE_INPUT, 2]
    :return: [N_NODES, SIZE_BATCH, LENGTH_SEQUENCE_INPUT, RANGE_NEIGHBORHOOD, RANGE_NEIGHBORHOOD, N_NODES]
    """

    # mn_pool = numpy.zeros((1, 2), dtype=int)
    # distance_xy = numpy.zeros((1, 2), dtype=float)
    # indication = lambda mn_pool, distance_xy: sum((distance_xy >= SIZE_POOL * (mn_pool - RANGE_NEIGHBORHOOD / 2))
    #                      & (distance_xy < SIZE_POOL * (mn_pool - RANGE_NEIGHBORHOOD / 2 + 1))) == 2

    # mn_pool = T.bvector('mn')
    # distance_xy = T.fvector('distance')
    # # todo test
    # # 1 / 0
    # if_within_grid = T.eq(T.sum((distance_xy >= SIZE_POOL * (mn_pool - RANGE_NEIGHBORHOOD / 2))
    #                      & (distance_xy < SIZE_POOL * (mn_pool - RANGE_NEIGHBORHOOD / 2 + 1))), 2)
    # # distance_xy = other_xy - my_xy
    # # pass in [m, n] in [0, RANGE_NEIGHBORHOOD)
    # indication = theano.function([mn_pool, distance_xy], if_within_grid, allow_input_downcast=True)

    # todo test
    # distance_xy = other_xy - my_xy
    # pass in [m, n] in [0, RANGE_NEIGHBORHOOD)
    # 1 / 0
    indication = lambda mn_pool, distance_xy: (T.ge(distance_xy[0], SIZE_POOL * (mn_pool[0] - RANGE_NEIGHBORHOOD / 2)))\
                                              and T.lt(distance_xy[0], SIZE_POOL * (mn_pool[0] - RANGE_NEIGHBORHOOD / 2 + 1))\
                                              and (T.ge(distance_xy[1], SIZE_POOL * (mn_pool[1] - RANGE_NEIGHBORHOOD / 2)))\
                                              and T.lt(distance_xy[1], SIZE_POOL * (mn_pool[1] - RANGE_NEIGHBORHOOD / 2 + 1))

    # n_nodes = all_nodes.shape[0]
    # n_nodes = T.cast(n_nodes, 'int32')
    # n_nodes = n_nodes.eval()

    ret = T.zeros((N_NODES, SIZE_BATCH, LENGTH_SEQUENCE_INPUT, RANGE_NEIGHBORHOOD, RANGE_NEIGHBORHOOD, N_NODES))
    for inode in xrange(N_NODES):
        for ibatch in xrange(SIZE_BATCH):
            for iseq in xrange(LENGTH_SEQUENCE_INPUT):
                for m in xrange(RANGE_NEIGHBORHOOD):
                    for n in xrange(RANGE_NEIGHBORHOOD):
                        for jnode in xrange(N_NODES):
                            if jnode == inode:
                                continue
                            ind = indication([m, n], sequences[jnode, ibatch, iseq] - sequences[inode, ibatch, iseq])
                            T.set_subtensor(ret[inode, ibatch, iseq, m, n, jnode], ind)

    return ret


def test_model():

    try:

        # todo build the network
        # todo define initializers
        # todo add debug info & assertion
        # todo extract args into config
        # todo write config to .log
        # todo read config from command line args
        # 1 batch for each node
        instants, net_inputs, net_targets = load_batch_for_nodes(all_traces, SIZE_BATCH, N_NODES, 0, True)

        print("Building network ...")

        layer_in = L.layers.InputLayer(name="symbolic-input",
                                             shape=(N_NODES, SIZE_BATCH, LENGTH_SEQUENCE_INPUT, DIMENSION_SAMPLE))
        # [(x, y)]
        layer_xy = L.layers.InputLayer(name="input-xy",
                                             shape=(N_NODES, SIZE_BATCH, LENGTH_SEQUENCE_INPUT, DIMENSION_SAMPLE))
        # e = relu(x, y; We)
        layer_e = L.layers.DenseLayer(layer_xy, name="e", num_units=DIMENSION_EMBED_LAYER,
                                            nonlinearity=L.nonlinearities.rectify, num_leading_axes=3)
        assert match(layer_e.output_shape, (N_NODES, SIZE_BATCH, LENGTH_SEQUENCE_INPUT, DIMENSION_EMBED_LAYER))

        # [N_NODES, SIZE_BATCH, LENGTH_SEQUENCE_INPUT, RANGE_NEIGHBORHOOD, RANGE_NEIGHBORHOOD, N_NODES]
        w_h_to_H = social_mask(net_inputs)
        # layer_social_mask = ExpressionLayer(layer_xy, social_mask, output_shape=(N_NODES, None, LENGTH_SEQUENCE_INPUT, RANGE_NEIGHBORHOOD, RANGE_NEIGHBORHOOD, N_NODES))
        layer_social_mask = L.layers.ExpressionLayer(layer_xy, social_mask, output_shape='auto')
        assert match(layer_social_mask.output_shape,
                     (N_NODES, SIZE_BATCH, LENGTH_SEQUENCE_INPUT, RANGE_NEIGHBORHOOD, RANGE_NEIGHBORHOOD, N_NODES))

        layer_shuffled_social_mask = L.layers.DimshuffleLayer(layer_social_mask, (0, 1, 2, 3, 4, 5, 'x'))
        assert match(layer_shuffled_social_mask.output_shape,
                     (N_NODES, SIZE_BATCH, LENGTH_SEQUENCE_INPUT, RANGE_NEIGHBORHOOD, RANGE_NEIGHBORHOOD, N_NODES, 1))

        # layer_prev_h = InputLayer(name="previous h", shape=(N_NODES, None, LENGTH_SEQUENCE_INPUT, DIMENSION_HIDDEN_LAYERS))
        layer_prev_h = L.layers.InputLayer(name="previous-h", shape=(N_NODES * SIZE_BATCH, LENGTH_SEQUENCE_INPUT, DIMENSION_HIDDEN_LAYERS))
        layer_reshaped_h = L.layers.ReshapeLayer(layer_prev_h, (N_NODES, -1, [1], [2]))
        assert match(layer_reshaped_h.output_shape, (N_NODES, SIZE_BATCH, LENGTH_SEQUENCE_INPUT, DIMENSION_HIDDEN_LAYERS))

        # [N_NODES, SIZE_BATCH, LENGTH_SEQUENCE_INPUT, DIMENSION_HIDDEN_LAYERS]
        # shuffle & broadcast into: [1, SIZE_BATCH, LENGTH_SEQUENCE_INPUT, 1, 1, N_NODES, DIMENSION_HIDDEN_LAYERS] to match social matrix
        layer_shuffled_h = L.layers.DimshuffleLayer(layer_reshaped_h, ('x', 1, 2, 'x', 'x', 0, 3))
        assert match(layer_shuffled_h.output_shape,
                     (1, SIZE_BATCH, LENGTH_SEQUENCE_INPUT, 1, 1, N_NODES, DIMENSION_HIDDEN_LAYERS))

        # todo test lambda
        # Perform elementwise multiplication & sum by -2nd dimension (N_NODES
        # layer_H = ExpressionMergeLayer([layer_shuffled_social_mask, layer_shuffled_h], lambda lt, rt: (T.mul(lt, rt)).sum(-2)
        #                                , output_shape="auto")
        layer_H = L.layers.ElemwiseMergeLayer([layer_shuffled_social_mask, layer_shuffled_h], T.mul)
        assert match(layer_H.output_shape
                     , (N_NODES, SIZE_BATCH, LENGTH_SEQUENCE_INPUT, RANGE_NEIGHBORHOOD, RANGE_NEIGHBORHOOD, N_NODES, DIMENSION_HIDDEN_LAYERS))

        layer_H = L.layers.ExpressionLayer(layer_H, lambda x: x.sum(-2), output_shape="auto")

        assert match(layer_H.output_shape
                     , (N_NODES, SIZE_BATCH, LENGTH_SEQUENCE_INPUT, RANGE_NEIGHBORHOOD, RANGE_NEIGHBORHOOD, DIMENSION_HIDDEN_LAYERS))

        # todo reshape batch & node dim together all the time?
        layer_a = L.layers.DenseLayer(layer_H, name="a", num_units=DIMENSION_EMBED_LAYER,
                                            nonlinearity=L.nonlinearities.rectify, num_leading_axes=3)
        assert match(layer_a.output_shape, (N_NODES, SIZE_BATCH, LENGTH_SEQUENCE_INPUT, DIMENSION_EMBED_LAYER))
        assert match(layer_e.output_shape, layer_a.output_shape)

        layer_in_lstms = L.layers.ConcatLayer([layer_e, layer_a], 3, name="e & a")
        assert match(layer_in_lstms.output_shape, (N_NODES, SIZE_BATCH, LENGTH_SEQUENCE_INPUT, 2 * DIMENSION_EMBED_LAYER))

        layers_in_lstms = []
        for inode in xrange(0, N_NODES):
            layers_in_lstms += [L.layers.SliceLayer(layer_in_lstms, inode, axis=0)]
        assert all(
            match(ilayer_in_lstm.output_shape, (SIZE_BATCH, LENGTH_SEQUENCE_INPUT, 2 * DIMENSION_EMBED_LAYER)) for ilayer_in_lstm
            in layers_in_lstms)

        # Create an LSTM layers for the 1st node
        layer_lstm_0 = L.layers.LSTMLayer(layers_in_lstms[0], DIMENSION_HIDDEN_LAYERS, name="LSTM-0",
                                                nonlinearity=L.nonlinearities.tanh,
                                                hid_init=L.init.Constant(0.0), cell_init=L.init.Constant(0.0),
                                                only_return_final=False)
        assert match(layer_lstm_0.output_shape, (SIZE_BATCH, LENGTH_SEQUENCE_INPUT, DIMENSION_HIDDEN_LAYERS))

        layers_lstm = [layer_lstm_0]

        # Create params sharing LSTMs for the rest (n - 1) nodes,
        # which have params exactly the same as LSTM_0
        for inode in xrange(1, N_NODES):
            # Overdated implement for lasagne/lasagne
            layers_lstm += [
                L.layers.LSTMLayer(layers_in_lstms[inode], DIMENSION_HIDDEN_LAYERS, name="LSTM-" + str(inode)
                                         , nonlinearity=L.nonlinearities.tanh, hid_init=L.init.Constant(0.0),
                                         cell_init=L.init.Constant(0.0), only_return_final=False,
                                         ingate=L.layers.Gate(W_in=layer_lstm_0.W_in_to_ingate,
                                                                    W_hid=layer_lstm_0.W_hid_to_ingate,
                                                                    W_cell=layer_lstm_0.W_cell_to_ingate,
                                                                    b=layer_lstm_0.b_ingate),
                                         outgate=L.layers.Gate(W_in=layer_lstm_0.W_in_to_outgate,
                                                                     W_hid=layer_lstm_0.W_hid_to_outgate,
                                                                     W_cell=layer_lstm_0.W_cell_to_outgate,
                                                                     b=layer_lstm_0.b_outgate),
                                         forgetgate=L.layers.Gate(W_in=layer_lstm_0.W_in_to_forgetgate,
                                                                        W_hid=layer_lstm_0.W_hid_to_forgetgate,
                                                                        W_cell=layer_lstm_0.W_cell_to_forgetgate,
                                                                        b=layer_lstm_0.b_forgetgate),
                                         cell=L.layers.Gate(W_in=layer_lstm_0.W_in_to_cell,
                                                                  W_hid=layer_lstm_0.W_hid_to_cell,
                                                                  W_cell=None,
                                                                  b=layer_lstm_0.b_cell,
                                                                  nonlinearity=L.nonlinearities.tanh
                                                                  ))]

        layer_concated_lstms = L.layers.ConcatLayer(layers_lstm, axis=0)
        assert match(layer_concated_lstms.output_shape, (N_NODES * SIZE_BATCH, LENGTH_SEQUENCE_INPUT, DIMENSION_HIDDEN_LAYERS))
        layer_h = layer_concated_lstms
        # # not sure about whether to reshape or not
        # layer_h = ReshapeLayer(layer_concated_lstms, (N_NODES, -1, [1], [2]))
        # assert match(layer_h.output_shape, (N_NODES, None, LENGTH_SEQUENCE_INPUT, DIMENSION_HIDDEN_LAYERS))

        # test forwarding connections: pass
        randoms_h_prev = numpy.random.random(layer_prev_h.shape).astype('float32')
        temp_outputs = L.layers.get_output(layer_h, {layer_xy: net_inputs, layer_prev_h: randoms_h_prev})
        temp_outputs = temp_outputs.eval()

        # tried the CustomRecurrentLayer approach
        layer_h_to_h = L.layers.NonlinearityLayer(L.layers.InputLayer((N_NODES * SIZE_BATCH, LENGTH_SEQUENCE_INPUT, DIMENSION_HIDDEN_LAYERS)),
                                                        nonlinearity=L.nonlinearities.rectify)
        layer_social_lstm = L.layers.CustomRecurrentLayer(layer_xy, layer_h, layer_h_to_h, nonlinearity=None,
                                                                hid_init=L.init.Constant(.0))

        # # tried the RecurrentContainerLayer aproach
        # cell_social_lstm = L.layers.CustomRecurrentCell(layer_xy, layer_h, layer_h_to_h
        #                                                         , nonlinearity=None, hid_init=L.init.Constant(.0))['output']
        # layer_social_lstm = L.layers.RecurrentContainerLayer({layer_xy: layer_in}, cell_social_lstm, {layer_prev_h: layer_h})


        # # trying rewriting CustomRecurrentCell
        # layer_h_to_h = L.layers.NonlinearityLayer(L.layers.InputLayer((N_NODES * SIZE_BATCH, LENGTH_SEQUENCE_INPUT, DIMENSION_HIDDEN_LAYERS))
        #                                                 , nonlinearity=L.nonlinearities.rectify)
        # cell_social_lstm = SocialLSTMCell(layer_xy, layer_prev_h, layer_h, layer_h_to_h
        #                                                         , nonlinearity=None, hid_init=L.init.Constant(.0))['output']
        # layer_social_lstm = L.layers.RecurrentContainerLayer({layer_xy: layer_in}, cell_social_lstm)
        #
        # randoms_in = numpy.random.random(net_inputs.shape).astype('float32')
        # temp_outputs = L.layers.get_output(layer_social_lstm, {layer_in: randoms_in}).eval()
        # temp_outputs = L.layers.get_output(layer_social_lstm).eval({layer_in.input_var: randoms_in})

        net_outputs = temp_outputs


    except KeyboardInterrupt:
        pass

    # except Exception, e:
    #     print str(type(e)) + e.message


# def test_model():

    # all_samples, all_targets = load_batch_for_nodes(read_traces_from_path(PATH_TRACE_FILES),
    #                                                        SIZE_BATCH, [], 0, True)

    # l_social_pooling = InputLayer(shape=(SIZE_BATCH, LENGTH_SEQUENCE_INPUT, DIMENSION_SAMPLE))
    # First, we build the network, starting with an input layer
    # Recurrent layers expect input of shape
    # (batch_size, SEQ_LENGTH, num_features)

    # We now build the LSTM layer which takes l_in as the input layer
    # We clip the gradients at GRAD_CLIP to prevent the problem of exploding gradients.

    # # only_return_final = True?
    # l_forward_1 = LSTMLayer(
    #     layer_in, DIMENSION_HIDDEN_LAYERS, grad_clipping=GRAD_CLIP,
    #     nonlinearity=tanh)
    #
    # # Parameter sharing between multiple layers can be achieved by using the same Theano shared variable instance
    # # for their parameters. e.g.
    # #
    # # l1 = DenseLayer(l_in, num_units=100)
    # # l2 = DenseLayer(l_in, num_units=100, W=l1.W)
    #
    # # DenseLayer: full connected
    # # The output of l_forward_2 of shape (batch_size, N_HIDDEN) is then passed through the dense layer to create
    # # The output of this stage is (size_batch, dim_sample)
    # l_out = DenseLayer(l_forward_2, num_units=1, W=Normal())

    # print("Building network ...")

    # # Theano tensor for the targets
    # target_values = T.fmatrix('target_output')
    #
    # # network_output: [size_batch, dim_sample]
    # # get_output produces a variable for the output of the net
    # # network_output = get_output(l_out)
    #
    # # whats categorical cross-entropy?
    # # The loss function is calculated as the mean of the (categorical) cross-entropy between the prediction and target.
    # cost = T.nnet.categorical_crossentropy(network_output, target_values).mean()
    #
    # # Retrieve all parameters from the network
    # all_params = get_all_params(temp_layer_out, trainable=True)
    #
    # # Compute RMSProp updates for training
    # print("Computing updates ...")
    # updates = L.updates.rmsprop(cost, all_params, LEARNING_RATE_RMSPROP)
    #
    # # Theano functions for training and computing cost
    # print("Compiling functions ...")
    # train = theano.function([layer_in.input_var, target_values], cost, updates=updates, allow_input_downcast=True)
    # compute_cost = theano.function([layer_in.input_var, target_values], cost, allow_input_downcast=True)
    #
    # predict = theano.function([layer_in.input_var], network_output, allow_input_downcast=True)
    #
    # def try_it_out():
    #     preds = numpy.zeros((node_count, DIMENSION_SAMPLE))
    #     ins, tars = load_batch_for_nodes(all_traces, 1, [], 0, True)
    #
    #     for i in range(LENGTH_SEQUENCE_OUTPUT):
    #         for inode in range(node_count):
    #             preds[inode] = predict(ins[inode])
    #             print preds[inode], tars[inode, :, LENGTH_SEQUENCE_OUTPUT - 1, :]
    #
    # print("Training ...")
    # p = 0
    # try:
    #     for it in xrange(N_SEQUENCES * NUM_EPOCH / SIZE_BATCH):
    #         try_it_out()  # Generate text using the p^th character as the start.
    #
    #         avg_cost = 0
    #         for _ in range(LOG_SLOT):
    #             for node in range(N_NODES):
    #                 # 获取(输入序列,实际输出)配对
    #                 inputs, targets = load_batch_for_nodes(all_traces, SIZE_BATCH, [], p, True)
    #
    #                 p += LENGTH_SEQUENCE_INPUT + SIZE_BATCH - 1
    #                 if p + SIZE_BATCH + LENGTH_SEQUENCE_INPUT >= N_SEQUENCES:
    #                     print('Carriage Return')
    #                     p = 0
    #
    #                 # 训练
    #                 avg_cost += train(inputs[node], targets[node, :, LENGTH_SEQUENCE_OUTPUT - 1, :])
    #             print("Epoch {} average loss = {}".format(it * 1.0 * LOG_SLOT / N_SEQUENCES * SIZE_BATCH,
    #                                                       avg_cost / LOG_SLOT))
    #     try_it_out()

    # except KeyboardInterrupt:
    #     pass


if __name__ == '__main__':
    test_model()
