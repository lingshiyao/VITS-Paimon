class Test:
    def run(self, a:int, b:int, c:int, *args):
        print(a, b, c, args)

print("here")
test = Test();
test.run(1, 2, 3, "asdas")

getattr(test, "run")(1, 2, 3)

def call_method(obj, method_name, *args, **kwargs):
    return getattr(obj, method_name)(*args, **kwargs)



call_method(test, "run", 1, 2, 3)