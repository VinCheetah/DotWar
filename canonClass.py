from pipe import ClassicPipe


class Canon:

    def __init__(self, dot):
        self.dot = dot
        self.pipes = set()

    def shoot(self):
        for pipe in self.pipes:
            pipe.shoot()

    def add_pipe(self, pipe):
        self.pipes.add(pipe)

    def display(self):
        raise NotImplementedError


class PipeCanon(Canon):

    def __init__(self, dot):
        Canon.__init__(self, dot)
        self.add_pipe(ClassicPipe(dot, 0))

    def display(self):
        for pipe in self.pipes:
            pipe.display()