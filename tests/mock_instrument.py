"""Compare the SCPI command sequence before and after the refactor."""
import sys, types, importlib.util

TRACE = []

class MockVNA:
    def write(self, cmd): TRACE.append(("write", cmd))
    def query(self, cmd):
        TRACE.append(("query", cmd))
        if "DATA:FDaTa?" in cmd:
            return "1.0,2.0\n"
        return "MAN"
    def read(self): return "ok"

def install_stubs():
    # numpy
    np = types.ModuleType("numpy")
    np.linspace = lambda start, stop, count: [start, stop][:count]
    np.asarray = lambda values: values
    np.array = lambda values: values
    np.zeros = lambda shape: None
    sys.modules["numpy"] = np
    # pyvisa
    pv = types.ModuleType("pyvisa")
    class RM:
        def __init__(self, *a, **k): TRACE.append(("ResourceManager", a[0] if a and a[0] else None))
        def list_resources(self): return ("TCPIP0::mock::INSTR",)
        def open_resource(self, addr): TRACE.append(("open", addr)); return MockVNA()
    pv.ResourceManager = RM
    sys.modules["pyvisa"] = pv
    # matplotlib / skrf / numpy passthrough where possible
    mpl = types.ModuleType("matplotlib"); plt = types.ModuleType("matplotlib.pyplot")
    for fn in ("figure","plot","savefig","close","show","title","xlabel","ylabel","legend","grid","subplots"):
        setattr(plt, fn, lambda *a, **k: None)
    plt.subplots = lambda *a, **k: (types.SimpleNamespace(savefig=lambda *a,**k: None),
                                    types.SimpleNamespace(plot=lambda *a,**k: None))
    mpl.pyplot = plt; sys.modules["matplotlib"] = mpl; sys.modules["matplotlib.pyplot"] = plt
    skrf = types.ModuleType("skrf")
    class Net:
        def __init__(self,*a,**k): pass
        def write_touchstone(self,*a,**k): TRACE.append(("touchstone", k.get("filename")))
        def plot_s_db(self,*a,**k): pass
        def plot_s_smith(self,*a,**k): pass
    skrf.Network = Net
    sys.modules["skrf"] = skrf

def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    sys.modules[name] = m
    spec.loader.exec_module(m)
    return m

def run(mod, is_new):
    """Exercise the shared helpers with fixed inputs."""
    TRACE.clear()
    target = mod
    if is_new:
        import vna_control
        target = vna_control
    target.VNA = MockVNA()
    target.PLOT_DIR = "/tmp/plots"
    target.set_freq_lims(1e6, 2e9)
    target.check_power_mode()
    target.set_power_mode("MAN", -12)
    target.set_power_mode("HIGH")
    return list(TRACE)
