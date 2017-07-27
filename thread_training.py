import threading
import os
import tensorflow as tf
from driving_data import DrivingData
import model
from database import Settings


class TrainingThread(threading.Thread):
    lock = threading.Lock()
    running = True

    def __init__(self, statusbar):
        self.driving_data = DrivingData()
        with TrainingThread.lock:
            TrainingThread.running = True

        threading.Thread.__init__(self, daemon=True)

        self.statusbar = statusbar
        country_string = Settings().get_value(Settings.COUNTRIES_MODEL)
        self.country = country_string.split(",")

    def stop(self):
        with TrainingThread.lock:
            TrainingThread.running = False

    def run(self):
        LOGDIR = './save'

        # print("Images:", self.driving_data.num_images)

        sess = tf.InteractiveSession(graph=model.g)

        L2NormConst = 0.001

        train_vars = tf.trainable_variables()

        loss = tf.reduce_mean(tf.square(tf.subtract(model.y_, model.y))) + tf.add_n(
            [tf.nn.l2_loss(v) for v in train_vars]) * L2NormConst
        train_step = tf.train.AdamOptimizer(1e-4).minimize(loss)
        sess.run(tf.initialize_all_variables())

        # create a summary to monitor cost tensor
        tf.summary.scalar("loss", loss)
        # merge all summaries into a single op
        merged_summary_op = tf.summary.merge_all()

        saver = tf.train.Saver()

        # op to write logs to Tensorboard
        logs_path = './logs'
        summary_writer = tf.summary.FileWriter(logs_path, graph=tf.get_default_graph())

        epochs = 30
        batch_size = 100

        # train over the dataset about 30 times
        loss_value = 0.0
        for epoch in range(epochs):
            for i in range(int(self.driving_data.num_images / batch_size)):
                if not TrainingThread.running:
                    return None

                xs, ys = self.driving_data.LoadTrainBatch(batch_size)
                train_step.run(feed_dict={model.x: xs, model.y_: ys, model.keep_prob: 0.8})
                if i % 10 == 0:
                    xs, ys = self.driving_data.LoadValBatch(batch_size)
                    loss_value = loss.eval(feed_dict={model.x: xs, model.y_: ys, model.keep_prob: 1.0})
                    self.statusbar.showMessage("Epoch: %d, Step: %d, Loss: %g" % (epoch, epoch * batch_size + i, loss_value))
                    #print("Epoch: %d, Step: %d, Loss: %g" % (epoch, epoch * batch_size + i, loss_value))

                # write logs at every iteration
                summary = merged_summary_op.eval(feed_dict={model.x: xs, model.y_: ys, model.keep_prob: 1.0})
                summary_writer.add_summary(summary, epoch * batch_size + i)

                if i % batch_size == 0:
                    if not os.path.exists(LOGDIR):
                        os.makedirs(LOGDIR)
                    checkpoint_path = os.path.join(LOGDIR, "model_%s.ckpt" % self.country[0])
                    filename = saver.save(sess, checkpoint_path)
            if loss_value < 0.25:

                return None
