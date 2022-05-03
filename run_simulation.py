#! /usr/bin/env python3

import os
import json
import math
import yaml
import copy
import time
import shlex
import shutil
import random
import datetime
import subprocess




class Robot(object):
    """docstring for Robot"""
    def __init__(self, n, loc, batt_level, skills, config):
        super(Robot, self).__init__()
        self.id = n
        self.pose = self.get_pose_from_loc(loc)
        self.batt_level = batt_level
        self.skills = skills
        self.config = config
        self.repre = {'id': self.id,
                      'pose': self.pose,
                      'batt_level': self.batt_level,
                      'skills': self.skills
                      }
        self.motion_pkg_name = 'motion_ctrl'
        self.pytrees_pkg_name = 'py_trees'
        self.motiond = None
        self.pytreesd = None
        self.build_motion_docker()
        self.build_pytrees_docker()

    def get_pose_from_loc(self, loc):
        poses = {
            "IC Corridor": [-37, 15],
            "IC Room 1": [-39.44, 33.98, 0.00],
            "IC Room 2": [-32.88, 33.95, 3.14],
            "IC Room 3": [-40.23, 25.37, 0.00],
            "IC Room 4": [-33.90, 18.93, 3.14],
            "IC Room 5": [-38.00, 21.50, 0.00],
            "IC Room 6": [-38.00, 10.00, 0.00],
            "PC Corridor": [-19, 16],
            "PC Room 1": [-28.50, 18.00,-1.57],
            "PC Room 2": [-27.23, 18.00,-1.57],
            "PC Room 3": [-21.00, 18.00,-1.57],
            "PC Room 4": [-19.00, 18.00,-1.57],
            "PC Room 5": [-13.50, 18.00,-1.57],
            "PC Room 6": [-11.50, 18,-1.57],
            "PC Room 7": [-4, 18,-1.57],
            "PC Room 8": [-27.23, 13.00, 1.57],
            "PC Room 9": [-26.00, 13.00, 1.57],
            "PC Room 10": [-18.00, 13.00, 1.57],
            "Reception": [-1, 20],
            "Pharmacy Corridor": [0, 8],
            "Pharmacy": [-2, 2.6],
        }
        return poses[loc]

    def get_id(self):
        return self.id

    def get_pose(self):
        return self.pose

    def get_batt_level(self):
        return self.batt_level

    def get_motion_docker(self):
        return ('motion_ctrl'+str(self.id), self.motiond)

    def get_pytrees_docker(self):
        return ('py_trees'+str(self.id), self.pytreesd)

    def get_params(self):
        return self.repre

    def __str__(self):
        return json.dumps(self.repre)

    def build_motion_docker(self):
        '''
        motion_ctrl:
            build:
              context: ./docker
              dockerfile: Dockerfile.motion
            container_name: motion_ctrl
            runtime: runc
            depends_on:
              - master
            ports:
              - "11311:11311"
            volumes:
              - ./docker/motion_ctrl:/ros_ws/src/motion_ctrl/
              - ./docker/turtlebot3_hospital_sim:/ros_ws/src/turtlebot3_hospital_sim/
            environment:
              - "ROS_HOSTNAME=motion_ctrl"
              - "ROS_MASTER_URI=http://motion_ctrl:11311"
              - "ROBOT_NAME=turtlebot1"
            env_file:
              - test.env
            command: /bin/bash -c "source /ros_ws/devel/setup.bash && roslaunch motion_ctrl base_navigation.launch & rosrun topic_tools relay /move_base_simple/goal /turtlebot1/move_base_simple/goal"
            tty: true
            privileged: true
            networks:
              morsegatonet:
                ipv4_address: 10.2.0.6
        '''
        package_name = 'motion_ctrl'
        container_name = self.motion_pkg_name+str(self.id)
        self.motiond = {
            'build': {
                'context' : './docker',
                'dockerfile': 'Dockerfile.motion',
            },
            'container_name': container_name,
            'runtime': 'runc',
            'depends_on': ['master'],
            # 'ports': ["9090:9090"],
            'env_file': [env_path],
            'volumes': [f'./docker/{self.motion_pkg_name}:/ros_ws/src/{self.motion_pkg_name}/', './docker/turtlebot3_hospital_sim:/ros_ws/src/turtlebot3_hospital_sim/', './log/:/root/.ros/logger_sim/'],
            'environment': [f"ROS_HOSTNAME={container_name}", "ROS_MASTER_URI=http://master:11311", f"ROBOT_NAME=turtlebot{self.id}"],
            # 'command': '/bin/bash -c "source /ros_ws/devel/setup.bash && roslaunch motion_ctrl base_navigation.launch & rosrun topic_tools relay /move_base_simple/goal /turtlebot1/move_base_simple/goal"'
            'command': '/bin/bash -c "source /ros_ws/devel/setup.bash && roslaunch motion_ctrl base_navigation.launch --wait"',
            'tty': True,
            'privileged': True,
            # 'networks': {
            #     'morsegatonet': {
            #         'ipv4_address': '10.2.0.6'
            #     }
            # },
            'networks': ['morsegatonet']
        }

    def build_pytrees_docker(self):
        '''
        py_trees1:
            build:
              context: ./docker
              dockerfile: Dockerfile.pytrees
            container_name: py_trees1
            runtime: runc
            depends_on:
              - motion_ctrl
            env_file:
              - .env
            devices:
              - "/dev/dri"
              - "/dev/snd"
            environment:
              - "ROS_HOSTNAME=py_trees1"
              - "ROS_MASTER_URI=http://motion_ctrl:11311"
              - "QT_X11_NO_MITSHM=1"
              - "DISPLAY=$DISPLAY"
              - "XAUTHORITY=$XAUTH"
              - "QT_GRAPHICSSYSTEM=native"
              - "PULSE_SERVER=unix:${XDG_RUNTIME_DIR}/pulse/native"
              - "ROBOT_NAME=turtlebot1"
            volumes:
              - /tmp/.docker.xauth:/tmp/.docker.xauth:rw
              - /tmp/.X11-unix:/tmp/.X11-unix:rw
              - /var/run/dbus:/var/run/dbus:ro
              - /etc/machine-id:/etc/machine-id:ro
              - ${XDG_RUNTIME_DIR}/pulse/native:${XDG_RUNTIME_DIR}/pulse/native
              - ~/.config/pulse/cookie:/root/.config/pulse/cookie
              - ./docker/py_trees_ros_behaviors:/ros_ws/src/py_trees_ros_behaviors/
            command: python3 /ros_ws/src/bridge.py
            command: /bin/bash -c "source /opt/ros/noetic/setup.bash && ros2 run ros1_bridge dynamic_bridge --bridge-all-topics "
            tty: true
            networks:
              morsegatonet:
                ipv4_address: 10.2.0.8
        '''
        package_name = 'py_trees'
        container_name = self.pytrees_pkg_name+str(self.id)
        self.pytreesd = {
            'build': {
                'context' : './docker',
                'dockerfile': 'Dockerfile.pytrees',
            },
            'container_name': container_name,
            'runtime': 'runc',
            'depends_on': ['master', f'motion_ctrl{self.id}'],
            'env_file': [env_path],
            'volumes': ['/tmp/.docker.xauth:/tmp/.docker.xauth:rw',
                '/tmp/.X11-unix:/tmp/.X11-unix:rw',
                '/var/run/dbus:/var/run/dbus:ro',
                '/etc/machine-id:/etc/machine-id:ro',
                '${XDG_RUNTIME_DIR}/pulse/native:${XDG_RUNTIME_DIR}/pulse/native',
                '~/.config/pulse/cookie:/root/.config/pulse/cookie',
                './docker/py_trees_ros_behaviors:/ros_ws/src/py_trees_ros_behaviors/'
                ],
            'environment': [f"ROS_HOSTNAME={container_name}", "ROS_MASTER_URI=http://master:11311", f"ROBOT_NAME=turtlebot{self.id}", f"SKILLS={self.skills}", f"ROBOT_CONFIG={json.dumps(self.config)}"],
            # 'command': '/bin/bash -c "source /ros_ws/devel/setup.bash && roslaunch motion_ctrl base_navigation.launch & rosrun topic_tools relay /move_base_simple/goal /turtlebot1/move_base_simple/goal"'
            'command': '/bin/bash -c "colcon build && source /ros_ws/install/setup.bash && ros2 launch py_trees_ros_behaviors tutorial_seven_docking_cancelling_failing_launch.py"',
            'tty': True,
            # 'networks': {
            #     'morsegatonet': {
            #         'ipv4_address': '10.2.0.8'
            #     }
            # },
            'networks': ['morsegatonet']
        }

