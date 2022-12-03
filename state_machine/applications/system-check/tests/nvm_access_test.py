from lib.pycubed import _Satellite, cubesat
from print_utils import bold, normal


nvm_flags = ["f_contact",
             "f_burn",
             ]

nvm_counters = ["c_boot",
                "c_state_err",
                "c_vbus_rst",
                "c_deploy",
                "c_downlink",
                "c_logfail",
                ]

def verify_value(field_str, value):
    setattr(cubesat, field_str, value)
    if not getattr(cubesat, field_str) == value:
        return False
    return True

def verify_counter(counter_str):
    """ verify that the counter values can be changed and stay in range """

    # save current counter value
    counter_prev = getattr(cubesat, counter_str)
    maxval = vars(_Satellite)[counter_str].maxval

    success = True
    success &= verify_value(counter_str, 0)
    success &= verify_value(counter_str, maxval)
    success &= not verify_value(counter_str, maxval + 1)

    # restore counter value
    setattr(cubesat, counter_str, counter_prev)

    return success

def verify_flag(flag_str):
    """ verify that the flag can be set to either 0 or 1 """

    # save current flag value
    flag_prev = getattr(cubesat, flag_str)

    success = True
    success &= verify_value(flag_str, 0)
    success &= verify_value(flag_str, 1)

    # restore flag value
    setattr(cubesat, flag_str, flag_prev)

    return success

def test_counter_interference(result_dict):
    """ check that updating any particular nvm counter doesn't affect
    other parts of non volatile memory """

    # save original values of the counters
    original_values = [getattr(cubesat, counter_str) for counter_str in nvm_counters]

    # set each counter in nvm to their maximum values
    for counter_str in nvm_counters:
        maxval = vars(_Satellite)[counter_str].maxval
        setattr(cubesat, counter_str, maxval)

    # change each counter to 0, make sure no other counter changed
    success = True
    interfering_counters = []
    for counter_str in nvm_counters:
        setattr(cubesat, counter_str, 0)

        # check that the remaining counter vals are the same
        for remaining_counter_str in nvm_counters:
            if remaining_counter_str == counter_str:
                continue

            maxval = vars(_Satellite)[remaining_counter_str].maxval
            val = getattr(cubesat, remaining_counter_str)
            if not val == maxval:
                success = False
                interfering_counters.append(f"{counter_str} interfers with {remaining_counter_str}")

        # set counter back to max
        maxval = vars(_Satellite)[counter_str].maxval
        setattr(cubesat, counter_str, maxval)

    if success:
        result_str = "No counter interference found"
    else:
        result_str = f"Inteferences: {interfering_counters}"

    result_dict["NVM_Counter_Interference"] = (result_str, success)

def prompt_to_zero_counters_and_flags():
    nvm_reset = input(f"\n\nWould you like to zero the counters and flags? Select {bold}(y){normal} for yes," +
                      f" or {bold}(n){normal} for no:\n~> ")
    if nvm_reset.lower() == 'y':
        cubesat.zero_counters()
        cubesat.zero_flags()

def test_counters(result_dict):

    for counter_str in nvm_counters:
        counter_success = verify_counter(counter_str)
        result_dict[f"NVM_Counter_{counter_str}"] = (f"value = {getattr(cubesat, counter_str)}", counter_success)

def test_flags(result_dict):

    for flag_str in nvm_flags:
        flag_success = verify_flag(flag_str)
        result_dict[f"NVM_Flag_{flag_str}"] = (f"value = {getattr(cubesat, flag_str)}", flag_success)

async def run(result_dict):
    """
    Test to make sure all nvm counters and flags exist, and that their values are in range.
    Also check that multibit flags do not interfere with each other or reference the same
    region in non volatile memory.
    """

    print("Starting NVM Test...")
    test_counters(result_dict)
    test_counter_interference(result_dict)
    test_flags(result_dict)
    prompt_to_zero_counters_and_flags()
    print("NVM Test Complete.\n")

    return result_dict
