#!/bin/bash

CONF="/etc/fan/fan.conf"
PWM_FILE="/etc/fan/fan_pwm.txt"
RPM_FILE="/etc/fan/fan_rpm.txt"

INTERVAL=5   # secondes

get_cpu_temp() {
    awk '{print int($1/1000)}' /sys/class/thermal/thermal_zone0/temp
}

get_pwm_for_temp() {
    local temp=$1
    local mode rules pwm=0

    mode=$(grep '^debug=' "$CONF" | cut -d= -f2)

    if [ "$mode" = "true" ]; then
        rules=$(awk '/debug:/{f=1;next}/^[a-z]+:/{f=0}f' "$CONF")
    else
        rules=$(awk '/main:/{f=1;next}/^[a-z]+:/{f=0}f' "$CONF")
    fi

    while IFS='=' read -r t v; do
        if [ "$temp" -ge "$t" ]; then
            pwm=$v
        fi
    done <<< "$rules"

    echo "$pwm"
}

while true; do
    temp=$(get_cpu_temp)
    pwm=$(get_pwm_for_temp "$temp")

    fan_pwm "$pwm" >/dev/null
    rpm=$(fan_pwm read)

    echo "$pwm" > "$PWM_FILE"
    echo "$rpm" > "$RPM_FILE"

    sleep "$INTERVAL"
done
