HARDWARE_VERSION = "B2/01"  # new flight boards (Dec 2022)
# HARDWARE_VERSION = "B1/02" # Oct 2022
# HARDWARE_VERSION = "B1/01" # Aug 2022

config = dict()

if HARDWARE_VERSION == "B2/01":

    config["sun_xn_i2c"] = "i2c3"
    config["sun_xn_address"] = 0x29

    config["sun_yn_i2c"] = "i2c1"
    config["sun_yn_address"] = 0x29

    config["sun_zn_i2c"] = "i2c2"
    config["sun_zn_address"] = 0x29

    config["sun_xp_i2c"] = "i2c3"
    config["sun_xp_address"] = 0x49

    config["sun_yp_i2c"] = "i2c1"
    config["sun_yp_address"] = 0x49

    config["sun_zp_i2c"] = "i2c2"
    config["sun_zp_address"] = 0x49

    config["coil_x_i2c"] = "i2c1"
    config["coil_x_address"] = 0x60

    config["coil_y_i2c"] = "i2c1"
    config["coil_y_address"] = 0x62

    config["coil_z_i2c"] = "i2c1"
    config["coil_z_address"] = 0x68

    config["rtc_i2c"] = "i2c2"

    config["imu_i2c"] = "i2c1"
    config["imu_address"] = 0x69

elif HARDWARE_VERSION == "B1/02":
    raise NotImplementedError(f"No configuration for {HARDWARE_VERSION}")
elif HARDWARE_VERSION == "B1/01":
    raise NotImplementedError(f"No configuration for {HARDWARE_VERSION}")
else:
    raise ValueError(f"Invalid hardware version {HARDWARE_VERSION}")
