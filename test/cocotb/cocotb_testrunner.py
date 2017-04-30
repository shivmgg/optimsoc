#!/usr/bin/python3

import os
import yaml
import sys
import glob
import argparse
import subprocess

tests = []
objdir = None

class CocotbTest():
    def __init__(self, manifest_path):
        self._manifest_path = None
        self.manifest = None
        self.objdir = os.path.join(os.getcwd(), 'objdir')
        
        self.manifest_path = manifest_path
        
    def _abspath(self, path, basedir):
        if path.startswith('/'):
            return path
        return os.path.abspath(os.path.join(basedir, path))
        
    def _parse_manifest(self, manifest_path):
        with open(manifest_path, 'r') as fp_manifest:
            try:
                manifest = yaml.safe_load(fp_manifest)
            except yaml.YAMLError as e:
                print(e)
                return False

        # ensure absolute paths in the list of sources
        manifest_dir = os.path.dirname(manifest_path)
        manifest['sources'][:] = map(lambda x: self._abspath(x, manifest_dir), 
                                     manifest['sources'])            
            
        manifest['manifest_dir'] = os.path.abspath(manifest_dir) 
        return manifest

    @property
    def manifest_path(self):
        return self._manifest_path
    
    @manifest_path.setter
    def manifest_path(self, manifest_path):
        self.manifest = self._parse_manifest(manifest_path)
        self._manifest_path = manifest_path

    def _get_makefile_vcs(self):
        makefile = "# Auto-generated Makefile by OpTiMSoC for Synopsys VCS\n"
        makefile += "SIM=vcs\n"
        makefile += "VERILOG_SOURCES=" + " \\\n\t".join(self.manifest["sources"]) + "\n"
        makefile += "TOPLEVEL=" + self.manifest["toplevel"] + "\n"
        makefile += "MODULE=" + self.manifest["module"] + "\n"
        
        # HDL parameters (passed to toplevel module in the design)
        args_hdl_params = []
        for name, value in self.manifest["parameters"].items():
            args_hdl_params.append("-pvalue+{}={}".format(name, value))

        #        sim_args = " ".join(args_hdl_params)
        sim_args = "+lint=all" 
        compile_args = "+lint=all -timescale=1ns/10ps " + " ".join(args_hdl_params) 

        makefile += "SIM_ARGS=" + sim_args + "\n"
        makefile += "COMPILE_ARGS=" + compile_args + "\n"

        makefile += "include $(COCOTB)/makefiles/Makefile.inc\n"
        makefile += "include $(COCOTB)/makefiles/Makefile.sim\n"

        return makefile
    
    def _prepare_objdir(self):
        # create Makefile
        makefile_contents = self._get_makefile_vcs()
        with open("{}/Makefile".format(self.objdir), "w") as fp_makefile:
            fp_makefile.write(makefile_contents)
    
    def run(self, gui, loglevel='INFO'):
        self._prepare_objdir()
        
        env = os.environ
        env['PYTHONPATH'] = self.manifest['manifest_dir']
        env['COCOTB_LOG_LEVEL'] = loglevel
        subprocess.run(["make", "SIM_ARGS=-gui"], cwd=self.objdir, env=env)
        


def run_tests(tests, gui=False, loglevel='INFO'):
    if len(tests) > 1:
        printf("You cannot run multiple tests with GUI. Please run again with a single test.")
        exit(1)

    for t in tests:
        t.run(gui, loglevel)


def discover_tests(test_search_base):
    for f in glob.iglob('{}/**/manifest.yaml'.format(test_search_base), recursive=True):
        cocotb_test = CocotbTest(manifest_path=f)
        cocotb_test.objdir = objdir
        tests.append(cocotb_test)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Testrunner for cocotb testbenches')
    parser.add_argument("-o", "--objdir", 
                        help="object directory [default: %(default)s]",
                        default=os.path.join(os.getcwd(), "objdir"))
    parser.add_argument("-l", "--loglevel", 
                        help="cocotb log level [default: %(default)s]",
                        default='INFO')
    parser.add_argument("-g", "--gui", action='store_true',
                        help="show GUI[default: %(default)s]",
                        default=False)
    parser.add_argument('dir', nargs='?', default=os.getcwd())

    args = parser.parse_args()

    objdir = args.objdir
    test_search_base = args.dir
                
    if not os.path.isdir(test_search_base):
        printf("Specified search base not an existing directory.")
        sys.exit(1)


    discover_tests(test_search_base)
    run_tests(tests, gui=args.gui, loglevel=args.loglevel)
