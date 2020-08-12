= Particle Tracks Configuration

Notes on configuring particle-tracks for production use.

== Outbound Email

Because our server is behind the campus firewall, in order to send
email beyond campus (e.g., for password resets), we configure the
Postfix `relayhost` to point to our SMTP server. The relevant line
in /etc/postfix/main.cf is:

    relayhost = smtp.cse.taylor.edu

