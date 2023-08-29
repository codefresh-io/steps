import os
import sys
import semver

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

    @staticmethod
    def printFail(message, end = '\n'):
        sys.stderr.write('\x1b[1;31m' + message.strip() + '\x1b[0m' + end)

# def getVariable(key, env):
#     if not StepUtility.getEnvironmentVariable(key, env):
#         print((str(key).split('SEMVERSIONER_')[1]).lower())
#         print( eval('DEF_'+'ACTION') )
#         the_var = eval('DEF_'+'ACTION') + '1'
#         print(the_var)
#         print(DEF_ACTION)

def exportResults(result): 
    print("\nExporting Results")

    env_file_path = "/meta/env_vars_to_export"
    if not os.path.exists(env_file_path):
        print(f"Result is '{result}'")        
    else:
        env_file = open(env_file_path, "a")          
        env_file.write("SEMVERSIONER_RESULT=" + result + "\n")
        env_file.close()

def main():
    env = os.environ
    action = StepUtility.getEnvironmentVariable('SEMVERSIONER_ACTION', env).lower()
    version = StepUtility.getEnvironmentVariable('SEMVERSIONER_VERSION', env).lower()
    part = StepUtility.getEnvironmentVariable('SEMVERSIONER_PART', env).lower()
    versionToCompare = StepUtility.getEnvironmentVariable('SEMVERSIONER_VERSION_TO_COMPARE', env).lower()

    version = semver.VersionInfo.parse(version)
    
    print(f"Action is '{action}'")
    print(f"Semver version is '{version}'")
    print(f"Semver part is '{part}'")
    print(f"Semver version to compare is '{versionToCompare}'")

    result = None
    if action == "bump":
        if part == "major":
            result = version.bump_major()
        elif part == "minor":
            result = version.bump_minor()
        else:
            result = version.bump_patch()
        print(f'Resulting semver version: {result}')

    elif action == "compare":
      result = version.compare(versionToCompare)
      print(f'Comparison result: {result}')
      comparisonTerms = ["less than","equal to","greater than"]
      print(f'{version} is {comparisonTerms[int(result)+1]} {versionToCompare}')
    else:
        StepUtility.printFail("Action not recognized")

    exportResults(str(result))
    

if __name__ == "__main__":
    main()