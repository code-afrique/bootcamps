class Node():
    def toBlock(self, frame):
        return None

    def findRow(self, lineno):
        return None

class PassNode(Node):
    def __init__(self):
        super().__init__()

    def toBlock(self, frame, level, block):
        return block.newPassBlock(frame, self, level, block)
