# Forest Recorder

Record a forest of trees.

## What is this?

[forestrecorder] is a standalone, dependency-free Python 3.5+ script
that allows you to record a sequence of changes to a `forest` of
`trees`.

A `tree` is a lineage of related universally unique `nodes` connected
by some child-to-parent relationship. A `forest` is an unordered
collection of `trees`.

## Why?

When someone asks "What is your favorite movie?", the answer is often
filled with caveats:

- "Are you asking about enjoyment or critical merit?"
- "Do you only include films, or do television series and other video
  streams count?"
- "In what genre?"
- "Does it matter when the movie was shot?"
- "Does it have to be in English?"
- "Are you asking because you want to watch it?"

The notion of a "favorite" requires us to consider the essence of what
it means to prefer one thing over another, and moreover, to consider
what is an eligible thing in the first place.

Instead of comparing a documentary to an animated film for children,
it might make sense that they inhabit different trees in the same
forest, with each node in a tree ordered by preference.

Considering movie preferences as a forest of trees yields answers to
some valuable questions:

- "What is the movie most similar to this one that is better than it?"
- "What movies are dissimilar to anything I've seen?"

It would be incredible to be able to compare forests with strangers
and use them to find new and interesting content.

See [videoforest] for an example using the project.

## Version

This is currently a pre-release project.

## Installation

There are no supported installation methods at this
time. [forestrecorder] is a standalone script.

## Usage

Record a forest of trees:

````
usage: forestrecorder [-h] command [argument [argument ...]]

Record a forest of trees.

optional_arguments:
  -h, --help            print this help message

command:
    configure           create a forest configuration
    add                 add a node to the forest
    move                move a node in the forest
    remove              remove a node from the forest
    history             print a tab-delimited history of forest actions
    dump                print a JSON representation of the current forest
    version             print the current version number and exit

````

Create a forest configuration:

````
usage: forestrecorder configure [-h] [-f] [-c CONFIGURATION_PATH]
                                [--non-interactive]
                                [--forest-name FOREST_NAME]
                                [--tree-name TREE_NAME]
                                [--node-name NODE_NAME]
                                [--child-to-parent-name CHILD_TO_PARENT_NAME]
                                [--actions-path ACTIONS_PATH]

Create a forest configuration.

optional arguments:
  -h, --help            show this help message and exit
  -f, --force           overwrite existing configuration file
  -c CONFIGURATION_PATH, --configuration-path CONFIGURATION_PATH
                        the configuration path. (default: .forestrecorder)
  --non-interactive     do not prompt the user to input missing arguments

interactive or required arguments:
  --forest-name FOREST_NAME
                        the name of the forest
  --tree-name TREE_NAME
                        the name of the trees
  --node-name NODE_NAME
                        the name of the nodes
  --child-to-parent-name CHILD_TO_PARENT_NAME
                        the name of the child-to-parent relationship
  --actions-path ACTIONS_PATH
                        the path to the actions

exit statuses:
  0 - success
  1 - unknown error
  2 - command line invocation error
  3 - keyboard_interrupt
  4 - unable to capture interactive input
  5 - cannot overwrite existing configuration
  6 - unable to write configuration file

````

Add a node to the forest:

````
usage: forestrecorder add [-h] [--parent PARENT] [--child CHILD]
                          [-c CONFIGURATION_PATH] [--non-interactive]
                          [--node NODE]

Add a node to the forest.

optional arguments:
  -h, --help            show this help message and exit
  --parent PARENT       the parent of the node
  --child CHILD         a child of the parent to be moved to node (may be
                        specified multiple times)
  -c CONFIGURATION_PATH, --configuration-path CONFIGURATION_PATH
                        the configuration path. (default: .forestrecorder)
  --non-interactive     do not prompt the user to input missing arguments

interactive or required arguments:
  --node NODE           the node to add to the forest

exit statuses:
  0 - success
  1 - unknown error
  2 - command line invocation error
  3 - keyboard_interrupt
  4 - unable to capture interactive input
  7 - unable to read configuration file
  8 - unable to parse configuration
  9 - invalid configuration value
  10 - missing required configuration value
  11 - unable to append to actions file
  12 - unable to read actions file
  13 - invalid command in actions file
  14 - attempted to add node already present in forest
  15 - parent of node not present in forest
  16 - child not direct descendant of parent

````

Move a node in the forest:

````
usage: forestrecorder move [-h] [--parent PARENT] [--child CHILD]
                           [-c CONFIGURATION_PATH] [--non-interactive]
                           [--node NODE]

Move a node in the forest.

