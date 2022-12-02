from lib.pycubed import cubesat
from print_utils import bold, normal

# initialize dictionary for nvm counters, list for values and key/value tuples
nvm_counters = {"c_boot": cubesat.c_boot,
                "c_state_err": cubesat.c_state_err,
                "c_vbus_rst": cubesat.c_vbus_rst,
                "c_deploy": cubesat.c_deploy,
                "c_downlink": cubesat.c_downlink,
                "c_logfail": cubesat.c_logfail,
                }
# items and values will be initialized with the same order by default
nvm_counters_items = list(nvm_counters.items())
nvm_counters_values = list(nvm_counters.values())

# initialize dictionary for nvm flags, list for values and key/value tuples
nvm_flags = {"f_contact": cubesat.f_contact,
             "f_burn":  cubesat.f_burn,
             }
# items and values will be initialized with the same order by default
nvm_flags_items = list(nvm_flags.items())
nvm_flags_values = list(nvm_flags.values())


def verify_counter_bits(counterstr, counter):
    """ verify that the counter is within a certain range of values """
    # if the counter doesn't exist, return None
    if counter is None:
        return None
    # if the counter exists, check that its values are between 0 and maxval - 1
    else:
        return 0 <= counter <= cubesat.max_vals[counterstr]


def verify_flag_bits(flagstr, flag):
    """ verify that the flag is set to either 0 or 1 """
    # if the flag doesn't exist, return None
    if flag is None:
        return None
    # if the flag exists, check that its value is either 0 or 1
    else:
        return 0 <= flag <= 1


def check_nvm_counter_overflow():
    """ check that updating any particular nvm counter doesn't affect
    other parts of non volatile memory """
    original_values = nvm_counters_items.copy()
    remaining_valid = True

    # set each counter in nvm to their maximum values
    for i in range(len(nvm_counters_items)):
        (counterstr, counter) = nvm_counters_items[i]
        nvm_counters[counterstr] = cubesat.max_vals[counterstr]

    # change each multibit counter to 0, make sure no other counter changed
    for i in range(len(nvm_counters_items)):
        # set some counter i to 0
        (counterstr, counter) = nvm_counters_items[i]
        nvm_counters[counterstr] = 0
        # check that the remaining counter vals are the same
        remaining_valid = (nvm_counters_items[:i] == original_values[:i] and
                           nvm_counters_items[i + 1:] == original_values[i + 1:])
        # set counter i back to max
        nvm_counters[counterstr] = cubesat.max_vals[counterstr]

    if not remaining_valid:
        return remaining_valid, "Counter", counterstr, "interferes with others."
    else:
        return remaining_valid, "No interference in NVM between counters."


async def run(result_dict):
    """
    Test to make sure all nvm counters and flags exist, and that their values are in range.
    Also check that multibit flags do not interfere with each other or reference the same
    region in non volatile memory.
    """

    print("Starting NVM Test...")
    nvm_counters_exist = [(counter is not None) for counter in nvm_counters_values]
    nvm_flags_exist = [(flag is not None) for flag in nvm_flags_values]

    counter_flag_access = not (False in nvm_counters_exist) and not (False in nvm_flags_exist)
    counter_flag_access_string = ""
    if counter_flag_access:
        counter_flag_access_string = "All counters and flags are accessible."
    else:
        counter_flag_access_string = "The following counters / flags are None:"
    print(nvm_counters_items, nvm_flags_items)

    nvm_counters_inrange = [verify_counter_bits(counterstr, counter) for counterstr, counter in nvm_counters_items]
    nvm_flags_inrange = [verify_flag_bits(flagstr, flag) for flagstr, flag in nvm_flags_items]

    counter_flag_inrange = (not (False in nvm_counters_inrange)) and (not (False in nvm_flags_inrange))
    counter_flag_inrange_string = ""
    if counter_flag_inrange:
        counter_flag_inrange_string = "All existing counters and flags are in range."
    else:
        counter_flag_inrange_string = "The following counters / flags are not in range:"

    for i in range(len(nvm_counters_values)):
        # if all counters are accessible, we'll never reach this
        # we only add to counter_flag_access_string if something is inaccessible
        if not nvm_counters_exist[i]:
            counter_flag_access_string += nvm_counters_items[i][0] + "; "
        # if the counter exists, verify its values
        else:
            # if all counters are in range, we'll never reach this
            # we only add to counter_flag_inrange_string if something is out of range
            if not nvm_counters_inrange[i]:
                counter_flag_inrange_string += nvm_counters_items[i][0] + "; "

    for i in range(len(nvm_flags_values)):
        # if all flags are accessible, we'll never reach this
        # we only add to counter_flag_access_string if something is inaccessible
        if not nvm_flags_exist[i]:
            counter_flag_access_string += nvm_flags_items[i][0] + "; "
        # if the flag exists, verify its values
        else:
            # if all flags are in range, we'll never reach this
            # we only add to counter_flag_inrange_string if something is out of range
            if not nvm_flags_inrange[i]:
                print(nvm_flags_inrange[i])
                counter_flag_inrange_string += nvm_flags_items[i][0] + "; "

    result_dict["NVM_CounterFlagAccess"] = (counter_flag_access_string, counter_flag_access)
    result_dict["NVM_CounterFlagValuesInRange"] = (counter_flag_inrange_string, counter_flag_inrange)
    counter_overflow, counter_overflow_string = check_nvm_counter_overflow()
    result_dict["NVM_CounterInterference"] = (counter_overflow_string, counter_overflow)

    nvm_reset = input(f"\n\nWould you like to reset non-volatile memory? Select {bold}(y){normal} for yes," +
                      f" or {bold}(n){normal} for no:\n~> ")
    if nvm_reset.lower() == 'y':
        cubesat.reset_nvm()

    print("NVM Test Complete.\n")

    return result_dict
