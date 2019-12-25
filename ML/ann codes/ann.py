import tensorflow as tf
import numpy as np
import random
import ops

class ann:
    learning_rate = 0.001
    model_restore = False
    working_dir = None
    hidden_layer_list=None
    activation_list=None
    batch_size = 64
    epochs = 10
    dropout = .7
    test_result = None
    train_result = None
    no_of_features = None
    no_of_classes = None
    loss_type = 'softmax'
    optimizer_type = 'adam'

    def __init__(self):
        return

    def setup(self):
        tf.reset_default_graph()
        self.test_result = []
        self.train_result = []
        self.x = tf.placeholder(dtype=tf.float32, shape=[None, self.no_of_features], name="input")
        self.y = tf.placeholder(dtype=tf.float32, shape=[None, self.no_of_classes], name="labels")
        self.lr = tf.placeholder("float", shape=[])
        self.is_train = tf.placeholder(tf.bool, shape=[])

        self.logits = self.model(self.x, self.is_train)

        with tf.name_scope('Output'):
            self.cross_entropy = ops.get_loss(self.logits, self.y, self.loss_type)

            hypothesis = tf.nn.softmax(self.logits, name="softmax")
            self.prediction = tf.argmax(hypothesis, 1, name='Prediction')
            correct_prediction = tf.equal(self.prediction, tf.argmax(self.y, 1), name='Correct_prediction')
            self.accuracy = tf.reduce_mean(tf.cast(correct_prediction, tf.float32), name='Accuracy')
            tf.summary.scalar("Cross_Entropy", self.cross_entropy)
            tf.summary.scalar("Accuracy", self.accuracy)

        with tf.name_scope('Optimizer'):
            # learningRate = tf.train.exponential_decay(learning_rate=learning_rate, global_step=1,
            #                                          decay_steps=shape[0], decay_rate=0.97, staircase=True,
            #                                          name='Learning_Rate')
            if (self.optimizer_type=='adadelta'):
                self.optimizer = tf.train.AdadeltaOptimizer(self.lr).minimize(self.cross_entropy)
            elif (self.optimizer_type=='gdecent'):
                self.optimizer = tf.train.GradientDescentOptimizer(self.lr).minimize(self.cross_entropy)
            elif (self.optimizer_type=='momentum'):
                self.optimizer = tf.train.MomentumOptimizer(self.lr, .9, use_nesterov=True).minimize(self.cross_entropy)
            else:
                self.optimizer = tf.train.AdamOptimizer(self.lr).minimize(self.cross_entropy)

        return

    def model(self, x, is_training):
        op = ops.get_n_hidden_layers(x,self.hidden_layer_list,self.activation_list,
                                     initializer='xavier')
        return ops.get_hidden_layer(op, 'output_layer', self.no_of_classes, 'none', initializer='xavier')

    def train(self, train, val_data=None, max_keep=100):
        init = tf.global_variables_initializer()
        session = tf.InteractiveSession()
        session.run(init)

        saver = tf.train.Saver(max_to_keep=max_keep)
        if self.model_restore == True and self.working_dir != None:
            name = ops.look_for_last_checkpoint(self.working_dir + "/model/")
            if name is not None:
                saver.restore(session, self.working_dir + "/model/" + name)
                print('Model Succesfully Loaded : ', name)
        if self.working_dir != None:
            merged = tf.summary.merge_all()
            train_writer = tf.summary.FileWriter(self.working_dir + '/train', session.graph)
            test_writer = tf.summary.FileWriter(self.working_dir + '/test')
        test_result = []
        train_result = []

        for epoch in range(1, self.epochs + 1):
            ind_list = [i for i in range(len(train['x']))]
            random.shuffle(ind_list)
            train['x'] = train['x'][ind_list]
            train['y'] = train['y'][ind_list]
            epoch_loss = 0
            acc = 0
            i = 0
            batch_iteration = 0
            while i < len(train['x']):
                start = i
                end = i + self.batch_size
                if (end > len(train['x'])): end = len(train['x'])
                batch_x = train['x'][start:end]
                batch_y = train['y'][start:end]
                if self.working_dir != None:
                    summary, _, loss, batch_acc = session.run(
                        [merged, self.optimizer, self.cross_entropy, self.accuracy],
                        feed_dict={self.x: batch_x, self.y: batch_y, self.lr: self.learning_rate, self.is_train: True})
                else:
                    _, loss, batch_acc = session.run([self.optimizer, self.cross_entropy, self.accuracy],
                                                     feed_dict={self.x: batch_x, self.y: batch_y,
                                                                self.lr: self.learning_rate, self.is_train: True})
                epoch_loss += loss
                acc += batch_acc
                batch_iteration += 1
                i += self.batch_size
            if self.working_dir != None:
                train_writer.add_summary(summary, epoch)
            train_result.append([epoch, epoch_loss / batch_iteration, acc / batch_iteration])
            if val_data != None:
                epoch_loss = 0
                acc = 0
                i = 0
                batch_iteration = 0
                while i < len(val_data['x']):
                    start = i
                    end = i + self.batch_size
                    if (end > len(val_data['x'])): end = len(val_data['x'])
                    batch_x = val_data['x'][start:end]
                    batch_y = val_data['y'][start:end]
                    if self.working_dir != None:
                        summary, loss, batch_acc = session.run([merged, self.cross_entropy, self.accuracy],
                                                               feed_dict={self.x: batch_x, self.y: batch_y,
                                                                          self.lr: self.learning_rate,
                                                                          self.is_train: False})
                    else:
                        loss, batch_acc = session.run([self.cross_entropy, self.accuracy],
                                                      feed_dict={self.x: batch_x, self.y: batch_y,
                                                                 self.lr: self.learning_rate, self.is_train: False})
                    epoch_loss += loss
                    acc += batch_acc
                    batch_iteration += 1
                    i += self.batch_size
                if self.working_dir != None:
                    test_writer.add_summary(summary, epoch)
                test_result.append([epoch, epoch_loss / batch_iteration, acc / batch_iteration])

                print("Training:", train_result[len(train_result) - 1], "Val:", test_result[len(test_result) - 1])
            else:
                print("Training :", train_result[len(train_result) - 1])

            if self.working_dir != None:
                save_path = saver.save(session, self.working_dir + "/model/" + 'model', global_step=epoch)
        print('Training Succesfully Complete')
        self.test_result = test_result
        self.train_result = train_result
        session.close()

    def check_restore(self):
        init = tf.global_variables_initializer()
        session = tf.InteractiveSession()
        saver = tf.train.Saver()
        print (self.working_dir + '/model/')
        saver.restore(session, tf.train.latest_checkpoint(self.working_dir + '/model/'))
        session.close()

    def predict(self, test):
        session = tf.InteractiveSession()
        saver = tf.train.Saver()
        print (self.working_dir + '/model/')
        saver.restore(session, tf.train.latest_checkpoint(self.working_dir + '/model/'))
        merged = tf.summary.merge_all()
        if 'x' in test and test['x'].shape[0] > 0:
            i = 0
            iteration = 0
            acc = 0
            test_prediction = []
            j = 0
            while i < len(test['x']):
                start = i
                end = i + self.batch_size
                if (end > len(test['x'])): end = len(test['x'])
                batch_x = test['x'][start:end]
                if 'y' in test and test['y'].shape[0] > 0:
                    batch_y = test['y'][start:end]
                    pred, batch_acc = session.run([self.prediction, self.accuracy],
                                                  feed_dict={self.x: batch_x, self.y: batch_y, self.is_train: False})
                    acc += batch_acc
                else:
                    pred = session.run([self.prediction], feed_dict={self.x: batch_x, self.is_train: False})
                iteration += 1
                i += self.batch_size
                if isinstance(pred, list):
                    test_prediction += pred[0].tolist()
                else:
                    test_prediction += pred.tolist()
            if 'y' in test and test['y'].shape[0] > 0:
                return np.array(test_prediction), acc / iteration
            else:
                return np.array(test_prediction)
            session.close()
