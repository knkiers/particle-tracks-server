#!/usr/bin/env bash

ansible-playbook \
  --ask-become-pass \
  --limit production \
  provision.yaml
