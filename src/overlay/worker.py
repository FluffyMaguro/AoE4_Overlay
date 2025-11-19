import sys
import traceback
from typing import Callable, Optional

from PyQt6 import QtCore

from overlay.logging_func import get_logger

logger = get_logger(__name__)

THREADPOOL = QtCore.QThreadPool()


class WorkerSignals(QtCore.QObject):
    '''
    Defines the signals available from a running worker thread.
    Supported signals are:

    finished
        No data
    
    error
        `tuple` (exctype, value, traceback.format_exc() )
    
    result
        `object` data returned from processing, anything

    '''
    finished = QtCore.pyqtSignal()
    error = QtCore.pyqtSignal(tuple)
    result = QtCore.pyqtSignal(object)
    progress = QtCore.pyqtSignal(object)


class Worker(QtCore.QRunnable):
    """
    Worker thread
    Inherits from QRunnable to handler worker thread setup, signals and wrap-up.
    The function callback to run on this worker thread. Supplied args and kwargs will be passed through to the runner.
    `fn` function
    `arg` Arguments to pass to the callback function
    `kwargs` Keywords to pass to the callback function
    """
    def __init__(self, fn, *args, **kwargs):
        super(Worker, self).__init__()
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()

        if 'progress_callback' in kwargs:
            self.kwargs['progress_callback'] = self.signals.progress

    @QtCore.pyqtSlot()
    def run(self):
        """ Runs the function and emits signals (error, result, finished) """
        try:
            try:
                result = self.fn(*self.args, **self.kwargs)
            except Exception:
                logger.exception("")
                exctype, value = sys.exc_info()[:2]
                self.signals.error.emit(
                    (exctype, value, traceback.format_exc()))
            else:
                self.signals.result.emit(result)
            finally:
                self.signals.finished.emit()
        except RuntimeError:
            logger.exception('Error with pyqt thread. The app likely closed.')
        except Exception:
            logger.exception("")


def scheldule(result_callback: Callable,
              worker_function: Callable,
              *args,
              error_callback: Optional[Callable] = None):
    """ Scheldules work on the worker function and passes the result to the callback function"""
    thread = Worker(worker_function, *args)
    thread.signals.result.connect(result_callback)
    if error_callback is not None:
        thread.signals.error.connect(error_callback)
    THREADPOOL.start(thread)