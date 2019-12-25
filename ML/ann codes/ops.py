import tensorflow as tf
import numpy as np
import string
def look_for_last_checkpoint(mode_dir):
    try:
        fr = open(mode_dir + 'checkpoint', "r")
    except:
        return None
    f_line = fr.readline()
    start = f_line.find('"')
    end = f_line.rfind('"')
    return f_line[start + 1:end]

def get_variable(name,shape, initial='random', dtype=tf.float32):
    if initial.lower() == 'random':
        initial_weight = tf.random_normal_initializer(stddev=0.05, dtype=dtype)
    elif initial.lower() == 'truncated':
        initial_weight = tf.truncated_normal_initializer(stddev=0.05, dtype=dtype)
    elif initial.lower() == 'uniform':
        initial_weight = tf.random_uniform_initializer()
    elif initial.lower() == 'xavier':
        initial_weight = tf.contrib.layers.xavier_initializer()
    elif initial.lower() == 'xavier_conv2d':
        initial_weight = tf.contrib.layers.xavier_initializer_conv2d()
    else:
        initial_weight = initial
    return tf.get_variable(name, shape=shape, initializer=initial_weight, dtype=dtype)

def bias_variable(shape,value=None):
    if value==None:
        initial = tf.constant(0.001, shape=shape)
    else:
        initial = tf.constant(value, shape=shape)
    return tf.Variable(initial)
def conv2d(input,name,kernel_size, strides, padding='SAME', initial='xavier', groups=1, with_bias=True):
    if groups == 1:
        W = get_variable(name, kernel_size, initial)
        conv = tf.nn.conv2d(input, W, strides, padding=padding, )
        if with_bias:
            return tf.nn.bias_add(conv, bias_variable([kernel_size[3]]))
        return conv
    else:
        convolve = lambda i, k: tf.nn.conv2d(i, k, strides=strides, padding=padding)
        W = get_variable(name, kernel_size, initial)
        input_groups = tf.split(axis=3, num_or_size_splits=groups, value=input)
        weight_groups = tf.split(axis=3, num_or_size_splits=groups, value=W)
        output_groups = [convolve(i, k) for i, k in zip(input_groups, weight_groups)]
        conv = tf.concat(axis=3, values=output_groups)
        if with_bias:
            tf.nn.bias_add(conv, bias_variable([kernel_size[3]]))
        return conv
def flatten(input):
    op_shape = input.get_shape().as_list()[1:]
    dim=1
    for value in op_shape:
        dim =dim*value
    return tf.reshape(input, [-1, dim])
def avg_pool(input, size, strides, padding='SAME'):
    return tf.nn.avg_pool(input, size, strides, padding)

def max_pool(input, size, strides, padding='SAME'):
    return tf.nn.max_pool(input, size, strides, padding)

def global_avg_pool(input,dim=[1,2]):
    assert input.get_shape().ndims == 4
    return tf.reduce_mean(input,dim)

def batch_normalization(input,is_training):
    return tf.contrib.layers.batch_norm(input, scale=True, is_training=is_training,updates_collections=None)

def get_hidden_layer(input,name,size=50, activation='relu', initializer='xavier', dtype=tf.float32):
    node_shape = input.get_shape().as_list()[1:]
    weight = get_variable('hidden_'+str(name),[node_shape[0], size], initializer, dtype)
    bias =  get_variable('Baises_'+str(name),[1, size], initializer, dtype)
    output = tf.add(tf.matmul(input, weight), bias)
    if isinstance(activation, int):
        output = get_activation_function(output, activation)
    elif isinstance(activation, str):
        output = get_activation_function(output, activation)
    elif isinstance(activation, list):
        for a in activation:
            output = get_activation_function(output, a)
    elif activation==None:
        output=get_activation_function(output,'relu')
    return output

def get_n_hidden_layers(input,hidden_sizes=None,activation_function_list=None,initializer=None):
    try:
        no_of_layers = len(hidden_sizes)
    except:
        no_of_layers = 0
    for i in range(no_of_layers):
        with tf.name_scope('Hidden_Layer_' + str(i + 1)):
            if i==0:
                output=get_hidden_layer(input,i,hidden_sizes[i],activation=activation_function_list[i],initializer=initializer)
            else:
                output = get_hidden_layer(output,i,hidden_sizes[i], activation=activation_function_list[i],initializer=initializer)
    return output


def leaky_relu(node, parameter=0.1):
    shape = node.get_shape().as_list()[1:]
    const = tf.constant(value=parameter, shape=shape)
    return tf.maximum(node * const, node)

def get_activation_function(input, choice=2,value=None):
    if choice == 0 or str(choice).lower() == 'none':
        return input
    if choice == 1 or str(choice).lower() == 'relu':
        return tf.nn.relu(input)
    if choice == 2 or str(choice).lower() == 'leaky_relu':
        if value==None:
            value=0.1
        return leaky_relu(input,value)
    if choice == 3 or str(choice).lower() == 'crelu':
        return tf.nn.crelu(input)
    if choice == 4 or str(choice).lower() == 'relu6':
        return tf.nn.relu6(input)
    if choice == 5 or str(choice).lower() == 'elu':
        return tf.nn.elu(input)
    if choice == 6 or str(choice).lower() == 'sigmoid':
        return tf.nn.sigmoid(input)
    if choice == 7 or str(choice).lower() == 'tanh':
        return tf.nn.tanh(input)
    if choice == 8 or str(choice).lower() == 'softplus':
        return tf.nn.softplus(input)
    if choice == 9 or str(choice).lower() == 'softsign':
        return tf.nn.softsign(input)
    if choice == 10 or str(choice).lower() == 'softmax':
        return tf.nn.softmax(logits=input)
    if choice == 11 or str(choice).lower() == 'dropout':
        if value==None:
            value=0.5
        return tf.nn.dropout(input, value)

