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
> particle-tracks:!!:17514:0:99999:7:::
The `!!` indicates that this user cannot log in normally.

# Sudo



<!--  LocalWords:  CentOS
 -->
