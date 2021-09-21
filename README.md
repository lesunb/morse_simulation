# Morse Simulation

## Overview

<!-- morse_simulation is a simulation environment used to run multi-robot experiments using docker+ROS+Morse. -->
morse_simulation is a simulation environmet based on docker and docker-compose used to run multi-robot experiments [ROS]+[Morse] in the Software Engineering Lab (LES) at University of Brasilia.

**Keywords:** simulation, multi-robot, mobile robots, simulation environment, morse, ROS

### License

The source code is released under a [MIT license](LICENSE).

**Authors: Gabriel F P Araujo, Gabriel Rodrigues and Vicente Moraes<br />
Affiliation: [LES](http://les.unb.br//)<br />
Maintainers: [Gabriel F P Araujo](mailto:gabriel.fp.araujo@gmail.com), [Gabriel Rodrigues](mailto:gabrielsr@gmail.com), [Vicente Moraes](mailto:vicenteromeiromoraes@gmail.com) and [Ricardo Caldas](mailto:rdinizcal@gmail.com)**

morse_simulation has been tested under Ubuntu 20.04, Docker 20.10.7 and docker-compose 1.29.2. This is research code, expect that it changes often and any fitness for a particular purpose is disclaimed.

![Execution Pipeline](docs/pipeline_execution2.png)

<!-- ### Publications

If you use this work in an academic context, please cite the following publication(s):

* P. Fankhauser, M. Bloesch, C. Gehring, M. Hutter, and R. Siegwart: **PAPER TITLE**. IEEE/RSJ International Conference on Intelligent Robots and Systems (IROS), 2015. ([PDF](http://dx.doi.org/10.3929/ethz-a-010173654))

        @inproceedings{Fankhauser2015,
            author = {Fankhauser, P\'{e}ter and Hutter, Marco},
            booktitle = {IEEE/RSJ International Conference on Intelligent Robots and Systems (IROS)},
            title = {{PAPER TITLE}},
            publisher = {IEEE},
            year = {2015}
        }
 -->

## Build

### Dependencies

- [Docker](https://docs.docker.com/get-docker/),
- [docker-compose](https://docs.docker.com/compose/install/)


Clone this repository to your workspace and build the images.

```bash
git clone https://github.com/lesunb/morse_simulation
git submodule update --init --recursive
docker-compose build
```

## Usage

Run the main node with
```bash
python3 run_simulation.py
```

## Config files

* **trials.json** Defines a list of scenarios to be tested
* **docker-compose.yaml** docker-compose yaml configuration file used to start a simulation
* **sim.env** configures the environment variables shared between all conteiners

<!-- ## Disclaimer

This code is used in research, have a good time! -->

<!-- # Package Name

## Overview

This is a template: replace, remove, and add where required. Describe here what this package does and what it's meant for in a few sentences.

**Keywords:** example, package, template

### License

The source code is released under a [BSD 3-Clause license](ros_package_template/LICENSE).

**Author: Péter Fankhauser<br />
Affiliation: [ANYbotics](https://www.anybotics.com/)<br />
Maintainer: Péter Fankhauser, pfankhauser@anybotics.com**

The PACKAGE NAME package has been tested under [ROS] Indigo and Ubuntu 14.04. This is research code, expect that it changes often and any fitness for a particular purpose is disclaimed.

[![Build Status](http://rsl-ci.ethz.ch/buildStatus/icon?job=ros_best_practices)](http://rsl-ci.ethz.ch/job/ros_best_practices/)


![Example image](doc/example.jpg)


### Publications

If you use this work in an academic context, please cite the following publication(s):

* P. Fankhauser, M. Bloesch, C. Gehring, M. Hutter, and R. Siegwart: **PAPER TITLE**. IEEE/RSJ International Conference on Intelligent Robots and Systems (IROS), 2015. ([PDF](http://dx.doi.org/10.3929/ethz-a-010173654))

        @inproceedings{Fankhauser2015,
            author = {Fankhauser, P\'{e}ter and Hutter, Marco},
            booktitle = {IEEE/RSJ International Conference on Intelligent Robots and Systems (IROS)},
            title = {{PAPER TITLE}},
            publisher = {IEEE},
            year = {2015}
        }


## Installation

### Installation from Packages

To install all packages from the this repository as Debian packages use

    sudo apt-get install ros-indigo-...

### Building from Source

#### Dependencies

- [Robot Operating System (ROS)](http://wiki.ros.org) (middleware for robotics),
- [Eigen] (linear algebra library)

    sudo apt-get install libeigen3-dev


#### Building

To build from source, clone the latest version from this repository into your catkin workspace and compile the package using

  cd catkin_workspace/src
  git clone https://github.com/ethz-asl/ros_package_template.git
  cd ../
  catkin_make


### Unit Tests

Run the unit tests with

  catkin_make run_tests_ros_package_template


## Usage

Describe the quickest way to run this software, for example:

Run the main node with

  roslaunch ros_package_template ros_package_template.launch

## Config files

Config file folder/set 1

* **config_file_1.yaml** Shortly explain the content of this config file

Config file folder/set 2

* **...**

## Launch files

* **launch_file_1.launch:** shortly explain what is launched (e.g standard simulation, simulation with gdb,...)

     Argument set 1

     - **`argument_1`** Short description (e.g. as commented in launch file). Default: `default_value`.

    Argument set 2

    - **`...`**

* **...**

## Nodes

### ros_package_template

Reads temperature measurements and computed the average.


#### Subscribed Topics

* **`/temperature`** ([sensor_msgs/Temperature])

  The temperature measurements from which the average is computed.


#### Published Topics

...


#### Services

* **`get_average`** ([std_srvs/Trigger])

  Returns information about the current average. For example, you can trigger the computation from the console with

    rosservice call /ros_package_template/get_average


#### Parameters

* **`subscriber_topic`** (string, default: "/temperature")

  The name of the input topic.

* **`cache_size`** (int, default: 200, min: 0, max: 1000)

  The size of the cache.


### NODE_B_NAME

...


## Bugs & Feature Requests

Please report bugs and request features using the [Issue Tracker](https://github.com/ethz-asl/ros_best_practices/issues).


[ROS]: http://www.ros.org
[rviz]: http://wiki.ros.org/rviz
[Eigen]: http://eigen.tuxfamily.org
[std_srvs/Trigger]: http://docs.ros.org/api/std_srvs/html/srv/Trigger.html
[sensor_msgs/Temperature]: http://docs.ros.org/api/sensor_msgs/html/msg/Temperature.html
 -->
[ROS]: http://www.ros.org
[Morse]: https://www.openrobots.org/morse/doc/stable/morse.html