optional arguments:
  -h, --help            show this help message and exit
  --parent PARENT       the new parent of the node
  --child CHILD         a child of the parent to be moved to node (may be
                        specified multiple times)
  -c CONFIGURATION_PATH, --configuration-path CONFIGURATION_PATH
                        the configuration path. (default: .forestrecorder)
  --non-interactive     do not prompt the user to input missing arguments

interactive or required arguments:
  --node NODE           the node to move in the forest

exit statuses:
  0 - success
  1 - unknown error
  2 - command line invocation error
  3 - keyboard_interrupt
  4 - unable to capture interactive input
  7 - unable to read configuration file
  8 - unable to parse configuration
  9 - invalid configuration value
  10 - missing required configuration value
  11 - unable to append to actions file
  12 - unable to read actions file
  13 - invalid command in actions file
  15 - parent of node not present in forest
  16 - child not direct descendant of parent
  17 - attempted to move node not present in forest

````

Remove a node from the forest:

````
usage: forestrecorder remove [-h] [-r] [-c CONFIGURATION_PATH]
                             [--non-interactive] [--node NODE]

Remove a node from the forest.

optional arguments:
  -h, --help            show this help message and exit
  -r, --recursive       remove all descendents of node recursively
  -c CONFIGURATION_PATH, --configuration-path CONFIGURATION_PATH
                        the configuration path. (default: .forestrecorder)
  --non-interactive     do not prompt the user to input missing arguments

interactive or required arguments:
  --node NODE           the node to remove from the forest

exit statuses:
  0 - success
  1 - unknown error
  2 - command line invocation error
  3 - keyboard_interrupt
  4 - unable to capture interactive input
  7 - unable to read configuration file
  8 - unable to parse configuration
  9 - invalid configuration value
  10 - missing required configuration value
  11 - unable to append to actions file
  12 - unable to read actions file
  13 - invalid command in actions file
  18 - attempted to remove node not present in forest

````

Print a tab-delimited history of forest actions:

````
usage: forestrecorder history [-h] [-c CONFIGURATION_PATH]

Print a tab-delimited history of forest actions.

optional arguments:
  -h, --help            show this help message and exit
  -c CONFIGURATION_PATH, --configuration-path CONFIGURATION_PATH
                        the configuration path. (default: .forestrecorder)

exit statuses:
  0 - success
  1 - unknown error
  2 - command line invocation error
  3 - keyboard_interrupt
  19 - unable to write history to file

````

Print a json representation of the current forest:

````
usage: forestrecorder dump [-h] [-c CONFIGURATION_PATH]

Print a json representation of the current forest.

optional arguments:
  -h, --help            show this help message and exit
  -c CONFIGURATION_PATH, --configuration-path CONFIGURATION_PATH
                        the configuration path. (default: .forestrecorder)

exit statuses:
  0 - success
  1 - unknown error
  2 - command line invocation error
  3 - keyboard_interrupt
  20 - unable to write JSON representation to file

````

Print the current version number and exit:

````
usage: forestrecorder version [-h]

Print the current version number and exit.

optional arguments:
  -h, --help  show this help message and exit

exit statuses:
  0 - success
  1 - unknown error
  2 - command line invocation error
  3 - keyboard_interrupt
  21 - unable to write version to file

````

## Exit Statuses

The program exits with one of the following exit statuses.

* `0` - Success
* `1` - Unknown error
* `2` - Command line invocation error
* `3` - Keyboard interrupt
* `4` - Unable to capture interactive input
* `5` - Cannot overwrite existing configuration
* `6` - Unable to write configuration file
* `7` - Unable to read configuration file
* `8` - Unable to parse configuration
* `9` - Invalid configuration value
* `10` - Missing required configuration value
* `11` - Unable to append to actions file
* `12` - Unable to read actions file
* `13` - Invalid command in actions file
* `14` - Attempted to add node already present in forest
* `15` - Parent of node not present in forest
* `16` - Child not direct descendant of parent
* `17` - Attempted to move node not present in forest
* `18` - Attempted to remove node not present in forest
* `19` - Unable to write history to file
* `20` - Unable to write JSON representation to file
* `21` - Unable to write version to file

## Contributing

Pull requests are welcome. A test suite would be appreciated.

## Support

Please post any comments, concerns, or issues to the Github issues
page.

## Changelog

There will be no changelog until a release is finalized.

## License

Distributed under the MIT License, which can be found at [LICENSE] in
the root of this distribution.

[forestrecorder]: https://github.com/dendrologist/forestrecorder/blob/master/forestrecorder
[videoforest]: https://github.com/dendrologist/videoforest
[LICENSE]: https://github.com/dendrologist/forestrecorder/blob/master/LICENSE