def multi_layer_bank(input,out_channel={'1': 32, '3': 32, '5': 32}, strides=[1, 1, 1, 1]):
    input_shape = input.get_shape().as_list()[1:]
    con_1x1 = conv2d(input,'MLB_Conv_0_1',kernel_size=[1, 1, input_shape[2], out_channel['1']], strides=strides,
                          initial='xavier')
    con_3x3 = conv2d(input,'MLB_Conv_0_2', kernel_size=[3, 3, input_shape[2], out_channel['3']], strides=strides,
                          initial='xavier')
    con_5x5 = conv2d(input,'MLB_Conv_0_3', kernel_size=[5, 5, input_shape[2], out_channel['5']], strides=strides,
                          initial='xavier')
    pool = max_pool(input, size=[1, 3, 3, 1], strides=strides)
    output = tf.concat([con_1x1, con_3x3, con_5x5, pool], 3)
    return output

def multi_layer_bank3(input,out_channel={'1': 32, '3': 32, '5': 32}, strides=[1, 1, 1, 1]):
    input_shape = input.get_shape().as_list()[1:]
    con_1x1 = conv2d(input,'MLB_Conv_0_1',kernel_size=[1, 1, input_shape[2], out_channel['1']], strides=strides,
                          initial='xavier')
    con_3x3 = conv2d(input,'MLB_Conv_0_2', kernel_size=[3, 3, input_shape[2], out_channel['3']], strides=strides,
                          initial='xavier')
    #con_5x5 = conv2d(input,'MLB_Conv_0_3', kernel_size=[5, 5, input_shape[2], out_channel['5']], strides=strides,
    #                      initial='xavier')
    pool = max_pool(input, size=[1, 3, 3, 1], strides=strides)
    output = tf.concat([con_1x1, con_3x3, pool], 3)
    return output

def get_loss(logits, labels, loss_type='softmax'):
    if loss_type.lower() == "softmax":
        cross_entropy = tf.reduce_mean(tf.nn.softmax_cross_entropy_with_logits(logits=logits, labels=labels, name='Cross_entropy'))
    elif loss_type.lower() == "hinge":
       cross_entropy = tf.reduce_mean(tf.losses.hinge_loss(logits=logits, labels=labels))
    elif loss_type.lower() == "huber":
       cross_entropy = tf.reduce_mean(tf.losses.huber_loss(labels=labels, predictions=logits))
    elif loss_type.lower() == "log":
       cross_entropy = tf.reduce_mean(tf.losses.log_loss(labels=labels, predictions=logits))
    elif loss_type.lower() == "absolute":
       cross_entropy = tf.reduce_mean(tf.losses.absolute_difference(labels=labels, predictions=logits))
    elif loss_type.lower() == "mse":
       cross_entropy = tf.losses.mean_squared_error(labels=labels, predictions=logits)
    elif loss_type.lower() == "mpse":
       cross_entropy = tf.losses.mean_pairwise_squared_error(labels=labels, predictions=logits)
    elif loss_type.lower() == "sigmoid":
       cross_entropy = tf.losses.sigmoid_cross_entropy(labels,logits)
    elif loss_type.lower() == "binary_crossentropy":
        cross_entropy = tf.reduce_mean(tf.keras.losses.binary_crossentropy(logits,labels))
    elif loss_type == "sparse_softmax":
        cross_entropy = tf.reduce_mean(tf.nn.sparse_softmax_cross_entropy(logits=logits, labels=labels))
    return cross_entropy

def get_regularization(self, input_loss, loss_type='l2', regularization_coefficient=0.0001):
    if loss_type == 'l2':
        beta = tf.constant(regularization_coefficient)
        regularized_loss = input_loss + beta * tf.add_n(
            [tf.nn.l2_loss(var) for var in tf.trainable_variables()], 'L2_regurlization')
        return regularized_loss
    if loss_type == 'l1':
        l1_regularizer = tf.contrib.layers.l1_regularizer(scale=regularization_coefficient, scope=None)
        weights = tf.trainable_variables()
        regularization_penalty = tf.contrib.layers.apply_regularization(l1_regularizer, weights)
        regularized_loss = input_loss + regularization_penalty
        return regularized_loss
    if loss_type == 'elastic_net':
        l1_regularizer = tf.contrib.layers.l1_regularizer(scale=regularization_coefficient[0], scope=None)
        l2_regularizer = tf.contrib.layers.l2_regularizer(scale=regularization_coefficient[1], scope=None)
        weights = tf.trainable_variables()
        l1_regularization_penalty = tf.contrib.layers.apply_regularization(l1_regularizer, weights)
        l2_regularization_penalty = tf.contrib.layers.apply_regularization(l2_regularizer, weights)
        regularized_loss = input_loss + l1_regularization_penalty + l2_regularization_penalty
        return regularized_loss
