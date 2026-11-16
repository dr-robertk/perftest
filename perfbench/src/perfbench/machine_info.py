import platform
import sys

import cpuinfo


def load_machine_info() -> dict[str, object]:
    """Return machine metadata in pytest-benchmark's machine_info format."""
    implementation = platform.python_implementation()
    implementation_version = platform.python_version()
    if implementation == "PyPy":
        implementation_version = ".".join(str(part) for part in sys.pypy_version_info[:3])
        if sys.pypy_version_info.releaselevel != "final":
            implementation_version += f"-{sys.pypy_version_info.releaselevel}{sys.pypy_version_info.serial}"

    cpu_info = cpuinfo.get_cpu_info() or {}
    machine_info: dict[str, object] = {
        "node": platform.node(),
        "processor": platform.processor(),
        "machine": platform.machine(),
        "python_compiler": platform.python_compiler(),
        "python_implementation": implementation,
        "python_implementation_version": implementation_version,
        "python_version": platform.python_version(),
        "python_build": platform.python_build(),
        "release": platform.release(),
        "system": platform.system(),
        "cpuinfo_version_string": cpu_info.get("cpuinfo_version_string"),
        "cpu_arch": cpu_info.get("arch"),
        "cpu_bits": cpu_info.get("bits"),
        "cpu_count": cpu_info.get("count"),
        "cpu_arch_string_raw": cpu_info.get("arch_string_raw"),
        "cpu_vendor_id_raw": cpu_info.get("vendor_id_raw"),
        "cpu_brand_raw": cpu_info.get("brand_raw"),
        "cpu_hz_advertised_friendly": cpu_info.get("hz_advertised_friendly"),
        "cpu_hz_actual_friendly": cpu_info.get("hz_actual_friendly"),
        "cpu_hz_advertised": (cpu_info.get("hz_advertised") or (None, None))[0],
        "cpu_hz_actual": (cpu_info.get("hz_actual") or (None, None))[0],
        "cpu_stepping": cpu_info.get("stepping"),
        "cpu_model": cpu_info.get("model"),
        "cpu_family": cpu_info.get("family"),
        "cpu_flags": cpu_info.get("flags"),
        "cpu_l3_cache_size": cpu_info.get("l3_cache_size"),
        "cpu_l2_cache_size": cpu_info.get("l2_cache_size"),
        "cpu_l1_data_cache_size": cpu_info.get("l1_data_cache_size"),
        "cpu_l1_instruction_cache_size": cpu_info.get("l1_instruction_cache_size"),
        "cpu_l2_cache_line_size": cpu_info.get("l2_cache_line_size"),
        "cpu_l2_cache_associativity": cpu_info.get("l2_cache_associativity"),
    }
    return machine_info
