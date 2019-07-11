class ModelClass():
    def __init__(self):
        '''
        Initializes the two members the class holds:
        The -- las -- file.
        the data from las file.
        the message to return back to the user on errors
        '''
        self.file = None

    def setFile(self, file):
        self.file = file

    def getFile(self):
        return self.file