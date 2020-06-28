import os

class StepUtility:    
    @staticmethod
    def getEnvironmentVariable(key, env):
        value = env.get(key, "")
        if value == "${{" + key + "}}":
            value = ""
        return value

    @staticmethod
    def printCleanException(exc):
        print('{}: {}'.format(type(exc).__name__, exc))
