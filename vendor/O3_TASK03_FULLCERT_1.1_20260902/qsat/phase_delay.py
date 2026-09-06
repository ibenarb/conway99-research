"""Test-only exec wrapper used to make a real phase observably slow."""
import os,sys,time
time.sleep(float(sys.argv[1]));os.execvp(sys.argv[2],sys.argv[2:])
