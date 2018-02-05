#! /usr/bin/python

#########################################################################################################
# The purpose of this script is to update the yml scrips automatically for rancher                      #
#########################################################################################################

import sys, os, argparse
from argparse import RawTextHelpFormatter
from os import listdir
from subprocess import Popen


parser=argparse.ArgumentParser(description='''
#########################################################################################################
 The purpose of this python script is to take the -tag argument and update the rancher compose yml files                                                                   
       that are on github with the new tags. 			   
#########################################################################################################			   
			   ''',
			   formatter_class=RawTextHelpFormatter)
parser.add_argument('-folder', help='The name of the docker folder enter in the rancher-catalog/templates folder (Required)', required=True)
parser.add_argument('-image', help='The tag that needs to update in the catalog (Required)', required=True)
parser.add_argument('--git', help='Commit changes to git',const=True, default=False,action='store_const')
parser.set_defaults(feature=False)
#parse input argument and split by ":"
args=parser.parse_args()

dockerFolder=args.folder
dockerImage=args.image

#open and figure out the most "current" configuration yml files by looping though files and determining which name is the highest number
FileDir="templates/"+dockerFolder
CurrentYML="-1"
for f in os.listdir(FileDir):
	if os.path.isdir(FileDir+"/"+f):
		if int(CurrentYML) < int(f):
			CurrentYML=f
CurrentYMLdir="templates/"+dockerFolder+"/"+CurrentYML
#Check the docker-compose.yml file in the current configuration folder for the latest tag
dockercompose_file=open(CurrentYMLdir+"/docker-compose.yml","r")
dockerCompose_uptodate=0
for line in dockercompose_file:
	if "dnadave/"+dockerImage in line:
		dockerCompose_uptodate=1
dockercompose_file.close()


#if the current configuration has the correct tag, stop runnning and quit
if dockerCompose_uptodate == 1:
	print "\n"
	print "Rancher configuration files are up to date!"
	sys.exit(0)
#if the current configuration does not have the correct tag, create a new folder one number higher than the previous version
#and copy the files from the previous config, updating the tag info
elif dockerCompose_uptodate == 0:
	print "Updating Rancher configuration files..."

	#create new Rancher config folder
	NewYML=1+int(CurrentYML)
	NewYMLdir="templates/"+dockerFolder+"/"+str(NewYML)
	os.mkdir(NewYMLdir)
	
	#create new docker-compose.yml
	dockercompose_file=open(CurrentYMLdir+"/docker-compose.yml","r")
	dockercompose_file_new=open(NewYMLdir+"/docker-compose.yml","w")
	for line in dockercompose_file:
		if "image: dnadave/"+dockerImage.split(":")[0] in line:
			line = "  image: dnadave/"+dockerImage+"\n"
		dockercompose_file_new.write(line)
	dockercompose_file.close()
	dockercompose_file_new.close()
		
	#create new rancher-compose.yml
	ranchercompose_file=open(CurrentYMLdir+"/rancher-compose.yml","r")
	ranchercompose_file_new=open(NewYMLdir+"/rancher-compose.yml","w")
	for line in ranchercompose_file:
		if "version:" in line:
			versionName = line.split('"')[1]
			versionNum = float(versionName.replace("v","").split("-")[0])+.1
			line = "  version: \"v"+str(versionNum)+"-"+dockerImage.split(":")[1]+"\"\n"
		ranchercompose_file_new.write(line)
	
	dockercompose_file.close()
	dockercompose_file_new.close()
	
	if args.git:
		#the following commands will:
		#	change the dir to rancher-catalog
		#	add the new files and commit them
		#	push the update
		commit_Commands=[]
		#commit_Commands.append('cd rancher-catalog')
		commit_Commands.append('git add '+NewYMLdir+"/*)
		commit_Commands.append('git commit -am "Updated Rancher config to include '+dockerImage+'"')
		#commit_Commands.append('git push')
		commit_Commands = ";".join(commit_Commands)
		print commit_Commands
		p=Popen(commit_Commands,shell=True)
		p.communicate()
	
	sys.exit(0)
