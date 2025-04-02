from flask import Flask, request, render_template

app = Flask(__name__)

# Predefined electrical devices (you can expand this list)
available_devices = {
    "Laptop": None,  # Power in Watts
    "Desktop Computer": None,
    "Television (LCD)": None,
    "Refrigerator": None,
    "Microwave Oven": None,
    "Light Bulb (LED)": None,
}

@app.route('/', methods=['GET', 'POST'])
def power_calculator():
    total_power = 0
    device_entries = []  # List to store device information entered by the user
    error = None

    if request.method == 'POST':
        # Handle predefined devices with user-entered power
        for device_name in available_devices:
            power_input = request.form.get(f'power_{device_name}')
            if power_input:
                try:
                    power = float(power_input)
                    if power >= 0:
                        device_entries.append({'name': device_name, 'power': power})
                        total_power += power
                    else:
                        error = "Power consumption cannot be negative."
                        break
                except ValueError:
                    error = f"Invalid power value for {device_name}. Please enter a number."
                    break

        if not error:  # Only process manual entries if no errors in predefined devices
            # Handle manually entered devices
            manual_device_names = request.form.getlist('manual_device_name')
            manual_device_powers = request.form.getlist('manual_device_power')

            for i in range(len(manual_device_names)):
                device_name = manual_device_names[i].strip()
                power_str = manual_device_powers[i].strip()

                if device_name and power_str:
                    try:
                        power = float(power_str)
                        if power >= 0:
                            device_entries.append({'name': device_name, 'power': power})
                            total_power += power
                        else:
                            error = "Power consumption cannot be negative."
                            break
                    except ValueError:
                        error = "Invalid power value entered for a manual device. Please enter a number."
                        break

    return render_template('power_calculator.html',
                           available_devices=available_devices,
                           device_entries=device_entries,
                           total_power=total_power,
                           error=error)

@app.route('/energy', methods=['GET', 'POST'])
def energy_calculator():
    total_energy = 0  # Energy in Watt-hours
    device_entries = []  # List to store device information entered by the user
    error = None

    if request.method == 'POST':
        energy_calculation_mode = request.form.get('energy_mode')

        if energy_calculation_mode == 'individual':
            # Calculate energy from individual device power and time
            device_names = request.form.getlist('device_name')
            device_powers = request.form.getlist('device_power')
            device_times = request.form.getlist('device_time')

            for i in range(len(device_names)):
                device_name = device_names[i].strip()
                power_str = device_powers[i].strip()
                time_str = device_times[i].strip()

                if device_name and power_str and time_str:
                    try:
                        power = float(power_str)
                        time = float(time_str)
                        if power >= 0 and time >= 0:
                            energy = power * time
                            device_entries.append({'name': device_name, 'power': power, 'time': time, 'energy': energy})
                            total_energy += energy
                        else:
                            error = "Power consumption and usage time cannot be negative."
                            break
                    except ValueError:
                        error = "Invalid input for a device. Please enter numbers for power and time."
                        break
        elif energy_calculation_mode == 'total':
            # Calculate energy from total power and total time
            total_power_input = request.form.get('total_power')
            total_time_input = request.form.get('total_time')

            if total_power_input and total_time_input:
                try:
                    total_power_val = float(total_power_input)
                    total_time_val = float(total_time_input)
                    if total_power_val >= 0 and total_time_val >= 0:
                        total_energy = total_power_val * total_time_val
                    else:
                        error = "Total power and total time cannot be negative."
                except ValueError:
                    error = "Invalid input for total power or total time. Please enter numbers."
        else:
            error = "Please select a method for calculating energy."

    return render_template('energy_calculator.html',
                           device_entries=device_entries,
                           total_energy=total_energy,
                           error=error)

@app.route('/cost', methods=['GET', 'POST'])
def cost_calculator():
    total_cost = 0
    error = None

    if request.method == 'POST':
        energy_calculation_mode = request.form.get('energy_mode')
        unit_cost_input = request.form.get('unit_cost')

        if not unit_cost_input:
            error = "Please enter the unit cost of energy."
        else:
            try:
                unit_cost = float(unit_cost_input)
                if unit_cost < 0:
                    error = "Unit cost cannot be negative."
                else:
                    if energy_calculation_mode == 'individual':
                        # Calculate energy from individual device power and time
                        device_powers = request.form.getlist('device_power')
                        device_times = request.form.getlist('device_time')

                        total_energy = 0
                        has_valid_energy_data = False
                        for i in range(len(device_powers)):
                            power_str = device_powers[i].strip()
                            time_str = device_times[i].strip()

                            if power_str and time_str:
                                try:
                                    power = float(power_str)
                                    time = float(time_str)
                                    if power >= 0 and time >= 0:
                                        total_energy += power * time
                                        has_valid_energy_data = True
                                    elif error is None:
                                        error = "Power consumption and usage time cannot be negative."
                                except ValueError:
                                    if error is None:
                                        error = "Invalid input for a device. Please enter numbers for power and time."
                        if has_valid_energy_data:
                            total_cost = (total_energy / 1000) * unit_cost # Convert Watt-hours to kWh
                    elif energy_calculation_mode == 'total':
                        # Calculate energy from total power and total time
                        total_power_input = request.form.get('total_power')
                        total_time_input = request.form.get('total_time')

                        if total_power_input and total_time_input:
                            try:
                                total_power_val = float(total_power_input)
                                total_time_val = float(total_time_input)
                                if total_power_val >= 0 and total_time_val >= 0:
                                    total_energy = total_power_val * total_time_val
                                    total_cost = (total_energy / 1000) * unit_cost # Convert Watt-hours to kWh
                                else:
                                    error = "Total power and total time cannot be negative."
                            except ValueError:
                                error = "Invalid input for total power or total time. Please enter numbers."
                    else:
                        error = "Please select a method for calculating energy."
            except ValueError:
                error = "Invalid unit cost. Please enter a number."

    return render_template('cost_calculator.html',
                           total_cost=total_cost,
                           error=error)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')