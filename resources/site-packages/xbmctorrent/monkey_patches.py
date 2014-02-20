from xbmcswift2.request import Request


old_init = Request.__init__
def init_with_args(self, *args, **kwargs):
    old_init(self, *args, **kwargs)
    self.args_dict = {}
    for k, v in self.args.items():
        self.args_dict[k] = v[0]
Request.__init__ = init_with_args
