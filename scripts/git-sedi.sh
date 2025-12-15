#!/bin/bash

git grep -l -z "$1" | tr '\n' '\000' | xargs -0 -r -0 sed -i -e "s^$1^$2^g"
