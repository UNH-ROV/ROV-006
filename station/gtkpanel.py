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

    return box, spinbutton

class ROVPanel(Gtk.Window):
    """ Gtk window for setting parameters in the ROV's high level controls.
    """
    def __init__(self, socket):
        Gtk.Window.__init__(self, title="ROV station")
        self.set_border_width(10)
        self.socket = socket

        self.controls_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)

        # Create PID box
        pid_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.controls_box.pack_start(pid_box, True, True, 0)
        pid_box.set_homogeneous(False)

        self.pid = {}
        pid_box.pack_start(Gtk.Label("PID"), True, True, 5)
        box, self.pid['p'] = boxed_entry("P: ", 2.0)
        pid_box.pack_start(box, True, True, 3)

        box, self.pid['i'] = boxed_entry("I: ", 0.5)
        pid_box.pack_start(box, True, True, 3)

        box, self.pid['d'] = boxed_entry("D: ", 1.0)
        pid_box.pack_start(box, True, True, 3)

        # Create LQR box
        lqr_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.controls_box.pack_start(lqr_box, True, True, 0)
        lqr_box.set_homogeneous(False)

        self.lqr = {}
        lqr_box.pack_start(Gtk.Label("LQR"), True, True, 5)
        box, self.lqr['q'] = boxed_entry("Q: ", 1.0)
        lqr_box.pack_start(box, True, True, 3)

        box, self.lqr['r'] = boxed_entry("R: ", 1.0)
        lqr_box.pack_start(box, True, True, 3)

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
        self.connect("delete-event", Gtk.main_quit)
        self.show_all()

    def on_pid_clicked(self, button):
        data = {
            'p': self.pid['p'].get_value(),
            'i': self.pid['i'].get_value(),
            'd': self.pid['d'].get_value()
        }
        output = "pid" + json.dumps(data)

        self.socket.write(output.encode())
        print("P: {}, I: {}, D: {}".format(self.pid['p'].get_value(), self.pid[
            'i'].get_value(), self.pid['d'].get_value()))

    def on_lqr_clicked(self, button):
        data = {
            'q': self.lqr['q'].get_value(),
            'r': self.lqr['r'].get_value(),
        }
        output = "lqr" + json.dumps(data)

        self.socket.write(output.encode())
        print("Q: {}, R: {}".format(self.lqr['q'].get_value(), self.lqr['r'].get_value()))

if __name__ == "__main__":
    win = ROVPanel()
    win.connect("delete-event", Gtk.main_quit)
    win.show_all()
    Gtk.main()
