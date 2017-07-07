import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

def boxed_entry(label, value):
    box = Gtk.Box()
    box.pack_start(Gtk.Label(label), True, True, 0)

    adjustment = Gtk.Adjustment(value, 0.0, 100.0, 0.1, 0.5, 0.0)
    spinbutton = Gtk.SpinButton()
    spinbutton.set_adjustment(adjustment)
    spinbutton.set_value(value)
    spinbutton.set_digits(1)
    spinbutton.set_numeric(True)
    box.pack_start(spinbutton, True, True, 0)

    return box

class ROVPanel(Gtk.Window):
    """ Gtk window for setting parameters in the ROV's high level controls.
    """
    def __init__(self):
        Gtk.Window.__init__(self, title="ROV controls station")
        self.set_border_width(10)

        self.controls_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)

        # Create PID box
        pid_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.controls_box.pack_start(pid_box, True, True, 0)
        pid_box.set_homogeneous(False)

        pid_box.pack_start(Gtk.Label("PID"), True, True, 5)
        pid_box.pack_start(boxed_entry("P: ", 2.0), True, True, 3)
        pid_box.pack_start(boxed_entry("I: ", 0.5), True, True, 3)
        pid_box.pack_start(boxed_entry("D: ", 1.0), True, True, 3)

        # Create LQR box
        lqr_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.controls_box.pack_start(lqr_box, True, True, 0)
        lqr_box.set_homogeneous(False)

        lqr_box.pack_start(Gtk.Label("LQR"), True, True, 5)
        lqr_box.pack_start(boxed_entry("Q: ", 1.0), True, True, 3)
        lqr_box.pack_start(boxed_entry("R: ", 1.0), True, True, 3)

        # Create Control choices
        button_box = Gtk.Box()
        button = Gtk.Button.new_with_label("PID")
        button.connect("clicked", self.on_pid_clicked)
        button_box.pack_start(button, True, True, 3)

        button = Gtk.Button.new_with_label("LQR")
        button.connect("clicked", self.on_lqr_clicked)
        button_box.pack_start(button, True, True, 3)

        self.controls_box.pack_start(button_box, True, True, 3)

        self.add(self.controls_box)

    def on_pid_clicked(self, button):
        print("PID clicked.")

    def on_lqr_clicked(self, button):
        print("LQR clicked.")


win = ROVPanel()
win.connect("delete-event", Gtk.main_quit)
win.show_all()
Gtk.main()
