import time
from datetime import datetime

import tensorflow as tf

from Players.AIPlayers.TakNet import TakNet

FLAGS = tf.app.flags.FLAGS
tf.app.flags.DEFINE_string('trainDir', 'trained_models/tak_train_test', """Directory where to write event logs and checkpoint.""")
tf.app.flags.DEFINE_integer('maxSteps', 40200, """Number of batches to run.""")


# train TakNet for a number of steps
def train():
    with tf.Graph().as_default():
        globalStep = tf.contrib.framework.get_or_create_global_step()

        # get data
        boards, pieceCounts, realScores = TakNet.inputs(False)

        # instantiate prediction graph
        scores = TakNet.inference(boards, pieceCounts)

        # calculate loss
        totalLoss, meanLoss = TakNet.loss(realScores, scores)

        # train for one batch and update parameters
        trainOp = TakNet.train(totalLoss, meanLoss, globalStep)

        # class to log loss over time
        # noinspection PyAttributeOutsideInit
        # noinspection PyUnusedLocal
        # noinspection PyClassHasNoInit
        class LoggerHook(tf.train.SessionRunHook):

            def begin(self):
                self._step = -1

            def before_run(self, runContext):
                self._step += 1
                self._startTime = time.time()
                return tf.train.SessionRunArgs(meanLoss)

            def after_run(self, runContext, runValues):
                duration = time.time() - self._startTime
                lossValue = runValues.results
                if self._step % 10 == 0:
                    examplesPerStep = FLAGS.batchSize
                    examplesPerSecond = examplesPerStep/duration
                    secondsPerBatch = float(duration)

                    formatString = '%s: step %d, loss = %.2f (%.1f examples/sec; %.3f sec/batch)'
                    print(formatString % (datetime.now(), self._step, lossValue, examplesPerSecond, secondsPerBatch))

        saver = tf.train.Saver(max_to_keep=10000000)
        with tf.train.MonitoredTrainingSession(
                checkpoint_dir=FLAGS.trainDir,
                hooks=[tf.train.StopAtStepHook(last_step=FLAGS.maxSteps),
                       tf.train.NanTensorHook(meanLoss),
                       tf.train.CheckpointSaverHook(FLAGS.trainDir, save_steps=50, saver=saver),
                       LoggerHook()],
                config=tf.ConfigProto()) as monitoredSession:

            while not monitoredSession.should_stop():
                monitoredSession.run(trainOp)


# noinspection PyUnusedLocal
def main(argv=None):
    train()

if __name__ == "__main__":
    if tf.gfile.Exists(FLAGS.trainDir):
        tf.gfile.DeleteRecursively(FLAGS.trainDir)
    tf.gfile.MakeDirs(FLAGS.trainDir)
    tf.app.run()
