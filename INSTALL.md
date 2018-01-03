# Installation

This document describes how to install Particle Tracks on a Fedora/CentOS server.

# Server User Account

It's best to limit the server's access,
so run it under a limited user account.
Here, we use an account called `particle-tracks`,
which has shell access but is _not_ a privileged user.

Do not allow login access to the server account.
Verify that the password field
in the `/etc/shadow` file is not a valid
password (per the output of `crypt(3)`).
For example, the relevant line for `particle-tracks`
might look something like this:
```
particle-tracks:!!:17514:0:99999:7:::
```
The `!!` indicates that this user cannot log in normally.

# Sudo

Although the `particle-tracks` account doesn't allow normal shell login,
it still owns all the application files.
There are two ways to run commands as the `particle-tracks` user 
using the `sudo` command.
In both cases, you must be logged in to the server
as a user who has `sudo` privileges.
One way to grant such privileges is to add the user account
to the `wheel` group.
Check which groups you are part of with the `id` command.

## Single Command

In many cases,
you will want to run just one command as the `particle-tracks` user
and then return to your normal login account. Use:
```
sudo -u particle-tracks <command>
```
By default `sudo` executes your command as the `root` user;
the `-u` flag specifies a different user,
under whose privileges the `<command>` is run.
Authenticate using the password for your normal login account.

For some commands
(e.g., `nginx` configuration),
you do want to run as `root`.
In this case, use simply:
```
sudo <command>
```

## Shell

If you are going to be running mulitple commands as the `particle-tracks` user,
it can be simpler to start a login shell running at that user. Use:
```
sudo -u particle-tracks -i
```
The `-i` flag asks for a login shell
running under the given user.
As for a single command,
the `-u` flag specifies a specific user.
Because the destuctive potential of a login shell running as `root`,
it's important to include the `-u` flag.
Note that there is no `<command>`
given here;
you are logging in so that you can issue multiple commands as the `particle-tracks` user.
Authenticate using the password for your normal login account.

# Clone Repositories

Clone the two Particle Tracks repositories
into the `particle-tracks` user's home directory.
Because you'll issue several commands as `particle-tracks`,
it will be easiest to `sudo` to a login shell.
You should find yourself in the home directory
of the `particle-tracks` account (e.g., `/home/particle-tracks`).

Clone the client:
```
git clone https://github.com/knkiers/particle-tracks.git
```
and the server:
```
git clone https://github.com/knkiers/particle-tracks-server.git
```

# Create Virtual Environment

The server runs under a Python virtual environment.
Use a `particle-tracks` login shell.
Run:
```
lsvirtualenv
```
to check whether there is already a virtual envionment set up.
If not, create one with:
```
mkvirtualenv particle-tracks
```
If so, make sure you are using the `particle-tracks` environment;
run:
```
workon particle-tracks
```
You can also check which virtual environment is current
by running just
```
workon
```

# Install Python Modules

Change directory to the `particle-tracks-server` directory,
where the `requirements.txt` file is located.
This file contains details of the Python modules
needed by the Particle Tracks server.
Install the required modules:
```
pip install -r requirements.txt
```

