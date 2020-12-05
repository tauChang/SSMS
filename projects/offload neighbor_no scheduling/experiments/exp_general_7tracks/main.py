"""

    This example

    @author: Isaac Lera & Carlos Guerrero

"""
import matplotlib

matplotlib.use('Agg') # Tau: for drawing

import os
import time
import json
import networkx as nx
import logging.config
import subprocess
#import osmnx as ox

import collections
import pickle
import random
import numpy as np
from collections import Counter


from yafs.application import Application, Message
from yafs.topology import Topology
from yafs.distribution import *
import yafs.distribution
from yafs.utils import get_shortest_random_path
from yafs.coverage import Voronoi, CircleCoverage
from yafs.utils import *

from yafs.customMovement import MovementUpdate

import trackanimation

from yafs.core import Sim

from yafs.population import *  # for population
from customSelection import DeviceSpeedAwareRouting  # for selection
from customPlacement import FogPlacement, CloudPlacement   # for placement


def create_applications_from_json(data):
    applications = {}
    for app in data:
        # Create application
        a = Application(name=app["name"])
        # Set modules
        modules = []
        for module in app["module"]:
            modules.append({module["name"]: {"RAM": module["RAM"], "Type": module["Type"]}})
        a.set_modules(modules)

        # Set messages
        ms = {}
        for message in app["message"]:
            # print "Creando mensaje: %s" %message["name"]
            ms[message["name"]] = Message(message["name"], message["src"], message["dst"],
                                          instructions=message["instructions"], bytes=message["bytes"])
            if message["src"] == "Source":
                a.add_source_messages(ms[message["name"]])

        for idx, message in enumerate(app["service"]):
            if "message_out" in message.keys():
                a.add_service_module(message["module"], ms[message["message_in"]], ms[message["message_out"]],
                                     fractional_selectivity, threshold=1.0)
        #    else:
        #        a.add_service_module(message["module"], ms[message["message_in"]])

        applications[app["name"]] = a

    return applications


def main(path, path_results, number_simulation_steps, tracks, topology, case, it, doExecutionVideo, coverage, generate_animation, map_boundary):
    """
    Prepares the rest of experiment configuration
    """

    """
    APPLICATION
    """
    dataApp = json.load(open(path + 'appDefinition.json'))
    app = create_applications_from_json(dataApp)["SSMS"] # since we only have one application now

    """
    PLACEMENT algorithm
    """
    # In our model only initial cloud placements are enabled
    placement = FogPlacement(name="FogPlacement")
    placement.scaleService({"Reception":1, "Computation": 1}) # Tau: Not really sure about the number

    """
    SELECTOR and Deploying algorithm
    """
    selector = DeviceSpeedAwareRouting()

    """
    Population
    """
    pop = Statical(name="Statical Population")

    dDistribution = deterministicDistribution(name="Deterministic",time=100)  # generate task every 100 ms
    pop.set_src_control({"model": "car", "number":1,"message": app.get_message("Task_Request"), "distribution": dDistribution})
    pop.set_sink_control({"model": "car","number":1,"module":app.get_sink_modules()})

    """
    SIMULATION ENGINE
    """
    s = Sim(topology, default_results_path=path_results + "Results_%s_%i" % (case, it))

    """
    Deploying application with specific distribution in the simulator
    # Penultimate phase
    """
    s.deploy_app(app, placement, pop, selector)

    """
    MOBILE - parametrization
    """
    s.load_user_tracks(tracks)

    s.load_map(map_boundary) # if empty, core.py gets by itself
    s.set_coverage_class(CircleCoverage, radius=coverage)  # radius in KM
    # s.set_coverage_class(Voronoi)
    s.set_mobile_fog_entities({})

    # Expensive task
    # It generates a short video (mp4) with the movement of users in the coverage (without network update)
    if generate_animation and not os.path.isfile(result_folder + "animation_one.mp4"):
        s.generate_animation(path_results+"animation_%s" % case)

    """
    Creating the custom monitor that manages the movement of mobile entities
    """
    stop_time = number_simulation_steps * time_in_each_step


    dStart = deterministicDistributionStartPoint(0, time_in_each_step, name="Deterministic")
    evol = MovementUpdate(path_results, doExecutionVideo)
    s.deploy_monitor("Traces_localization_update", evol, dStart,
                     **{"sim": s, "routing": selector, "case": case, "stop_time": stop_time, "it": it})

    s.set_movement_control(evol)

    """
    RUNNING
    """
    logging.info(" Performing simulation: %s %i " % (case, it))
    s.run(stop_time, test_initial_deploy=False, show_progress_monitor=False, mobile_behaviour=True)

    """
    Storing results from customized strategies
    """
    # Getting some info
    s.print_debug_assignaments()