class Orchestrator(object):
    """docstring for Orchestrator"""
    def __init__(self, config_file="trials.json", exp_id=0):
        super(Orchestrator, self).__init__()
        self.sim_process = None
        self.docker_compose = dict()
        self.xp_id = exp_id
        self.nrobots = 0
        self.config_file = config_file
        self.simulation_timeout_s = 45*60
        self.load_trials(self.config_file)
        self.relocate_nurse = {
            "PC Room 1": [-1, -1],
            "PC Room 2": [-1, -1],
            "PC Room 3": [-1, +1],
            "PC Room 4": [+1, +1],
            "PC Room 5": [-1, +1],
            "PC Room 6": [+1, +1],
            "PC Room 7": [-1, +1],
            "PC Room 8": [+1, +1],
            "IC Room 1": [-1, +1],
            "IC Room 2": [-1, -1],
            "IC Room 3": [-1, +1],
            "IC Room 4": [-1, -1],
            "IC Room 5": [+1, -1],
            "IC Room 6": [+1, +1],
        }
        self.endsim = ''
        self.chose_robot = ""
        self.n_timeout_wall = 0
        self.n_timeout_sim = 0
        self.n_successes = 0
        self.n_bt_failures = 0
        self.n_low_battery = 0
        self.total = 0
        self.current_date = datetime.datetime.today().strftime('%H-%M-%S-%d-%b-%Y')

    def load_trials(self, file_name):
        # file_name = "experiment_sample.json"
        curr_path = os.getcwd()+'/'
        file_path = curr_path + file_name
        self.config = None
        with open(file_path) as f:
            self.config = json.load(f)
        print(print(json.dumps(self.config[0]["robots"][0], indent=2, sort_keys=True)))
        print(self.config[0]["nurses"][0])
        print(len(self.config[0]["robots"][1]))
        self.nurses_config = self.config[0]["nurses"]
        self.robots_config = self.config[0]["robots"]

    def prepare_environment(self):
        self.endsim = False
        idx = 0
        self.nurses_config = self.config[idx]["nurses"]
        self.robots_config = self.config[idx]["robots"]
        self.create_env_file(self.config[idx]["id"], self.config[idx]["code"])
        self.create_dockers()
        self.create_robots()
        self.save_compose_file()

    def run_simulation(self):
        self.endsim = False
        idx = 0
        self.nurses_config = self.config[idx]["nurses"]
        self.robots_config = self.config[idx]["robots"]
        self.create_env_file(self.config[idx]["id"]. self.config[idx]["code"])
        self.create_dockers()
        self.create_robots()
        self.save_compose_file()
        print("STARTING SIMULATION...")
        self.start_simulation()
        start = time.time()
        runtime = time.time()
        self.clear_log_file()
        # call simulation and watch timeout
        while (runtime - start) <= self.simulation_timeout_s and self.endsim == False:
           time.sleep(1)
           runtime = time.time()
           self.check_end_simulation()
        end = time.time()
        self.close_simulation()
        print("ENDING SIMULATION...")
        print(f"Runtime of the simulation is {end - start}")
        self.save_log_file(idx, end - start)
        self.save_table_file()

    def run_some_simulations(self, sim_list):
        print("RUNNING %d TRIALS FOR THIS EXPERIMENT"%len(self.config))
        # create files
        for idx in sim_list:
            self.endsim = False
            print("RUNNING TRIALS #%d"%idx)
            self.nurses_config = self.config[idx]["nurses"]
            self.robots_config = self.config[idx]["robots"]
            self.create_env_file(self.config[idx]["id"], self.config[idx]["code"])
            self.create_dockers()
            self.create_robots()
            self.save_compose_file()
            print(f"STARTING SIMULATION #{idx}...")
            self.start_simulation()
            start = time.time()
            runtime = time.time()
            self.clear_log_file()
            # call simulation and watch timeout
            while (runtime - start) <= self.simulation_timeout_s and self.endsim == False:
                time.sleep(1)
                runtime = time.time()
                self.check_end_simulation()
                # check simulation end
            end = time.time()
            self.close_simulation()
            print(f"ENDING SIMULATION #{idx}...")
            print(f"Runtime of the simulation #{idx} is {end - start}")
            self.save_log_file(self.config[idx]["id"], self.config[idx]["code"], end - start)
            self.save_table_file()

    def run_all_simulations(self):
        print("RUNNING %d TRIALS FOR THIS EXPERIMENT"%len(self.config))
        # create files
        for i in range(0, len(self.config)):
            self.endsim = False
            print(f"RUNNING TRIALS #{i}")
            self.nurses_config = self.config[i]["nurses"]
            self.robots_config = self.config[i]["robots"]
            self.trial_id      = self.config[i]["id"]
            self.trial_code    = self.config[i]["code"]
            self.create_env_file(self.trial_id, self.config[i]["code"])
            self.create_dockers()
            self.create_robots()
            self.save_compose_file()
            print(f"STARTING SIMULATION #{i}...")
            self.start_simulation()
            start = time.time()
            runtime = time.time()
            self.clear_log_file()
            # call simulation and watch timeout
            while (runtime - start) <= self.simulation_timeout_s and self.endsim == False:
                time.sleep(1)
                runtime = time.time()
                self.check_end_simulation()
                # check simulation end
            end = time.time()
            self.close_simulation()
            print(f"ENDING SIMULATION #{i}...")
            print(f"Runtime of the simulation #{self.trial_id} is {end - start}")
            self.save_log_file(self.config[i]["id"], self.config[i]["code"], end - start)
            self.save_table_file()

    def save_table_file(self):
        with open(f'{current_path}/log/experiment-{self.current_date}.csv', 'w') as file:
            file.write('Type, Quantity\n')
            file.write(f'BT Failure, {self.n_bt_failures}\n')
            file.write(f'Timeout Wall, {self.n_timeout_wall}\n')
            file.write(f'Timeout Sim, {self.n_timeout_sim}\n')
            file.write(f'Low Battery, {self.n_low_battery}\n')
            file.write(f'Success, {self.n_successes}\n')
            file.write(f'Total, {self.total}\n')
            file.write(f'\n')

    def clear_log_file(self):
        with open(f'{current_path}/log/trial.log', 'w') as file:
            file.write('')

    def save_log_file(self, trial_id, trial_code, execution_time):
        print("Saving log file as: {}/log/{:0>2d}_{}.log".format(current_path,trial_id, trial_code))
        timeout_to_wait_for_s = 60
        start = time.time()
        runtime = time.time()
        while (runtime - start) <= timeout_to_wait_for_s:
            time.sleep(1)
            runtime = time.time()
        end = time.time()
        old_path  = f'{current_path}/log/trial.log'
        new_path = '{}/log/{:0>2d}_{}'.format(current_path,trial_id, trial_code)
        cp_cmd = 'cp log/trial.log log/{:0>2d}_{}.bkp'.format(trial_id, trial_code)
        cp_tk = shlex.split(cp_cmd)

        cp_process = subprocess.run(cp_tk,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE,
                             universal_newlines=True)
        print(cp_process.stdout)
        print(cp_process.stderr)

        # shutil.copy(old_path, new_path)
        with open(f'{new_path}.done', 'a') as logfile:
            for line in self.lines:
                logfile.write(line)
            text = '{:02.2f}, [DEBUG], trial-watcher, {}: wall-clock={}\n'.format(execution_time,self.endsim,execution_time)
            logfile.write(text)

        with open(f'{new_path}.bkp', 'a') as logfile:
            text = '{:02.2f}, [DEBUG], trial-watcher, {}: wall-clock={}\n'.format(execution_time,self.endsim,execution_time)
            logfile.write(text)
            if self.endsim == 'reach-target':
                self.n_successes = self.n_successes + 1
            elif self.endsim == 'failure-bt':
                self.n_bt_failures = self.n_bt_failures + 1
            elif self.endsim == 'low-battery':
                self.n_low_battery = self.n_low_battery + 1
            elif self.endsim == 'timeout-sim':
                self.n_timeout_sim = self.n_timeout_sim + 1
            else:
                self.n_timeout_wall = self.n_timeout_wall + 1
            self.total = self.total + 1
        self.clear_log_file()
        # self.save_bag_file(trial_id)

    def save_bag_file(self, run):
        current_date = datetime.datetime.today().strftime('%H-%M-%S-%d-%b-%Y')
        os.rename(f'{current_path}/log/bag.bag', f'{current_path}/log/exp{self.xp_id}_trial{run}_{current_date}.bag')

    def check_end_simulation(self):
        with open(f'{current_path}/log/trial.log', 'r') as file:
            # print("Checking simulation...")
            self.lines = file.readlines()
            # print(lines)
            alllines = ''
            for line in self.lines:
                alllines = alllines+line
                if "ENDSIM" in line:
                    self.endsim = 'reach-target'
                if "FAILURE" in line:
                    self.endsim = 'failure-bt'
                if "ENDLOWBATT" in line:
                    self.endsim = 'low-battery'
                if "ENDTIMEOUTSIM" in line:
                    self.endsim = 'timeout-sim'

    def get_nurse_new_pos(self, nurse_idx):
        nurse_pos = self.nurses_config[0]["position"]
        nurse_loc = self.nurses_config[0]["location"]
        x = 0
        y = 1
        new_nurse_pos = []
        new_nurse_pos.append(nurse_pos[x] + self.relocate_nurse[nurse_loc][x])
        new_nurse_pos.append(nurse_pos[y] + self.relocate_nurse[nurse_loc][y])

        print(f"Relocating nurse from {nurse_pos} to {new_nurse_pos}")
        nurse_pos[x] = new_nurse_pos[x]
        nurse_pos[y] = new_nurse_pos[y]
        return nurse_pos

    def create_env_file(self, n_trial, trial_code):
        self.env_name = "sim.env"
        curr_path = os.getcwd()+'/'
        file_path = curr_path + self.env_name
        
        self.chose_robot = ""
        for r_config in self.robots_config:
            r_id = r_config["id"]
            if r_config["local_plan"] != None:  self.chose_robot = "turtlebot"+str(r_id)
        
        with open(file_path, "w") as ef:
            nurse_pos = self.get_nurse_new_pos(0)
            print(str(nurse_pos))
            nurse_str = str(nurse_pos).replace(',',';')
            ef.write(f"TRIAL={n_trial}\n\n")
            ef.write(f"TRIAL_CODE={trial_code}\n\n")
            ef.write(f"NURSE_POSE={nurse_str}\n\n")
            ef.write(f"CHOSE_ROBOT={self.chose_robot}\n\n")
            ef.write(f'N_ROBOTS={len(self.robots_config)}\n\n')
            for robot in self.robots_config:
                # name
                id_str = (robot["id"])
                ef.write(f'ROBOT_NAME_{id_str}=turtlebot{id_str}\n')
                # pose
                yaw = random.uniform(-math.pi, math.pi)
                pose_str = str(robot["position"]).replace(',',';')
                pose_env = (f"ROBOT_POSE_{id_str}={pose_str}")
                ef.write(pose_env+'\n')
                # batt level
                batt_level_str = robot["battery_charge"]*100
                batt_level_env = "BATT_INIT_STATE_{}={:02.2f}".format(id_str,batt_level_str)
                ef.write(batt_level_env+'\n')
                batt_slope_str = robot["battery_discharge_rate"]*100
                batt_slope_env = "BATT_SLOPE_STATE_{}={:02.2f}".format(id_str, batt_slope_str)
                ef.write(batt_slope_env+'\n')
                ef.write('\n')

    def create_robots(self):
        robots_servs = []
        # build robots
        for r_config in self.robots_config:
            r_id = r_config["id"]
            r_loc = r_config["location"]
            robot = Robot(r_id, r_loc, r_config["battery_charge"], r_config["skills"], r_config)
            r_motion_name, r_motion_serv = robot.get_motion_docker()
            r_pytrees_name, r_pytrees_serv = robot.get_pytrees_docker()
            robot_info = {
                'id': r_id,
                'robot': robot,
                'motion_name': r_motion_name,
                'motion_serv': r_motion_serv,
                'pytrees_name': r_pytrees_name,
                'pytrees_serv': r_pytrees_serv,
            }
            robots_servs.append(robot_info)
            print(f'Robot {robot} has the following plan => {r_config["local_plan"]}')
        for i in range(0, len(self.robots_config)):
            self.services[robots_servs[i]["motion_name"]] = robots_servs[i]["motion_serv"]
            self.services[robots_servs[i]["pytrees_name"]] = robots_servs[i]["pytrees_serv"]
        # print(self.services)

    def create_dockers(self):
        display_idx = random.choice([1,2,3])
        morse_cmd = '/bin/bash -c "source /ros_ws/devel/setup.bash && Xvfb -screen 0 100x100x24 :%d & DISPLAY=:%d morse run morse_hospital_sim"'
        self.morse = {
            'build': {
                'context' : './docker',
                'dockerfile': 'Dockerfile.app',
            },
            'runtime': 'runc',
            'container_name': 'morse',
            'depends_on': ['master'],
            # 'devices': ["/dev/dri", "/dev/snd"],
            'env_file': [env_path],
            'environment': ["ROS_HOSTNAME=morse", "ROS_MASTER_URI=http://master:11311", "QT_X11_NO_MITSHM=1"],
            'volumes': ['/tmp/.X11-unix:/tmp/.X11-unix:rw', '~/.config/pulse/cookie:/root/.config/pulse/cookie', './docker/hmrs_hostpital_simulation/morse_hospital_sim:/ros_ws/morse_hospital_sim'],
            'expose': ["8081", "3000", "3001"],
            # 'command': 'roslaunch rosbridge_server rosbridge_websocket.launch',
            # 'command': 'rosrun tf2_web_republisher tf2_web_republisher',
            'command': (morse_cmd%(display_idx,display_idx)),
            'tty': True,
            'networks': ['morsegatonet']
        }
        self.master = {
            'build': {
                'context' : './docker',
                'dockerfile': 'Dockerfile.motion',
            },
            'container_name': 'master',
            'env_file': [env_path],
            'environment': ["ROBOTS_CONFIG="+json.dumps(self.robots_config), "NURSES_CONFIG="+json.dumps(self.nurses_config)],
            'volumes': ['./log/:/root/.ros/logger_sim/', './docker/motion_ctrl:/ros_ws/src/motion_ctrl/'],
            'command': '/bin/bash -c "source /ros_ws/devel/setup.bash && roslaunch src/motion_ctrl/launch/log.launch"',
            'tty': True,
            'networks': {
                'morsegatonet': {
                    'ipv4_address': '10.2.0.5'
                }
            },
        }
        self.ros1_bridge = {
            'build': {
                'context' : './docker',
                'dockerfile': 'Dockerfile.pytrees',
            },
            'container_name': 'ros1_bridge',
            'runtime': 'runc',
            'depends_on': ['master'],
            'env_file': [env_path],
            'volumes': ['/tmp/.docker.xauth:/tmp/.docker.xauth:rw', '/tmp/.X11-unix:/tmp/.X11-unix:rw', '/var/run/dbus:/var/run/dbus:ro'],
            'environment': ["ROS_HOSTNAME=ros1_bridge", "ROS_MASTER_URI=http://master:11311"],
            'command': '/bin/bash -c "source /opt/ros/noetic/setup.bash && ros2 run ros1_bridge dynamic_bridge --bridge-all-topics "',
            'tty': True,
            # 'networks': {
            #     'morsegatonet': {
            #         'ipv4_address': '10.2.0.8'
            #     }
            # },
            'networks': ['morsegatonet']
        }
        self.networks = {
            'morsegatonet': {
                'driver': 'bridge',
                'ipam': {
                    'driver': 'default',
                    'config': [{'subnet': '10.2.0.0/16'}],
                }
            }
        }
        self.services = {
            'morse': self.morse,
            'master': self.master,
            'ros1_bridge': self.ros1_bridge,
        }
        self.docker_compose = {
            'version': "2.3",
            'services': self.services,
            'networks': self.networks,
        }

    def get_compose_file(self):
        return self.docker_compose

    def start_simulation(self):
        up_docker_str = 'docker-compose -f experiment_trials.yaml up -d'
        # up_docker_str = 'docker-compose up -d'
        print('Run Simulation')
        up_docker_tk = shlex.split(up_docker_str)
        # print(up_docker_tk)

        self.sim_process = subprocess.run(up_docker_tk,
                                     stdout=subprocess.PIPE,
                                     stderr=subprocess.PIPE,
                                     universal_newlines=True)
        print(self.sim_process.stdout)
        print(self.sim_process.stderr)

    def close_simulation(self):
        # stop_docker_str = 'docker-compose down'
        start = time.time()
        runtime = time.time()
        self.clear_log_file()
        timeout_to_wait_for_s = 30
        while (runtime - start) <= timeout_to_wait_for_s:
            time.sleep(1)
            runtime = time.time()
        end = time.time()
        stop_docker_str = 'docker-compose -f experiment_trials.yaml down'
        stop_docker_tk = shlex.split(stop_docker_str)

        print('Closing Simulation')
        self.sim_process = subprocess.run(stop_docker_tk,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE,
                             universal_newlines=True)
        print(self.sim_process.stdout)
        print(self.sim_process.stderr)

    def save_compose_file(self):
        self.compose_name = 'experiment_trials.yaml'
        with open(f'{current_path}/{self.compose_name}', 'w') as file:
            documents = yaml.dump(self.get_compose_file(), file)

def choose_poses(n_robots):
    poses = []
    for n in range(0, n_robots):
        pose = []
        pose = random.choice(rooms)
        print(pose)
        pose.append(random.uniform(-math.pi, math.pi)) # choose initial orientation
        if len(pose) > 3:
            raise Exception('len(pose)==', len(pose))
        poses.append(pose)
        print(poses)
        # TODO: check if the choosed pose is already taken
    return poses

env_path = None

if __name__ == '__main__':
    current_path = os.getcwd()
    print(f'current running path = {current_path}')
    env_path = current_path+'/sim.env'
    print(f'env file will be written in = {env_path}')

    trials_runner = Orchestrator("trials.json", 9)
    trials_runner.prepare_environment()
    # trials_runner.run_simulation()
    # trials_runner.run_some_simulations([9, 17, 34, 63, 73, 75])
    trials_runner.run_all_simulations()
