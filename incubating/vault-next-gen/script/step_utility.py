import os

class StepUtility:    
    @staticmethod
    def getEnvironmentVariable(key, env):
        value = env.get(key, "")
        if value == "${{" + key + "}}":
            value = ""
        return value
