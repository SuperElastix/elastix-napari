from qtpy.QtWidgets import QMessageBox


def error(message):
    """
    Shows a pop up with the given error message.
    """
    print("ERROR: ", message)
    QMessageBox.critical(None, "Error", message)
