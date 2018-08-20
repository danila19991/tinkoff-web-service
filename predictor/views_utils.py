from ml_algorithm.shell import Shell


def make_prediction(input_data):
    sh = Shell()
    sh.predict(input_data)
    sh.test()
    return sh.predictions
