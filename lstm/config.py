# coding:utf-8

__all__ = [
    "global_configuration",
    "update_config",
    "test"
]


config_pool = {
    'default':
        {
            # Path for trace files
            'path_trace': 'res/trace/',
            # Path for logs
            'path_log': 'log/',
            # How often should we check the output
            'log_slot': 1,
            # Show warning info or not
            'show_warning': False,
            # Level of printing detail
            # 0 means mandatory printing only
            'print_level': 3,
            # How many nodes to learn on
            'num_node': 1,
            # Dimension of sample input: 2 for [x, y]; 3 for [sec, x, y]
            'dimension_sample': 3,
            # If only a full size batch will be accepted
            'strict_batch_size': True,
            # Length of edge when coordinates need to be mapped to grid
            'grain_grid': 100
        },
    'debug':
        {

            # Nano-size net config for debugging

            # Length of observed sequence
            'length_sequence_input': 4,
            # Length of predicted sequence
            'length_sequence_output': 4,
            # Number of units in embedding layer ([x, y] -> e)
            'dimension_embed_layer': 2,
            # Number of units in hidden (LSTM) layers
            # n: single layer of n units
            # (m, n): m * layers of n units
            'dimension_hidden_layer': (2, 2),

            # """
            # Social-LSTM config
            # """
            # 'size_pool': 100,
            # # x * x of pools around each node
            # 'range_neighborhood': 4,

            # Batch Size
            'size_batch': 10,
            # Number of epochs to train the net
            'num_epoch': 2,
            # Optimization learning rate
            'learning_rate_rmsprop': .03,
            'rho_rmsprop': .9,
            'epsilon_rmsprop': 1e-8,
            # All gradients above this will be clipped
            'grad_clip': 100
        },
    'run':
        {
            # Length of observed sequence
            'length_sequence_input': 10,
            # Length of predicted sequence
            'length_sequence_output': 10,
            # Number of units in embedding layer ([x, y] -> e)
            'dimension_embed_layer': 64,
            # Number of units in hidden (LSTM) layers
            # n: single layer of n units
            # (m, n): m * layers of n units
            'dimension_hidden_layer': (10, 32),

            # """
            # Social-LSTM config
            # """
            # 'size_pool': 100,
            # # x * x of pools around each node
            # 'range_neighborhood': 4,

            # Batch Size
            'size_batch': 10,
            # Number of epochs to train the net
            'num_epoch': 50,
            # Optimization learning rate
            'learning_rate_rmsprop': .003,
            'rho_rmsprop': .95,
            'epsilon_rmsprop': 1e-8,
            # All gradients above this will be clipped
            'grad_clip': 0
        }
}


def _get_config_from_pool_(key='default'):
    try:
        if key not in config_pool:
            available_keys = config_pool.keys()
            raise ValueError("get_config_from_pool @ config: "
                             "Invalid key '%s'. Must choose from %s."
                             % (key, available_keys))

        return config_pool[key]

    except:
        raise


global_configuration = _get_config_from_pool_('default')


def update_config(key=None, config=None):
    try:
        global global_configuration
        if key is not None:
            global_configuration.update(_get_config_from_pool_(key=key))
        if config is not None:
            if isinstance(config, dict):
                global_configuration.update(config)
            else:
                raise ValueError("update_config @ config: "
                                 "Expect <dict> while getting %s instead." % type(config))
    except:
        raise


if __debug__:
    update_config(key='debug')
else:
    update_config(key='run')


def test():
    try:
        run = _get_config_from_pool_()
        config_pool['debug']['show_warning'] = True
        debug = _get_config_from_pool_(key='debug')
        try:
            invalid = _get_config_from_pool_(key='default')
        except Exception, e:
            pass
        try:
            invalid = _get_config_from_pool_(key='invalid-key')
        except Exception, e:
            pass
        update_config(config={'_': True})
    except:
        raise
