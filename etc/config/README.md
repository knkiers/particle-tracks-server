= Particle Tracks Configuration

Notes on configuring particle-tracks for production use.

== Outbound Email

Because our server was behind the campus firewall, in order to send email
beyond campus (e.g., for password resets), we needed to configure the
`relayhost` for the postfix mail server to point to our SMTP server. The
relevant line is:

    relayhost = smtp.cse.taylor.edu
