from subprocess import Popen, PIPE
import os, shutil
import os.path
from os import path
import subprocess

baseDir = os.path.abspath(os.getcwd())

#creates if not exists tmp folder and the source file in it
def setupEnvironment(src_code, absolute_file_name):
    if( not path.exists('tmp') ):
        os.mkdir('tmp')

    file = open('tmp/' + absolute_file_name, "w")
    file.write(src_code)
    file.close()


#blindly delete everything in tmp which resides in current directory
def cleanupEnvironment():
    folder = 'tmp'

    for filename in os.listdir(folder):
        file_path = os.path.join(folder, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print('Failed to delete %s. Reason: %s' % (file_path, e))

def runSubProcess(cmdLine):
    cmnd = " ".join(cmdLine)

    output = None
    err = None

    try:
    
        output = subprocess.check_output(cmnd, stderr=subprocess.STDOUT, shell=True, universal_newlines=True)
    
    except subprocess.CalledProcessError as exc:
        err = exc.output
        #print("Status : FAIL\n", exc.returncode, exc.output)

    return (output, err)

#absolute_file_name includes file name with extension
def produceResponse(src_code, absolute_file_name):
    ext = absolute_file_name[absolute_file_name.find(".") + 1:]
    file_name = absolute_file_name[ : absolute_file_name.find(".") ]

    setupEnvironment(src_code, absolute_file_name)

    response = {}
    output = ""
    err = ""
    printOrInterpret = "print"

    #interpreted types... php, python
    if(ext == "py"):
        printOrInterpret = "print"
        (output, err) = runSubProcess([ "python", "tmp/"+absolute_file_name, "." ])

    #which need to be compiled separately and executed separately
    if(ext == "c" or ext == "cpp" or ext == "java"):

        try:
            if(ext == "c"):
                (output, err) = runSubProcess([ "gcc", "tmp/" + absolute_file_name, "-o", "tmp/" + file_name + ".exe" ])
                
                if(err != None):
                    pass
                else:
                    (output, err) = runSubProcess([ "tmp\\"+ file_name +".exe" ])

            if(ext == "cpp"):
                (output, err) = runSubProcess( ["g++", "tmp/" + absolute_file_name, "-o", "tmp/" + file_name + ".exe"])
                
                if(err != None):
                    pass
                else:
                    (output, err) = runSubProcess([ "tmp\\" + file_name + ".exe" ])

            if(ext == "java"):
                (output, err) = runSubProcess( ["javac", "tmp/" + absolute_file_name ])

                if(err != None):
                    pass
                else:
                    (output, err) = runSubProcess([ "java", "-classpath", "tmp" , file_name ])

        except subprocess.CalledProcess as exc:
            err = exc.output

    cleanupEnvironment()

    response["out"] = output
    response["err"] = err
    response["printOrInterpret"] = printOrInterpret # "print" or "interpret" on client side

    return response