# Particle Tracks Dev Ops

This document describes how to install
and update Particle Tracks on an Ubuntu Linux server.

- [Accounts](#accounts)
- [Application Directory Structure](#application-directory-structure)
- [Install Particle Tracks](#install-particle-tracks)
- [System Service Manager](#system-service-manager)
- [Update Particle Tracks](#update-particle-tracks)

# Accounts

There are three relevant user accounts on the server.
1. The particle tracks account,
   under which the application runs.
   For security,
   this account has limited permissions
   and does not permit direct login.
1. An administrator account,
   which is user account that has `sudo` permission.
   Log in as this user to perform devops work.
1. The super user (`root`) account on the server.
   Some operations require `root` permission.
   To avoid an accidental misconfiguration
   of the server, use this account 
   sparingly with the `sudo` command.

## Particle Tracks Account

It's best to limit the application's access to server resources,
so run it under a limited user account.
Here, we use an account called `particle-tracks`,
which has shell access but is _not_ a privileged user.

Do not allow login access to the server account.
A simple way to create an account that does not allow direct login is:
```
sudo adduser --disabled-password particle-tracks
```
To ensure this command worked as expected,
verify that the password field
in the `/etc/shadow` file is not a valid password.
For example, the relevant line for `particle-tracks`
might look something like this:
```
particle-tracks:*:17514:0:99999:7:::
```
The `*` indicates that this user cannot log in normally.

## Administrator Account

Administrator accounts are normal login accounts
that have been granted `sudo` permission.
One way to grant `sudo` permission 
is to add the user account
to the `wheel` group.
For example, to add account `myaccount` to the `wheel` group, run: 
```
sudo adduser myaccount wheel
```
Check which groups you are part of with the `id` command.

**Important**:
Do _not_ grant `sudo` permission to the Particle Tracks account,
which would create a major security vulnerability.

## Super User Access

**Important**: 
The term "super user"
often refers to the `root` user on Unix/Linux.
Because `root` has unlimited permissions
on a server,
it's seldom a good idea to log in directly as `root`
lest you clobber something important by accident.
Instead, use commands like `sudo`, which grant a temporary increase
in privileges to an ordinary user who has been granted 
`sudo` access.

By default, `sudo` runs commands as the `root` user.
For example:
```
sudo ls
```
lists the current directly 
while running as `root`.
However, `sudo` _also_ allows you to run commands as _any_ user
by supplying the `-u` option.
```
sudu -u particle-tracks ls
```
lists the current directory 
while running as the `particle-tracks` user.

The general principle is to run all commands 
with the _least privilege necessary_.
For example, the `particle-tracks` account doesn't allow normal shell login,
it still owns all the application files.
We can maintain this ownership by running all relevant commands
as the `particle-tracks` user.
It's not necessary to run such commands as the `root` user
(in fact, it would probably break things).

There are two ways to run commands as the `particle-tracks` user 
using the `sudo` command.
In both cases, you must be logged in to the server
as an administrator (i.e., with `sudo` access).

### Single Sudo Command

In many cases,
you will want to run just one command as the `particle-tracks` user
and then return to your normal login account. Use:
```
sudo -u particle-tracks <command>
```
By default `sudo` executes your command as the `root` user;
the `-u` flag specifies a different user,
under whose privileges `<command>` is run.
Authenticate using the password for your normal login account.

For some commands
(e.g., `nginx` configuration),
you do want to run as `root`.
In this case, use simply:
```
sudo <command>
```

### Sudo Shell

If you are going to be running _multiple_ commands 
as the `particle-tracks` user,
it can be simpler to start a login shell running as that user:
```
sudo -u particle-tracks -i
```
Authenticate using the password for your normal login account.
The `-i` flag asks for a login shell
running under the given user.
As for a single command,
the `-u` flag specifies a specific user.
Because of the destructive potential of a login shell running as `root`,
it's important to include the `-u` flag.

Notes:
* There is no `<command>` given here;
  you are logging in so that you can issue multiple commands 
  as the `particle-tracks` user.
* When you're done running commands as the `particle-tracks` user,
  exit the `particle-tracks` shell and 
  return to your regular account; 
  issue the `exit` command or hit `CTRL-D`.

# Application Directory Structure

We'll refer to the Particle Tracks home directory
as `$PT_HOME`.
Unless there's some reason to install Particle Tracks elsewhere,
this will typically be `/home/particle-tracks`.
These are the top-level directories within `$PT_HOME`:

   - `logs` - application log files
   - `server` - Particle Tracks server 
     (from the `particle-tracks-server` repository)
   - `ui` - Particle Tracks UI
     (from the `particle-tracks-ui` repository)
   - `venv` - Python virtual environment for server

# Install Particle Tracks

This section covers installing Particle Tracks
for the first time on a server.

## Install Linux Packages

Particle tracks relies on several Linux packages.
Install these using the package manager
running as `root`.

### Node

The Particle Tracks UI relies on [Node](https://nodejs.org/en/).
```
sudo apt install nodejs
```

### Nginx

[Nginx](https://www.nginx.com/) serves static files
and proxies application requests to the Particle Tracks server.
```
sudo apt install nginx
```

### Supervisor

[Supervisor](http://supervisord.org/) manages the Particle Tracks
server process.
```
sudo apt install supervisor
```

## Clone Repositories

Clone the two Particle Tracks repositories
into the `particle-tracks` user's home directory
(`$PT_HOME`).
You should find yourself in the home directory
of the `particle-tracks` account (e.g., `/home/particle-tracks`).

1. Because you'll issue several commands as `particle-tracks`,
   it will be easiest to `sudo` to a shell as `particle-tracks`.
   ```
   sudo -u particle-tracks-i
   ```
1. Change to the Particle Tracks home directory
   ```
   cd $PT_HOME
   ```
1. Clone the client:
   ```
   git clone https://github.com/knkiers/particle-tracks-ui.git ui
   ```
1. Clone the server:
   ```
   git clone https://github.com/knkiers/particle-tracks-server.git server
   ```
   Note that both `git` commands specify a (simpler, shorter)
   local directory.

## Create Virtual Environment

The server runs under a Python virtual environment.
1. Use a `particle-tracks` shell.
1. In the `$PT_HOME` directory, run:
   ```
   python3 -m venv venv
   ```
   This command uses the Python virtual environment module
   (specified by `-m venv`)
   and creates a virtual environment
   in the directory `venv`.

## Activate Virtual Environment

1. Use a `particle-tracks` shell.
1. In the `$PT_HOME` directory,
   activate the virtual environment in your shell:
   ```
   source ./venv/bin/activate
   ```
1. To check that your virtual environment is activated,
   check which `pip` command will be executed:
   ```
   which pip
   ```
   The response should indicate the `pip` program
   in `$PT_HOME/venv/bin/pip`
   
Note that you must repeat the activation command
whenever you start a new shell
that needs to use the virtual environment.

You can also disable the virtual environment with this command:
```
deactivate
```

## Install Python Modules

Next, install all required Python modules
in the virtual environment.

1. Make sure you have activated the virtual environment
   in your current shell.
1. From the `particle-tracks` home directory (`$PT_HOME`), run:
   ```
   sudo -u particle-tracks pip install -r server/requirements.txt
   ```

## Collect Static Files

1. Make sure the virtual environment is activate in your shell.
1. Populate the Particle Tracks server `static` directory
   with required files:
   ```
   cd $PT_HOME/server
   sudo -u particle-tracks ./manage.py collectstatic
   ``` 

## Build the UI

1. Change to the proper directory
    ```
    cd $PT_HOME/ui
    ```
1. Build the user interface bundles:
    ```
    sudo -u particle-tracks npm build
    ```

## Set up the Database

Particle Tracks current uses [SQLite](https://www.sqlite.org/index.html).
To install an existing database file:
```
sudo -u particle-tracks cp <file> $PT_HOME/server/particle-tracks.db
```

## Configure Particle Tracks Server

The Particle Tracks server requires
private configuration information.
Install the configuration file:
```
sudo -u particle-tracks cp <file> $PT_HOME/server/particle_tracks_server/secret.py
```

## Configure Nginx

Configure `nginx` to serve static files
and proxy requests to the Particle tracks server.
Because `nginx` is owned by the `root` user,
run this command as `root`.
```
sudo cp $PT_HOME/server/etc/config/particle-tracks-nginx.conf /etc/nginx/sites-available
sudo ln -s /etc/nginx/sites-available/particle-tracks-nginx.conf /etc/sites-enabled 
```
Note that the configuration file may need to be
updated to accommodate the local configuration.
Refer to [these instructions](#system-service-manager)
for information on starting/reloading `nginx`.

## Configure Supervisor

Configure the Supervisor daemon to manage the Particle Tracks server process.
```
sudo cp $PT_HOME/server/etc/config/particle-tracks-supervisor.conf /etc/supervisor/conf.d
```
Note that the configuration file may need to be
updated to accommodate the local configuration.
Refer to [these instructions](#system-service-manager)
for information on starting/reloading `supervisor`.

After adding a new configuration file,
instruct Supervisor to load that file
and begin managing the process:
```
sudo supervisorctl update
```
To check on the status of the managed process use:
```
sudo supervisorctl status
```
The status for the Particle Tracks server
should be `RUNNING`.

Note that you can also run Supervisor commands
from an interactive shell:
```
sudo supervisorctl
```

## Test the Installation

Point a web browser at the Particle Tracks URL
and load the application!

# System Service Manager

The system service manager (`systemd`)
manages both `nginx` and `supervisor`.

To check the status of a service
```
sudo systemctl status <service-name>
```
where `<service-name>` should be replaced
with `nginx` or `supervisor`.

To start a service that isn't running:
```
sudo systemctl start <service-name>
```

To restart a service (e.g., after updating its configuration file):
```
sudo systemctl restart <service-name>
```

# Update Particle Tracks

Following are instructions to update 
an existing Particle Tracks installation.
All instructions assume you are logged in
with an [administrative account](#administrator-account).

Rather than repeating a lot of `sudo` commands,
you may find it more convenient to run
a [`sudo` shell](#sudo-shell)
for those commands that require it.

Note that the `particle-tracks` account
should _not_ have `sudo` access.
Any `sudo` command must be executed
from your [administrator account](#administrator-account).
For example, if you use a `particle-tracks` shell,
you will have to exit that shell back to your
administrator account shell
in order to restart the server process
as `root`.

## User Interface

1. Change directory
   ```
   cd $PT_HOME/ui
   ```
1. Update from GitHub
   ```
   sudo -u particle-tracks git pull
   ```
1. Rebuild
   ```
   sudo -u particle-tracks npm build
   ```
   
## Server

1. Change directory
   ```
   cd $PT_HOME/server
   ```
1. Update from GitHub
   ```
   sudo -u particle-tracks git pull
   ```
1. Rebuild static files (if they have changed)
   ```
   sudo -u particle-tracks ./manage.py collectstatic
   ```
1. Restart server in Supervisor
   (must be done as `root` user)
   ```
   sudo supervisorctl restart particle-tracks-server
   ```