def do_video_from_execution_snaps(output_file, png_names, framerate):
    cmdstring = ('ffmpeg',
                 '-loglevel', 'quiet',
                 '-framerate', str(framerate),
                 '-i', png_names,
                 '-r', '25',
                 '-s', '1280x960',
                 '-pix_fmt', 'yuv420p',
                 output_file + '.mp4'
                 )

    subprocess.call(cmdstring)


if __name__ == '__main__':
    # Load config json file
    config = json.load(open('config.json'))

    # Logging can be avoided by commenting these three lines
    import logging.config

    if "logging_file_path" in config:
        logging.config.fileConfig(config["logging_file_path"])
    else:
        logging.config.fileConfig("src/logging.ini")
    #

    ##
    # STEP-0:
    # Initial parametrization of the experiment
    ##

    # As we perform the simulations in external server, we simplify the path value according with the WD_path
    experiment_path = config["exp_dir_path"] + "/"
    print "Experiment Path ", experiment_path
    #

    # Experiment variables
    nSimulations = config["num_simulation"]
    number_simulation_steps = config["num_simulation_step"]
    time_in_each_step = config["time_in_each_step"]  # the interval of how long the network topology is updated

    result_folder = config["result_dir_path"] + "/"

    trajectories_path = config["trajectory_dir_path"] + "/"

    try:
        os.makedirs(result_folder)
    except OSError:
        None

    ##
    # STEP-1:
    # Initializing of the common and static context of each simulation
    ##

    # 1.1 Mobile entities trough GPX traces
    # The track normalization is an expensive computational task. A cached file is generated in each temporal path
    if os.path.isfile(result_folder + "normalized_trajectories.csv"):
        input_directory = result_folder + "normalized_trajectories.csv"  #
        logging.info("Loading trajectories from (cached file): %s" % input_directory)
        tracks = trackanimation.read_track(input_directory)
    else:
        input_directory = trajectories_path  # can load csv files
        logging.info("Loading trajectories from (raw files): %s" % input_directory)
        tracks = trackanimation.read_track(input_directory)
        tracks = tracks.time_video_normalize(time=number_simulation_steps, framerate=1)  # framerate must be one
        tracks.export(result_folder + "normalized_trajectories")

    # 1.2 Network infrastructure
    # Endpoint entities must have three attributes: level(=0) and lat/lng coordinates
    t = Topology()
    dataNetwork = json.load(open(experiment_path + 'networkDefinition.json'))
    t.load_all_node_attr(dataNetwork)

    # Performing multiple simulations
    for i in range(nSimulations):
        random.seed(i)
        np.random.seed(i)
        logging.info("Running Mobility Case - %s" % experiment_path)
        start_time = time.time()

        main(path=experiment_path,
             path_results=result_folder,
             number_simulation_steps=number_simulation_steps,
             tracks=tracks,
             topology=t,
             case='one',
             doExecutionVideo=True,  # expensive task
             it=i,
             coverage=config["server_coverage_radius"],
             generate_animation=config["generate_animation"],
             map_boundary=config["map_boundary"])

        print("\n--- %s seconds ---" % (time.time() - start_time))
        do_video_from_execution_snaps(result_folder + "animation_snaps", 'snap_%05d.png', 10)

    print "Simulation Done!"